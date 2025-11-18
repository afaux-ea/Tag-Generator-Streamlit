"""
Customization Service

Service for managing customization settings and providing a clean interface
for GUI components to interact with customization data.
"""

from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
from ..models.customization import CustomizationSettings, AnalyteNameMapping, ExceedanceConfig

if TYPE_CHECKING:
    from ..logic.parser import ExcelParser


class CustomizationService:
    """
    Service for managing customization settings.
    
    Provides methods for managing analyte name mappings and other
    customization options for tag generation.
    """
    
    def __init__(self):
        self.settings = CustomizationSettings()
    
    def get_settings(self) -> CustomizationSettings:
        """
        Get the current customization settings.
        
        Returns:
            Current customization settings
        """
        return self.settings
    
    def update_analyte_mapping(self, original_name: str, display_name: str):
        """
        Update the display name for an analyte.
        
        Args:
            original_name: The original analyte name
            display_name: The custom display name
        """
        self.settings.set_analyte_display_name(original_name, display_name)
    
    def get_analyte_display_name(self, original_name: str) -> str:
        """
        Get the display name for an analyte.
        
        Args:
            original_name: The original analyte name
            
        Returns:
            The custom display name if set, otherwise the original name
        """
        return self.settings.get_analyte_display_name(original_name)
    
    def get_analyte_mappings(self) -> Dict[str, str]:
        """
        Get all current analyte name mappings.
        
        Returns:
            Dictionary mapping original names to display names
        """
        return self.settings.get_mapped_analytes()
    
    def clear_analyte_mappings(self):
        """Clear all analyte name mappings."""
        self.settings.clear_analyte_mappings()
    
    def apply_analyte_mappings_to_list(self, analyte_names: List[str]) -> List[str]:
        """
        Apply current analyte mappings to a list of analyte names.
        
        Args:
            analyte_names: List of original analyte names
            
        Returns:
            List of display names (mapped or original)
        """
        return [self.get_analyte_display_name(name) for name in analyte_names]
    
    def update_settings(self, new_settings: CustomizationSettings):
        """
        Update all customization settings.
        
        Args:
            new_settings: New customization settings
        """
        self.settings = new_settings
    
    def reset_to_defaults(self):
        """Reset all customization settings to default values."""
        self.settings = CustomizationSettings()
    
    def set_show_non_detect_as_nd(self, enabled: bool):
        """
        Set whether non-detect values should be displayed as "ND".
        
        Args:
            enabled: True to show non-detect values as "ND", False to show original values
        """
        self.settings.show_non_detect_as_nd = enabled
    
    def get_show_non_detect_as_nd(self) -> bool:
        """
        Get whether non-detect values should be displayed as "ND".
        
        Returns:
            True if non-detect values should be shown as "ND", False otherwise
        """
        return self.settings.show_non_detect_as_nd
    
    def set_date_format(self, date_format: str):
        """
        Set the date format for displaying dates in tags.
        
        Args:
            date_format: The date format string (e.g., "YYYY-MM-DD", "MM/DD/YYYY")
        """
        self.settings.date_format = date_format
    
    def get_date_format(self) -> str:
        """
        Get the current date format setting.
        
        Returns:
            The current date format string
        """
        return self.settings.date_format
    
    def set_date_header_text(self, text: str):
        """
        Set the text to display in the first column of the date header row.
        
        Args:
            text: The text to display in the date column header
        """
        self.settings.date_header_text = text
    
    def get_date_header_text(self) -> str:
        """
        Get the current date header text setting.
        
        Returns:
            The current date header text
        """
        return self.settings.date_header_text
    
    def set_center_analyte_names(self, enabled: bool):
        """
        Set whether analyte names should be centered in their cells.
        
        Args:
            enabled: True to center analyte names, False to left-align them
        """
        self.settings.center_analyte_names = enabled
    
    def get_center_analyte_names(self) -> bool:
        """
        Get whether analyte names should be centered in their cells.
        
        Returns:
            True if analyte names should be centered, False otherwise
        """
        return self.settings.center_analyte_names
    
    def set_header_fill_color(self, color: str):
        """
        Set the header fill color for header rows.
        
        Args:
            color: The hex color string (e.g., "#E0E0E0")
        """
        self.settings.header_fill_color = color
    
    def get_header_fill_color(self) -> str:
        """
        Get the current header fill color setting.
        
        Returns:
            The current header fill color as hex string
        """
        return self.settings.header_fill_color
    
    def set_exceedance_fill_color(self, color: str):
        """
        Set the exceedance fill color for cells that exceed thresholds.
        
        Args:
            color: The hex color string (e.g., "#CCCCCC")
        """
        self.settings.exceedance_fill_color = color
    
    def get_exceedance_fill_color(self) -> str:
        """
        Get the current exceedance fill color setting.
        
        Returns:
            The current exceedance fill color as hex string
        """
        return self.settings.exceedance_fill_color
    
    def set_exceedance_bold(self, enabled: bool):
        """
        Set whether exceedance values should be bolded.
        
        Args:
            enabled: True to bold exceedance values, False otherwise
        """
        self.settings.exceedance_bold = enabled
    
    def get_exceedance_bold(self) -> bool:
        """
        Get whether exceedance values should be bolded.
        
        Returns:
            True if exceedance values should be bolded, False otherwise
        """
        return self.settings.exceedance_bold
    
    def set_standards_text_color(self, standards_col_name: str, color: str):
        """
        Set the text color for a specific standards column.
        
        Args:
            standards_col_name: The name of the standards column
            color: The hex color string (e.g., "#FF0000")
        """
        config = self.settings.get_exceedance_config(standards_col_name)
        config.text_color = color
        self.settings.set_exceedance_config(standards_col_name, config)
    
    def get_standards_text_color(self, standards_col_name: str) -> str:
        """
        Get the text color for a specific standards column.
        
        Args:
            standards_col_name: The name of the standards column
            
        Returns:
            The text color as hex string
        """
        config = self.settings.get_exceedance_config(standards_col_name)
        return config.text_color
    
    def set_standards_enabled(self, standards_col_name: str, enabled: bool):
        """
        Set whether a specific standards column is enabled for exceedance checking.
        
        Args:
            standards_col_name: The name of the standards column
            enabled: True to enable exceedance checking for this column, False to disable
        """
        config = self.settings.get_exceedance_config(standards_col_name)
        config.enabled = enabled
        self.settings.set_exceedance_config(standards_col_name, config)
    
    def get_standards_enabled(self, standards_col_name: str) -> bool:
        """
        Get whether a specific standards column is enabled for exceedance checking.
        
        Args:
            standards_col_name: The name of the standards column
            
        Returns:
            True if the standards column is enabled, False otherwise
        """
        config = self.settings.get_exceedance_config(standards_col_name)
        return config.enabled
    
    def get_all_standards_configs(self) -> Dict[str, ExceedanceConfig]:
        """
        Get all exceedance configurations for standards columns.
        
        Returns:
            Dictionary mapping standards column names to their ExceedanceConfig objects
        """
        return self.settings.get_all_exceedance_configs()
    
    def initialize_exceedance_configs(self, parser: 'ExcelParser'):
        """
        Initialize exceedance configurations for detected standards columns.
        
        This method should be called when a file is loaded to ensure all detected
        standards columns have default configurations. All standards columns are
        enabled by default.
        
        Args:
            parser: The ExcelParser instance containing detected standards columns
        """
        standards_columns = parser.get_standards_columns()
        
        # Initialize configs for all detected standards columns
        for standards_col_name in standards_columns:
            # Get or create config (get_exceedance_config creates default if not exists)
            config = self.settings.get_exceedance_config(standards_col_name)
            # Ensure it's enabled by default
            config.enabled = True
            # Default text color is black (already set in ExceedanceConfig)
            self.settings.set_exceedance_config(standards_col_name, config)
    
    def check_exceedance(self, analyte_name: str, value: float, parser: 'ExcelParser') -> Tuple[bool, Optional[str]]:
        """
        Check if a value exceeds any enabled standards for an analyte.
        
        Returns whether the value exceeds any standard and the name of the standards column
        with the highest standard value that is exceeded (for text color determination).
        
        Args:
            analyte_name: The name of the analyte
            value: The numeric value to check
            parser: The ExcelParser instance containing standards data
            
        Returns:
            Tuple of (is_exceeded: bool, highest_exceeded_standards_col: Optional[str])
            - is_exceeded: True if value exceeds any enabled standard, False otherwise
            - highest_exceeded_standards_col: Name of standards column with highest exceeded value, or None
        """
        # Get all enabled standards configs
        all_configs = self.get_all_standards_configs()
        enabled_configs = {
            col_name: config 
            for col_name, config in all_configs.items() 
            if config.enabled
        }
        
        # If no enabled standards columns, check if any standards columns exist in parser
        # and auto-enable them with default configs
        standards_columns = parser.get_standards_columns()
        if not enabled_configs and standards_columns:
            # Auto-enable all standards columns with default configs
            for col_name in standards_columns:
                config = self.settings.get_exceedance_config(col_name)
                enabled_configs[col_name] = config
        
        # Track which standards are exceeded and their values
        exceeded_standards = {}  # Maps standards_col_name -> standard_value
        
        # Check each enabled standards column
        for standards_col_name, config in enabled_configs.items():
            # Get standard value for this analyte
            standard_value = parser.get_standards_value(analyte_name, standards_col_name)
            
            # Skip if standard is None or non-numeric
            if standard_value is None:
                continue
            
            # Check if value exceeds this standard
            if value > standard_value:
                exceeded_standards[standards_col_name] = standard_value
        
        # If no standards were exceeded, return False
        if not exceeded_standards:
            return (False, None)
        
        # Find the highest standard value that was exceeded
        # (highest standard value = most restrictive standard that was exceeded)
        highest_exceeded_standard_value = max(exceeded_standards.values())
        highest_exceeded_col = None
        
        # Find the standards column name with this highest value
        # Iterate through standards_columns in order to respect the original column order
        # When multiple standards have the same highest value, select the last one in the order
        if standards_columns:
            for col_name in standards_columns:
                if col_name in exceeded_standards:
                    std_value = exceeded_standards[col_name]
                    if std_value == highest_exceeded_standard_value:
                        highest_exceeded_col = col_name
                        # Don't break - continue to find the last matching column
        
        # Fallback: if standards_columns is empty or no match found, use first exceeded standard
        # (shouldn't happen in normal operation, but provides safety)
        if highest_exceeded_col is None:
            for col_name, std_value in exceeded_standards.items():
                if std_value == highest_exceeded_standard_value:
                    highest_exceeded_col = col_name
                    break
        
        return (True, highest_exceeded_col)
    
    def set_font_family(self, font_family: str):
        """
        Set the font family for tag text.
        
        Args:
            font_family: The font family name (e.g., "Arial", "Calibri", "Times New Roman")
        """
        self.settings.font_family = font_family
    
    def get_font_family(self) -> str:
        """
        Get the current font family setting.
        
        Returns:
            The current font family name
        """
        return self.settings.font_family
    
    def set_font_size(self, font_size: int):
        """
        Set the font size for tag text.
        
        Args:
            font_size: The font size in points
        """
        self.settings.font_size = font_size
    
    def get_font_size(self) -> int:
        """
        Get the current font size setting.
        
        Returns:
            The current font size in points
        """
        return self.settings.font_size
    
    def format_date(self, date_str: str) -> str:
        """
        Format a date string according to the current date format setting.
        
        Args:
            date_str: The date string to format (expected in YYYY-MM-DD format)
            
        Returns:
            The formatted date string
        """
        if not date_str or not isinstance(date_str, str):
            return date_str
        
        # Parse the input date (expected to be in YYYY-MM-DD format)
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            # If parsing fails, return the original string
            return date_str
        
        # Apply the selected format
        format_map = {
            "YYYY-MM-DD": "%Y-%m-%d",
            "MM/DD/YYYY": "%m/%d/%Y",
            "DD/MM/YYYY": "%d/%m/%Y",
            "MM-DD-YYYY": "%m-%d-%Y",
            "DD-MM-YYYY": "%d-%m-%Y",
            "MMM DD, YYYY": "%b %d, %Y",
            "MMMM DD, YYYY": "%B %d, %Y",
            "YYYY/MM/DD": "%Y/%m/%d",
            "MMMM, YYYY": "%B, %Y",
            "MMM, YYYY": "%b, %Y"
        }
        
        format_string = format_map.get(self.settings.date_format, "%Y-%m-%d")
        return date_obj.strftime(format_string)
    
    def process_non_detect_value(self, value: str) -> str:
        """
        Process a value according to non-detect settings.
        
        Args:
            value: The original value string
            
        Returns:
            The processed value string
        """
        if not self.settings.show_non_detect_as_nd:
            return value
        
        # Check if value matches non-detect pattern: starts with "<" and ends with "U"
        if isinstance(value, str) and value.strip().startswith("<") and value.strip().endswith("U"):
            return "ND"
        
        return value 