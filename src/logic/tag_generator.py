"""
Tag Generator Module

Handles the creation of tags based on selected locations, analytes, and dates.
Creates one tag per location that has selected dates, with the format specified
in the example_tags.csv file.
"""

from typing import List, Dict, Set, Optional
from ..models.tag import Tag, TagRow
from .parser import ExcelParser
from .customization_service import CustomizationService


class TagGenerator:
    """
    Generator for creating tags from selected data.
    
    Creates tags in the format specified by example_tags.csv:
    - One tag per location that has selected dates
    - Header row with Sample ID, Location ID, and date columns
    - Date row with "Date Sampled" and actual dates
    - Analyte rows with analyte names and values for each date
    """
    
    def __init__(self, parser: ExcelParser, customization_service: Optional[CustomizationService] = None):
        """
        Initialize the tag generator with a parser and optional customization service.
        
        Args:
            parser: ExcelParser instance containing the loaded data
            customization_service: Optional CustomizationService for applying custom settings
        """
        self.parser = parser
        self.customization_service = customization_service
    
    def generate_tags(self, selected_locations: List[str], 
                     selected_analytes: List[str], 
                     selected_dates: List[str]) -> List[Tag]:
        """
        Generate tags based on the selected data.
        
        Args:
            selected_locations: List of selected location IDs
            selected_analytes: List of selected analyte names
            selected_dates: List of selected date strings
            
        Returns:
            List of Tag objects, one per location that has selected dates
        """
        tags = []
        
        # Group selected dates by location
        location_dates = self._group_dates_by_location(selected_locations, selected_dates)
        
        # Create one tag per location that has selected dates
        for location_id, dates in location_dates.items():
            if dates:  # Only create tag if location has selected dates
                tag = self._create_tag_for_location(location_id, dates, selected_analytes)
                tags.append(tag)
        
        return tags
    
    def _group_dates_by_location(self, selected_locations: List[str], 
                                selected_dates: List[str]) -> Dict[str, List[str]]:
        """
        Group selected dates by their associated locations.
        
        Args:
            selected_locations: List of selected location IDs
            selected_dates: List of selected date strings in format "DATE:location_id:date"
            
        Returns:
            Dictionary mapping location IDs to lists of their selected dates
        """
        location_dates = {}
        
        # Initialize with empty lists for all selected locations
        for location_id in selected_locations:
            location_dates[location_id] = []
        
        # For each selected date, extract location and date information
        for date_item in selected_dates:
            if date_item.startswith("DATE:"):
                # Parse the date item: "DATE:location_id:date"
                parts = date_item.split(":", 2)
                if len(parts) >= 3:
                    location_id = parts[1]
                    date = parts[2]
                    
                    # Only add if this location is in our selected locations
                    if location_id in selected_locations:
                        location_dates[location_id].append(date)
        
        # Sort dates for each location
        for location_id in location_dates:
            location_dates[location_id].sort()
        
        return location_dates
    
    def _create_tag_for_location(self, location_id: str, dates: List[str], 
                                selected_analytes: List[str]) -> Tag:
        """
        Create a single tag for a specific location.
        
        Args:
            location_id: The location ID for this tag
            dates: List of selected dates for this location
            selected_analytes: List of selected analyte names
            
        Returns:
            Tag object for the location
        """
        # Create header row: Location ID in first column, empty columns for dates
        # The exporter will merge columns A and B for the sample ID
        # Total columns needed: 1 (analyte names) + len(dates) (date columns)
        total_columns = 1 + len(dates)
        header_values = [location_id] + [""] * (total_columns - 1)
        header_highlighted = [False] * len(header_values)
        header_row = TagRow("", header_values, header_highlighted)
        
        # Format dates according to customization settings
        formatted_dates = []
        for date in dates:
            if self.customization_service:
                formatted_date = self.customization_service.format_date(date)
            else:
                formatted_date = date
            formatted_dates.append(formatted_date)
        
        # Create date row with customizable header text
        date_header_text = "Analyte"  # Default
        if self.customization_service:
            date_header_text = self.customization_service.get_date_header_text()
        
        date_values = [date_header_text] + formatted_dates
        date_highlighted = [False] * len(date_values)
        date_row = TagRow("", date_values, date_highlighted)
        
        # Create analyte rows
        analyte_rows = []
        for analyte_name in selected_analytes:
            # Get custom display name if available
            display_name = analyte_name
            if self.customization_service:
                display_name = self.customization_service.get_analyte_display_name(analyte_name)
            
            # Get values for this analyte across all dates for this location
            analyte_values = [display_name]
            analyte_highlighted = [False]
            
            for date in dates:
                # Get the result value for this location, date, and analyte
                result_value = self.parser.get_result_value(location_id, date, analyte_name)
                if result_value is not None:
                    # Apply non-detect processing if customization service is available
                    if self.customization_service:
                        result_value = self.customization_service.process_non_detect_value(result_value)
                    analyte_values.append(result_value)
                    
                    # Check if value should be highlighted (exceeds threshold)
                    threshold = self.parser.get_analyte_threshold(analyte_name)
                    if threshold is not None:
                        try:
                            numeric_value = float(result_value)
                            is_highlighted = numeric_value > threshold
                        except (ValueError, TypeError):
                            is_highlighted = False
                    else:
                        is_highlighted = False
                    
                    analyte_highlighted.append(is_highlighted)
                else:
                    analyte_values.append("")
                    analyte_highlighted.append(False)
            
            analyte_row = TagRow(analyte_name, analyte_values, analyte_highlighted)
            analyte_rows.append(analyte_row)
        
        # Create the tag
        tag = Tag(
            location_id=location_id,
            dates=dates,
            header_row=header_row,
            analyte_rows=[date_row] + analyte_rows  # Include date row as first analyte row
        )
        
        return tag
    
    def get_tag_count(self, selected_locations: List[str], 
                     selected_analytes: List[str], 
                     selected_dates: List[str]) -> int:
        """
        Get the number of tags that would be generated.
        
        Args:
            selected_locations: List of selected location IDs
            selected_analytes: List of selected analyte names
            selected_dates: List of selected date strings
            
        Returns:
            Number of tags that would be generated
        """
        location_dates = self._group_dates_by_location(selected_locations, selected_dates)
        
        # Count locations that have at least one selected date
        count = sum(1 for dates in location_dates.values() if dates)
        
        return count 