"""
Tag Data Models

Contains data structures for representing tags, locations, analytes, and categories.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class LocationData:
    """
    Data structure for location information.
    
    Attributes:
        location_id: Unique identifier for the location
        dates: List of available sample dates for this location
    """
    location_id: str
    dates: List[str]


@dataclass
class AnalyteData:
    """
    Data structure for analyte information.
    
    Attributes:
        name: Name of the analyte
        category: Category the analyte belongs to
        threshold: Numeric threshold value for highlighting
    """
    name: str
    category: str
    threshold: Optional[float]


@dataclass
class CategoryData:
    """
    Data structure for analyte category information.
    
    Attributes:
        name: Name of the category
        analytes: List of AnalyteData objects in this category
    """
    name: str
    analytes: List[AnalyteData]


@dataclass
class TagRow:
    """
    Data structure for a single row in a tag.
    
    Attributes:
        analyte_name: Name of the analyte (empty for header rows)
        values: List of values for each date column
        is_highlighted: List of boolean flags indicating if each value should be highlighted
    """
    analyte_name: str
    values: List[str]
    is_highlighted: List[bool]


@dataclass
class Tag:
    """
    Data structure for a complete tag.
    
    Attributes:
        location_id: The location ID for this tag
        dates: List of selected sample dates
        header_row: The header row with location ID and dates
        analyte_rows: List of rows containing analyte data
    """
    location_id: str
    dates: List[str]
    header_row: TagRow
    analyte_rows: List[TagRow]
    
    def get_all_rows(self) -> List[TagRow]:
        """
        Get all rows in the tag including header and analyte rows.
        
        Returns:
            List of all TagRow objects in the tag
        """
        return [self.header_row] + self.analyte_rows 