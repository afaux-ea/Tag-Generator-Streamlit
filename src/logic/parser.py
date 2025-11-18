"""
Excel Parser Module

Handles reading and parsing of input Excel files with complex header structures.
Extracts location IDs, sample dates, analyte categories, and result values.
"""

import pandas as pd
import re
from typing import Dict, List, Tuple, Optional
from ..models.tag import LocationData, AnalyteData, CategoryData


def _get_depth_sort_key(depth: str) -> Tuple[float, str]:
    """
    Extract numeric sort key from depth interval string.
    
    Parses depth strings like "0-3", "12-15", "3-6" and returns a tuple
    that can be used for numeric sorting. The first element is the numeric
    start value, and the second is the original string for tie-breaking.
    
    Args:
        depth: Depth string (e.g., "0-3", "12-15", "3.5-6")
        
    Returns:
        Tuple of (numeric_start_value, original_string) for sorting
    """
    if not depth:
        return (float('inf'), depth)
    
    # Extract the first number from the depth string
    # Handles formats like "0-3", "12-15", "3.5-6", etc.
    match = re.match(r'^(\d+\.?\d*)', depth.strip())
    if match:
        try:
            numeric_value = float(match.group(1))
            return (numeric_value, depth)
        except ValueError:
            pass
    
    # If we can't parse it, return a high value so it sorts last
    return (float('inf'), depth)


class ExcelParser:
    """
    Parser for Excel files containing environmental sampling data.
    
    Handles the complex header structure with multiple header rows and
    wide-format data representing various sampling locations and analytes.
    """
    
    def __init__(self):
        self.data = None
        self.locations = []
        self.categories = []
        self.analytes = []
        self.location_dates = {}  # Maps location_id to list of dates
        self.analyte_thresholds = {}  # Maps analyte_name to threshold value (backward compatibility)
        self.result_data = {}  # Maps (location_id, date, analyte) to list of result values (for duplicate handling)
        self.first_location_col = None  # Column index where Location IDs start (auto-detected)
        self.has_sample_depth = False  # Flag to indicate if file contains sample depth
        self.column_metadata = {}  # Maps (location_id, date, depth) -> col_idx
        self.date_depth_combinations = {}  # Maps location_id -> list of (date, depth) tuples
        # New data structures for multi-standards column support
        self.analyte_standards = {}  # Maps analyte_name -> {standards_col_name: value}
        self.standards_columns = []  # List of standards column names in order
        self.standards_column_indices = {}  # Maps standards_col_name -> column index
    
    def load_file(self, file_path: str) -> bool:
        """
        Load and parse an Excel file.
        
        Args:
            file_path: Path to the Excel file to load
            
        Returns:
            True if file was loaded successfully, False otherwise
        """
        try:
            # Try to read as Excel first, then as CSV if that fails
            # Note: We use keep_default_na=False and specify na_values to exclude "NA"
            # This preserves "NA" as a string while still recognizing empty cells as missing
            default_na_values = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN', 
                                '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A', 
                                'NULL', 'NaN', 'n/a', 'nan', 'null']
            # Exclude "NA" from the list so it's preserved as a string
            na_values_list = [v for v in default_na_values if v != 'NA']
            
            try:
                self.data = pd.read_excel(file_path, header=None, keep_default_na=False, na_values=na_values_list)
            except Exception:
                # Try different encodings for CSV
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        self.data = pd.read_csv(file_path, header=None, encoding=encoding, 
                                               keep_default_na=False, na_values=na_values_list)
                        break
                    except Exception:
                        continue
                else:
                    raise Exception("Failed to load file with any encoding")
            
            # Parse the file structure according to input_table_format.md
            # Automatically detect where Location IDs start
            self.first_location_col = self._find_first_location_column()
            self._parse_locations_and_dates()
            self._parse_categories_and_analytes()
            
            return True
            
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
    def _find_first_location_column(self) -> int:
        """
        Automatically detect the first column containing Location IDs.
        
        Scans row 0 to find the first column that contains a Location ID.
        Skips known header/metadata columns like "AWQS".
        
        Returns:
            The column index (0-based) where Location IDs start, or 3 if not found (default)
        """
        # Known header/metadata column values to skip
        skip_values = {'AWQS', 'Analyte', 'Threshold', 'Sample Name', 'Location ID', 'Location Name',
                      'Date', 'Sample Date', 'Parent Sample Name'}
        
        # Scan row 0 from left to right, starting from column A (index 0)
        # but typically Location IDs won't be in the first 2 columns (Analyte, Threshold)
        for col_idx in range(0, len(self.data.columns)):
            cell_value = self.data.iloc[0, col_idx]
            
            if pd.notna(cell_value):
                cell_str = str(cell_value).strip()
                
                # Skip known header/metadata columns
                if cell_str.upper() in [s.upper() for s in skip_values]:
                    continue
                
                # If cell is not empty and not a known header, check if it looks like a Location ID
                # Location IDs typically:
                # - Are non-empty
                # - Contain alphanumeric characters
                # - May contain hyphens
                # - Are not just numbers or dates
                if cell_str and len(cell_str) > 0:
                    # Additional validation: check if there's a corresponding date in row 3
                    # This helps distinguish Location IDs from other header text
                    if len(self.data) > 3:
                        date_value = self.data.iloc[3, col_idx]
                        
                        # If there's a date in row 3 for this column, it's likely a Location ID column
                        if date_value is not None and pd.notna(date_value):
                            return col_idx
        
        # Default to column D (index 3) if we can't find it automatically
        return 3
    
    def _normalize_location_id_for_matching(self, location_id: str) -> str:
        """
        Normalize location ID by removing leading zeros from numeric parts.
        
        This handles cases where location IDs have leading zeros (e.g., "SB-A01")
        but sample names don't (e.g., "915239-SB-A1-6.0-9.0").
        
        Examples:
            "SB-A01" -> "SB-A1"
            "SB-B01" -> "SB-B1"
            "SB-A10" -> "SB-A10" (no change)
            "SD-02" -> "SD-2"
        
        Args:
            location_id: The location ID to normalize
            
        Returns:
            Normalized location ID with leading zeros removed from numeric parts
        """
        import re
        # Pattern to find numeric parts with leading zeros (e.g., "01", "02", "09")
        # This matches one or more digits, but we want to remove leading zeros
        def remove_leading_zeros(match):
            num_str = match.group(0)
            # Remove leading zeros, but keep at least one digit
            return str(int(num_str))
        
        # Replace sequences of digits with their integer representation (removes leading zeros)
        normalized = re.sub(r'\d+', remove_leading_zeros, location_id)
        return normalized
    
    def _extract_depth_from_sample_name(self, sample_name: str, location_id: str) -> Optional[str]:
        """
        Extract depth from sample name.
        
        Sample name format: "915239-SD-02-0-2.0" where location_id is "SD-02"
        Depth is the last segment after the location ID: "0-2.0" -> "0-2"
        
        Handles cases where location IDs have leading zeros but sample names don't.
        For example, location_id "SB-A01" will match "SB-A1" in sample name.
        
        Args:
            sample_name: The full sample name
            location_id: The location ID to find in the sample name
            
        Returns:
            The depth as a string (e.g., "0-2"), or None if not found
        """
        if not sample_name or not location_id:
            return None
        
        # Try to find the location ID in the sample name
        location_idx = sample_name.find(location_id)
        
        # If not found, try with normalized location ID (removes leading zeros)
        if location_idx == -1:
            normalized_location_id = self._normalize_location_id_for_matching(location_id)
            location_idx = sample_name.find(normalized_location_id)
            if location_idx == -1:
                return None
            # Use normalized location ID for length calculation
            matched_location_id = normalized_location_id
        else:
            matched_location_id = location_id
        
        # Get the portion after the location ID (use matched_location_id for length)
        after_location = sample_name[location_idx + len(matched_location_id):]
        
        # Remove leading/trailing hyphens and whitespace
        after_location = after_location.strip('-').strip()
        
        if not after_location:
            return None
        
        # Process depth format: remove ".0" from each part if present
        # Examples: "2.0-6.0" -> "2-6", "2.0-6" -> "2-6", "2.5-6" -> "2.5-6"
        if '-' in after_location:
            parts = after_location.split('-')
            processed_parts = []
            for part in parts:
                part = part.strip()
                # Remove ".0" only if the part ends with ".0"
                if part.endswith('.0'):
                    part = part[:-2]
                processed_parts.append(part)
            after_location = '-'.join(processed_parts)
        else:
            # Single value, remove ".0" if present
            if after_location.endswith('.0'):
                after_location = after_location[:-2]
        
        return after_location
    
    def _parse_locations(self):
        """Parse location IDs from row 0 starting at column D (index 3)."""
        self.locations = []
        self.location_dates = {}
        
        # Get unique location IDs from row 0, starting at column D (index 3)
        unique_locations = set()
        for col_idx in range(3, len(self.data.columns)):
            location_id = self.data.iloc[0, col_idx]
            if pd.notna(location_id) and str(location_id).strip():
                unique_locations.add(str(location_id).strip())
        
        # Convert to sorted list for consistent ordering
        self.locations = sorted(list(unique_locations))
        
        # Initialize location_dates dictionary for each unique location
        for location_id in self.locations:
            self.location_dates[location_id] = []
    
    def _parse_dates(self):
        """Parse sample dates from row 3 and associate with locations."""
        # Get dates from row 3, starting at column D (index 3)
        for col_idx in range(3, len(self.data.columns)):
            # Get the location ID for this column
            location_id = self.data.iloc[0, col_idx]
            if pd.notna(location_id) and str(location_id).strip():
                location_id = str(location_id).strip()
                
                # Get the date for this column
                date_value = self.data.iloc[3, col_idx]
                
                if pd.notna(date_value):
                    # Convert date to string format
                    if hasattr(date_value, 'strftime'):
                        date_str = date_value.strftime('%Y-%m-%d')
                    else:
                        date_str = str(date_value)
                    
                    # Add date to the location's date list if not already present
                    if date_str not in self.location_dates[location_id]:
                        self.location_dates[location_id].append(date_str)
        
        # Sort dates for each location
        for location_id in self.location_dates:
            self.location_dates[location_id].sort()
    
    def _parse_locations_and_dates(self):
        """Parse locations and dates in a single pass for better performance."""
        self.locations = []
        self.location_dates = {}
        self.column_metadata = {}
        self.date_depth_combinations = {}
        
        # Use the detected first location column, or default to 3 if not set
        first_location_col = self.first_location_col if self.first_location_col is not None else 3
        
        # Get unique location IDs and their dates from rows 0 and 3
        unique_locations = set()
        location_dates_dict = {}
        location_date_depth_dict = {}  # For sample depth: maps location_id -> set of (date, depth) tuples
        
        for col_idx in range(first_location_col, len(self.data.columns)):
            location_id = self.data.iloc[0, col_idx]
            if pd.notna(location_id) and str(location_id).strip():
                location_id = str(location_id).strip()
                unique_locations.add(location_id)
                
                # Get the date for this column
                date_value = self.data.iloc[3, col_idx]
                if pd.notna(date_value):
                    # Convert date to string format
                    if hasattr(date_value, 'strftime'):
                        date_str = date_value.strftime('%Y-%m-%d')
                    else:
                        date_str = str(date_value)
                    
                    # Add date to the location's date list
                    if location_id not in location_dates_dict:
                        location_dates_dict[location_id] = set()
                    location_dates_dict[location_id].add(date_str)
                    
                    # If sample depth is enabled, parse sample name and extract depth
                    depth = None
                    if self.has_sample_depth and len(self.data) > 1:
                        sample_name_value = self.data.iloc[1, col_idx]
                        if pd.notna(sample_name_value):
                            sample_name = str(sample_name_value).strip()
                            depth = self._extract_depth_from_sample_name(sample_name, location_id)
                            
                            if depth:
                                # Store column metadata
                                key = (location_id, date_str, depth)
                                self.column_metadata[key] = col_idx
                                
                                # Store date-depth combination
                                if location_id not in location_date_depth_dict:
                                    location_date_depth_dict[location_id] = set()
                                location_date_depth_dict[location_id].add((date_str, depth))
        
        # Convert to sorted lists for consistent ordering
        self.locations = sorted(list(unique_locations))
        
        # Convert sets to sorted lists for each location
        for location_id in self.locations:
            self.location_dates[location_id] = sorted(list(location_dates_dict.get(location_id, set())))
            
            # Store date-depth combinations if sample depth is enabled
            if self.has_sample_depth and location_id in location_date_depth_dict:
                # Sort by date, then by depth (numeric sorting for depth)
                combinations = sorted(
                    list(location_date_depth_dict[location_id]),
                    key=lambda x: (x[0], _get_depth_sort_key(x[1] if x[1] else ""))
                )
                self.date_depth_combinations[location_id] = combinations
    
    def _detect_standards_columns(self) -> None:
        """
        Detect all standards columns between column A (analyte names) and first location column.
        
        Standards columns are identified as columns that:
        - Are between index 1 and first_location_col - 1
        - Have a header name in row 4 (where "Analyte" appears) or row 0 (fallback)
        - Contain numeric values in analyte rows (rows 5+)
        """
        self.standards_columns = []
        self.standards_column_indices = {}
        
        # Get the first location column (default to 3 if not set)
        first_location_col = self.first_location_col if self.first_location_col is not None else 3
        
        # Find the header row (row 4 typically contains "Analyte")
        header_row_idx = 4  # Default to row 4
        if len(self.data) > 4:
            # Check if row 4 has "Analyte" in column 0
            if pd.notna(self.data.iloc[4, 0]) and "Analyte" in str(self.data.iloc[4, 0]):
                header_row_idx = 4
            # Fallback to row 0 if row 4 doesn't have "Analyte"
            elif len(self.data) > 0:
                header_row_idx = 0
        
        # Scan columns from index 1 (column B) to just before first location column
        for col_idx in range(1, first_location_col):
            # Get header name from the header row (row 4 or row 0)
            header_value = None
            if len(self.data) > header_row_idx:
                header_value = self.data.iloc[header_row_idx, col_idx]
            
            # Generate header name if empty
            if pd.notna(header_value) and str(header_value).strip():
                standards_col_name = str(header_value).strip()
            else:
                # Auto-generate name: "Standard 1", "Standard 2", etc.
                standards_col_name = f"Standard {col_idx}"
            
            # Validate that this column contains numeric values in analyte rows
            # Check a few rows starting from row 5 to see if there are numeric values
            has_numeric_values = False
            if len(self.data) > 5:
                for check_row in range(5, min(len(self.data), 20)):  # Check up to 15 rows
                    cell_value = self.data.iloc[check_row, col_idx]
                    if pd.notna(cell_value):
                        try:
                            float(cell_value)
                            has_numeric_values = True
                            break
                        except (ValueError, TypeError):
                            continue
            
            # If column has numeric values, it's a valid standards column
            if has_numeric_values:
                self.standards_columns.append(standards_col_name)
                self.standards_column_indices[standards_col_name] = col_idx
    
    def _parse_categories_and_analytes(self):
        """Parse categories and analytes starting from row 5."""
        self.categories = []
        self.analytes = []
        self.analyte_thresholds = {}
        self.analyte_standards = {}
        
        # Detect standards columns before parsing analytes
        self._detect_standards_columns()
        
        current_category = None
        row_idx = 5
        
        while row_idx < len(self.data):
            # Check if we've reached the "Notes:" row
            if pd.notna(self.data.iloc[row_idx, 0]) and str(self.data.iloc[row_idx, 0]).strip() == "Notes:":
                break
            
            # Check if this is a category row (only column A has content)
            col_a_value = self.data.iloc[row_idx, 0]
            if pd.notna(col_a_value) and str(col_a_value).strip():
                # Check if other columns in this row are empty
                other_cols_empty = True
                for col_idx in range(1, len(self.data.columns)):
                    if pd.notna(self.data.iloc[row_idx, col_idx]) and str(self.data.iloc[row_idx, col_idx]).strip():
                        other_cols_empty = False
                        break
                
                if other_cols_empty:
                    # This is a category row
                    current_category = str(col_a_value).strip()
                    category_analytes = []
                    self.categories.append(CategoryData(current_category, category_analytes))
                else:
                    # This is an analyte row
                    if current_category is not None:
                        analyte_name = str(col_a_value).strip()
                        
                        # Initialize standards dict for this analyte
                        self.analyte_standards[analyte_name] = {}
                        
                        # Read values from all detected standards columns
                        threshold = None  # For backward compatibility, use first standards column with a value
                        for standards_col_name in self.standards_columns:
                            col_idx = self.standards_column_indices[standards_col_name]
                            standards_value = self.data.iloc[row_idx, col_idx]
                            
                            # Try to convert to float
                            numeric_value = None
                            if pd.notna(standards_value):
                                try:
                                    numeric_value = float(standards_value)
                                except (ValueError, TypeError):
                                    numeric_value = None
                            
                            # Store the value (None if non-numeric or missing)
                            self.analyte_standards[analyte_name][standards_col_name] = numeric_value
                            
                            # For backward compatibility, use first standards column with a value as threshold
                            if threshold is None and numeric_value is not None:
                                threshold = numeric_value
                        
                        # Create AnalyteData object (using first standards column for backward compatibility)
                        analyte_data = AnalyteData(analyte_name, current_category, threshold)
                        self.analytes.append(analyte_data)
                        self.analyte_thresholds[analyte_name] = threshold
                        
                        # Add to current category
                        self.categories[-1].analytes.append(analyte_data)
                        
                        # Store result values for this analyte
                        self._store_analyte_results(row_idx, analyte_name)
            
            row_idx += 1
    
    def _store_analyte_results(self, row_idx: int, analyte_name: str):
        """Store result values for an analyte across all locations and dates."""
        # Use the detected first location column, or default to 3 if not set
        first_location_col = self.first_location_col if self.first_location_col is not None else 3
        
        for col_idx in range(first_location_col, len(self.data.columns)):
            # Get the location ID for this column
            location_id = self.data.iloc[0, col_idx]
            if pd.notna(location_id) and str(location_id).strip():
                location_id = str(location_id).strip()
                
                # Get the date for this column
                date_value = self.data.iloc[3, col_idx]
                
                if pd.notna(date_value):
                    # Convert date to string format
                    if hasattr(date_value, 'strftime'):
                        date_str = date_value.strftime('%Y-%m-%d')
                    else:
                        date_str = str(date_value)
                    
                    # Get depth if sample depth is enabled
                    depth = None
                    if self.has_sample_depth:
                        # Find depth for this (location_id, date, col_idx) combination
                        for (loc_id, date, dep), col in self.column_metadata.items():
                            if loc_id == location_id and date == date_str and col == col_idx:
                                depth = dep
                                break
                    
                    # Get result value
                    result_value = self.data.iloc[row_idx, col_idx]
                    if pd.notna(result_value):
                        result_str = str(result_value).strip()
                        
                        # Store result value - handle duplicates by storing in a list
                        # Include depth in key if sample depth is enabled
                        if self.has_sample_depth and depth:
                            key = (location_id, date_str, depth, analyte_name)
                        else:
                            key = (location_id, date_str, analyte_name)
                        
                        if key not in self.result_data:
                            self.result_data[key] = []
                        self.result_data[key].append(result_str)
    
    def _resolve_duplicate_values(self, values: List[str]) -> str:
        """
        Resolve duplicate values by selecting the greater numeric value.
        
        Args:
            values: List of result values to compare
            
        Returns:
            The greater value as a string, or the first value if comparison fails
        """
        if not values:
            return ""
        
        if len(values) == 1:
            return values[0]
        
        # Try to convert values to numbers for comparison
        numeric_values = []
        for value in values:
            try:
                # Extract numeric part (remove qualifiers like "J", "U", etc.)
                numeric_part = value.strip()
                # Remove common qualifiers from the end
                qualifiers = ["J", "U", "E", "N", "T", "B", "R", "L"]
                for qualifier in qualifiers:
                    if numeric_part.endswith(qualifier):
                        numeric_part = numeric_part[:-1]
                
                # Convert to float
                numeric_value = float(numeric_part)
                numeric_values.append((numeric_value, value))
            except (ValueError, TypeError):
                # If conversion fails, keep the original value for comparison
                numeric_values.append((float('-inf'), value))
        
        # Find the maximum numeric value
        max_numeric, max_value = max(numeric_values, key=lambda x: x[0])
        
        return max_value
    
    def get_locations(self) -> List[str]:
        """
        Get list of unique location IDs from the loaded file.
        
        Returns:
            List of location ID strings
        """
        return self.locations.copy()
    
    def get_categories(self) -> List[CategoryData]:
        """
        Get list of analyte categories with their associated analytes.
        
        Returns:
            List of CategoryData objects
        """
        return self.categories.copy()
    
    def get_dates_by_location(self, location_id: str) -> List[str]:
        """
        Get list of sample dates available for a specific location.
        
        Args:
            location_id: The location ID to get dates for
            
        Returns:
            List of date strings for the location
        """
        return self.location_dates.get(location_id, []).copy()
    
    def get_result_value(self, location_id: str, date: str, analyte: str, depth: Optional[str] = None) -> Optional[str]:
        """
        Get the result value for a specific location, date, and analyte.
        
        Args:
            location_id: The location ID
            date: The sample date
            analyte: The analyte name
            depth: Optional depth string (required if has_sample_depth is True)
            
        Returns:
            The result value as a string, or None if not found
        """
        # Build key based on whether sample depth is enabled
        if self.has_sample_depth and depth:
            key = (location_id, date, depth, analyte)
        else:
            key = (location_id, date, analyte)
        
        values = self.result_data.get(key)
        if values is None:
            return None
        
        # Resolve duplicates by selecting the greater value
        return self._resolve_duplicate_values(values)
    
    def get_date_depth_combinations(self, location_id: str) -> List[Tuple[str, str]]:
        """
        Get all (date, depth) combinations for a location.
        
        Args:
            location_id: The location ID to get combinations for
            
        Returns:
            List of tuples (date, depth) for this location, or empty list if sample depth is not enabled
        """
        if not self.has_sample_depth:
            return []
        
        return self.date_depth_combinations.get(location_id, [])
    
    def get_analyte_threshold(self, analyte: str) -> Optional[float]:
        """
        Get the threshold value for a specific analyte.
        
        For backward compatibility, returns the value from the first standards column.
        
        Args:
            analyte: The analyte name
            
        Returns:
            The threshold value as a float, or None if not found
        """
        return self.analyte_thresholds.get(analyte)
    
    def get_standards_columns(self) -> List[str]:
        """
        Get list of all detected standards column names.
        
        Returns:
            List of standards column names in order
        """
        return self.standards_columns.copy()
    
    def get_analyte_standards(self, analyte_name: str) -> Dict[str, Optional[float]]:
        """
        Get all standards values for a specific analyte.
        
        Args:
            analyte_name: The analyte name
            
        Returns:
            Dictionary mapping standards column names to their values (None if missing/non-numeric)
        """
        return self.analyte_standards.get(analyte_name, {}).copy()
    
    def get_standards_value(self, analyte_name: str, standards_col_name: str) -> Optional[float]:
        """
        Get a specific standards value for an analyte.
        
        Args:
            analyte_name: The analyte name
            standards_col_name: The standards column name
            
        Returns:
            The standards value as a float, or None if not found or non-numeric
        """
        analyte_standards = self.analyte_standards.get(analyte_name, {})
        return analyte_standards.get(standards_col_name) 