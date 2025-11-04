"""
Excel Parser Module

Handles reading and parsing of input Excel files with complex header structures.
Extracts location IDs, sample dates, analyte categories, and result values.
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional
from ..models.tag import LocationData, AnalyteData, CategoryData


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
        self.analyte_thresholds = {}  # Maps analyte_name to threshold value
        self.result_data = {}  # Maps (location_id, date, analyte) to list of result values (for duplicate handling)
    
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
            try:
                self.data = pd.read_excel(file_path, header=None)
            except Exception:
                # Try different encodings for CSV
                encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                for encoding in encodings:
                    try:
                        self.data = pd.read_csv(file_path, header=None, encoding=encoding)
                        break
                    except Exception:
                        continue
                else:
                    raise Exception("Failed to load file with any encoding")
            
            # Parse the file structure according to input_table_format.md
            self._parse_locations_and_dates()
            self._parse_categories_and_analytes()
            
            return True
            
        except Exception as e:
            print(f"Error loading file: {e}")
            return False
    
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
        
        # Get unique location IDs and their dates from rows 0 and 3
        unique_locations = set()
        location_dates_dict = {}
        
        for col_idx in range(3, len(self.data.columns)):
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
        
        # Convert to sorted lists for consistent ordering
        self.locations = sorted(list(unique_locations))
        
        # Convert sets to sorted lists for each location
        for location_id in self.locations:
            self.location_dates[location_id] = sorted(list(location_dates_dict.get(location_id, set())))
    
    def _parse_categories_and_analytes(self):
        """Parse categories and analytes starting from row 5."""
        self.categories = []
        self.analytes = []
        self.analyte_thresholds = {}
        
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
                        
                        # Get threshold from column B
                        threshold_value = self.data.iloc[row_idx, 1]
                        threshold = None
                        if pd.notna(threshold_value):
                            try:
                                threshold = float(threshold_value)
                            except (ValueError, TypeError):
                                threshold = None
                        
                        # Create AnalyteData object
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
                    
                    # Get result value
                    result_value = self.data.iloc[row_idx, col_idx]
                    if pd.notna(result_value):
                        result_str = str(result_value).strip()
                        
                        # Store result value - handle duplicates by storing in a list
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
    
    def get_result_value(self, location_id: str, date: str, analyte: str) -> Optional[str]:
        """
        Get the result value for a specific location, date, and analyte.
        
        Args:
            location_id: The location ID
            date: The sample date
            analyte: The analyte name
            
        Returns:
            The result value as a string, or None if not found
        """
        values = self.result_data.get((location_id, date, analyte))
        if values is None:
            return None
        
        # Resolve duplicates by selecting the greater value
        return self._resolve_duplicate_values(values)
    
    def get_analyte_threshold(self, analyte: str) -> Optional[float]:
        """
        Get the threshold value for a specific analyte.
        
        Args:
            analyte: The analyte name
            
        Returns:
            The threshold value as a float, or None if not found
        """
        return self.analyte_thresholds.get(analyte) 