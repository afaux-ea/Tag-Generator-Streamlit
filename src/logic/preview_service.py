"""
Preview Service Module

Handles generation of preview data for tags to be displayed in the preview panel.
Separates preview logic from actual tag generation to maintain clean architecture.
"""

from typing import List, Dict, Optional, Tuple
from ..models.tag import Tag
from .parser import ExcelParser
from .customization_service import CustomizationService


class PreviewService:
    """
    Service for generating preview data for tags.
    
    Provides methods to generate preview information for tags without
    creating full Tag objects, maintaining separation of concerns.
    """
    
    def __init__(self, parser: ExcelParser, customization_service: CustomizationService):
        """
        Initialize the preview service.
        
        Args:
            parser: ExcelParser instance containing the loaded data
            customization_service: CustomizationService for applying custom settings
        """
        self.parser = parser
        self.customization_service = customization_service
    
    def generate_preview_data(self, selected_locations: List[str], 
                            selected_analytes: List[str], 
                            selected_dates: List[str]) -> List[Dict]:
        """
        Generate preview data for tags based on selected criteria.
        
        Args:
            selected_locations: List of selected location IDs
            selected_analytes: List of selected analyte names
            selected_dates: List of selected date strings
            
        Returns:
            List of preview data dictionaries, one per location that has selected dates
        """
        preview_data = []
        
        # Group selected dates by location
        location_dates = self._group_dates_by_location(selected_locations, selected_dates)
        
        # Create preview data for each location that has selected dates
        for location_id, dates in location_dates.items():
            if dates:  # Only create preview if location has selected dates
                preview = self._create_preview_for_location(location_id, dates, selected_analytes)
                preview_data.append(preview)
        
        return preview_data
    
    def _group_dates_by_location(self, selected_locations: List[str], 
                                selected_dates: List[str]) -> Dict[str, List[str]]:
        """
        Group selected dates by location.
        
        Args:
            selected_locations: List of selected location IDs
            selected_dates: List of selected date strings
            
        Returns:
            Dictionary mapping location_id to list of dates for that location
        """
        location_dates = {}
        
        for location_id in selected_locations:
            location_dates[location_id] = []
            
            # Get all available dates for this location
            available_dates = self.parser.get_dates_by_location(location_id)
            
            # Filter to only selected dates
            for date_item in selected_dates:
                if date_item.startswith("DATE:"):
                    # Parse the date item: "DATE:location_id:date"
                    parts = date_item.split(":", 2)
                    if len(parts) >= 3 and parts[1] == location_id:
                        date = parts[2]
                        if date in available_dates:
                            location_dates[location_id].append(date)
        
        return location_dates
    
    def _create_preview_for_location(self, location_id: str, dates: List[str], 
                                   selected_analytes: List[str]) -> Dict:
        """
        Create preview data for a specific location.
        
        Args:
            location_id: The location ID for this preview
            dates: List of selected dates for this location
            selected_analytes: List of selected analyte names
            
        Returns:
            Dictionary containing preview data for the location
        """
        # Format dates according to customization settings
        formatted_dates = []
        for date in dates:
            if self.customization_service:
                formatted_date = self.customization_service.format_date(date)
            else:
                formatted_date = date
            formatted_dates.append(formatted_date)
        
        # Create preview rows
        preview_rows = []
        
        # Add location ID header row (merged across all columns)
        location_header = {
            'type': 'location_header',
            'values': [location_id] + [''] * len(formatted_dates),  # Location ID in first column, empty for others
            'is_highlighted': [False] * (len(formatted_dates) + 1),
            'merged': True  # Flag to indicate this row should be merged
        }
        preview_rows.append(location_header)
        
        # Add date header row
        date_header_text = "Analyte"  # Default
        if self.customization_service:
            date_header_text = self.customization_service.get_date_header_text()
        
        date_header = {
            'type': 'header',
            'values': [date_header_text] + formatted_dates,
            'is_highlighted': [False] * (len(formatted_dates) + 1)
        }
        preview_rows.append(date_header)
        
        # Add analyte rows
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
            
            analyte_row = {
                'type': 'analyte',
                'analyte_name': analyte_name,
                'values': analyte_values,
                'is_highlighted': analyte_highlighted
            }
            preview_rows.append(analyte_row)
        
        return {
            'location_id': location_id,
            'dates': dates,
            'formatted_dates': formatted_dates,
            'rows': preview_rows,
            'total_columns': len(formatted_dates) + 1
        }
    
    def get_preview_count(self, selected_locations: List[str], 
                         selected_analytes: List[str], 
                         selected_dates: List[str]) -> int:
        """
        Get the number of previews that would be generated.
        
        Args:
            selected_locations: List of selected location IDs
            selected_analytes: List of selected analyte names
            selected_dates: List of selected date strings
            
        Returns:
            Number of previews that would be generated
        """
        location_dates = self._group_dates_by_location(selected_locations, selected_dates)
        
        # Count locations that have at least one selected date
        count = sum(1 for dates in location_dates.values() if dates)
        
        return count 