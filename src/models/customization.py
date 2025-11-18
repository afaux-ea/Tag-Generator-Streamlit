"""
Customization Models

Data structures for managing customization settings for tag generation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class ExceedanceConfig:
    """
    Configuration for exceedance handling for a specific standards column.
    
    Attributes:
        enabled: Whether this standards column is enabled for exceedance checking
        text_color: Hex color string for text color when value exceeds this standard
    """
    enabled: bool = True
    text_color: str = "#000000"  # Default black


@dataclass
class AnalyteNameMapping:
    """
    Mapping between original analyte names and custom display names.
    
    Attributes:
        original_name: The original analyte name from the data source
        display_name: The custom name to display on generated tags
    """
    original_name: str
    display_name: str


@dataclass
class CustomizationSettings:
    """
    Complete customization settings for tag generation.
    
    Attributes:
        analyte_mappings: Dictionary mapping original analyte names to custom display names
        tag_format: Format style for tags (default, compact, etc.)
        custom_prefix: Custom prefix to add to tag names
        custom_suffix: Custom suffix to add to tag names
        date_format: Format for displaying dates
        date_header_text: Text to display in the first column of the date header row
        center_analyte_names: Whether to center analyte names in their cells
        header_fill_color: Hex color string for header row background fill
        exceedance_fill_color: Hex color string for exceedance cell background fill (global setting)
        exceedance_bold: Whether to bold text when value exceeds any standard (global setting)
        exceedance_configs: Dictionary mapping standards column names to ExceedanceConfig objects
        output_naming: Naming convention for output files
        show_non_detect_as_nd: Whether to display non-detect values as "ND"
        font_family: Font family name for tag text (e.g., "Arial", "Calibri", "Times New Roman")
        font_size: Font size in points for tag text
    """
    analyte_mappings: Dict[str, str] = field(default_factory=dict)
    tag_format: str = "default"
    custom_prefix: str = ""
    custom_suffix: str = ""
    date_format: str = "YYYY-MM-DD"
    date_header_text: str = "Analyte"
    center_analyte_names: bool = False
    header_fill_color: str = "#E0E0E0"
    exceedance_fill_color: str = "#CCCCCC"  # Updated default to match current implementation
    exceedance_bold: bool = True
    exceedance_configs: Dict[str, ExceedanceConfig] = field(default_factory=dict)
    output_naming: str = "default"
    show_non_detect_as_nd: bool = False
    font_family: str = "Arial"
    font_size: int = 10
    
    def get_analyte_display_name(self, original_name: str) -> str:
        """
        Get the display name for an analyte.
        
        Args:
            original_name: The original analyte name
            
        Returns:
            The custom display name if set, otherwise the original name
        """
        return self.analyte_mappings.get(original_name, original_name)
    
    def set_analyte_display_name(self, original_name: str, display_name: str):
        """
        Set a custom display name for an analyte.
        
        Args:
            original_name: The original analyte name
            display_name: The custom display name
        """
        if display_name.strip():
            self.analyte_mappings[original_name] = display_name.strip()
        else:
            # Remove mapping if display name is empty
            self.analyte_mappings.pop(original_name, None)
    
    def clear_analyte_mappings(self):
        """Clear all analyte name mappings."""
        self.analyte_mappings.clear()
    
    def get_mapped_analytes(self) -> Dict[str, str]:
        """
        Get all analyte mappings.
        
        Returns:
            Dictionary of original names to display names
        """
        return self.analyte_mappings.copy()
    
    def get_exceedance_config(self, standards_col_name: str) -> ExceedanceConfig:
        """
        Get the exceedance configuration for a specific standards column.
        
        If no config exists for the standards column, creates and returns a default config.
        
        Args:
            standards_col_name: The name of the standards column
            
        Returns:
            ExceedanceConfig for the standards column
        """
        if standards_col_name not in self.exceedance_configs:
            # Create default config if it doesn't exist
            self.exceedance_configs[standards_col_name] = ExceedanceConfig()
        return self.exceedance_configs[standards_col_name]
    
    def set_exceedance_config(self, standards_col_name: str, config: ExceedanceConfig):
        """
        Update the exceedance configuration for a standards column.
        
        Args:
            standards_col_name: The name of the standards column
            config: The ExceedanceConfig to set
        """
        self.exceedance_configs[standards_col_name] = config
    
    def get_all_exceedance_configs(self) -> Dict[str, ExceedanceConfig]:
        """
        Get all exceedance configurations.
        
        Returns:
            Dictionary mapping standards column names to their ExceedanceConfig objects
        """
        return self.exceedance_configs.copy() 