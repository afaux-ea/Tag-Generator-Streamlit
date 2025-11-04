"""
Customization Models

Data structures for managing customization settings for tag generation.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional


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
        exceedance_fill_color: Hex color string for exceedance cell background fill
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
    exceedance_fill_color: str = "#999999"
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