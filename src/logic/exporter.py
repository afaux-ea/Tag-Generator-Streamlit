"""
Excel Exporter Module

Handles writing formatted tags to Excel files with proper formatting and highlighting.
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from typing import List
from ..models.tag import Tag


class ExcelExporter:
    """
    Exporter for writing formatted tags to Excel files.
    
    Handles the creation of Excel workbooks with proper formatting,
    highlighting, and layout according to the tag structure specification.
    """
    
    def __init__(self, customization_service=None):
        """
        Initialize the Excel exporter.
        
        Args:
            customization_service: CustomizationService instance for applying custom settings
        """
        self.customization_service = customization_service
        self.workbook = None
        self.worksheet = None
        
        # Define styles
        self.black_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        
        self.white_fill = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
        self.light_grey_fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
        self.highlight_fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        
        self.bold_font = Font(bold=True)
        self.normal_font = Font(bold=False)
    
    def _get_font(self, bold: bool = False):
        """
        Get a font object based on customization settings.
        
        Args:
            bold: Whether the font should be bold
            
        Returns:
            Font object with custom settings applied
        """
        font_name = "Arial"  # Default
        font_size = 10  # Default
        
        if self.customization_service:
            font_name = self.customization_service.get_font_family()
            font_size = self.customization_service.get_font_size()
        
        return Font(name=font_name, size=font_size, bold=bold)
    
    def _get_bold_font(self):
        """
        Get a bold font object based on customization settings.
        
        Returns:
            Bold Font object with custom settings applied
        """
        return self._get_font(bold=True)
    
    def _get_normal_font(self):
        """
        Get a normal font object based on customization settings.
        
        Returns:
            Normal Font object with custom settings applied
        """
        return self._get_font(bold=False)
    
    def _get_header_fill(self):
        """
        Get the header fill color based on customization settings.
        
        Returns:
            PatternFill object for header background
        """
        if self.customization_service:
            color = self.customization_service.get_header_fill_color()
            # Remove the # prefix if present for Excel
            if color.startswith('#'):
                color = color[1:]
            return PatternFill(start_color=color, end_color=color, fill_type="solid")
        else:
            return self.light_grey_fill
    
    def _get_exceedance_fill(self):
        """
        Get the exceedance fill color based on customization settings.
        
        Returns:
            PatternFill object for exceedance background
        """
        if self.customization_service:
            color = self.customization_service.get_exceedance_fill_color()
            # Remove the # prefix if present for Excel
            if color.startswith('#'):
                color = color[1:]
            return PatternFill(start_color=color, end_color=color, fill_type="solid")
        else:
            return self.highlight_fill
    
    def export_tags(self, tags: List[Tag], output_path: str) -> bool:
        """
        Export a list of tags to an Excel file.
        
        Args:
            tags: List of Tag objects to export
            output_path: Path where the Excel file should be saved
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Create new workbook and worksheet
            self.workbook = Workbook()
            self.worksheet = self.workbook.active
            self.worksheet.title = "Tags"
            
            # Write each tag
            current_row = 1
            for i, tag in enumerate(tags):
                current_row = self._write_tag(tag, current_row)
                
                # Add spacing between tags (except after the last one)
                if i < len(tags) - 1:
                    current_row += 2
            
            # Auto-fit column widths
            self._auto_fit_columns()
            
            # Save the workbook
            self.workbook.save(output_path)
            return True
            
        except Exception as e:
            print(f"Error exporting tags: {e}")
            return False
    
    def _write_tag(self, tag: Tag, start_row: int) -> int:
        """
        Write a single tag to the worksheet.
        
        Args:
            tag: The Tag object to write
            start_row: The starting row number in the worksheet
            
        Returns:
            The next available row number after writing the tag
        """
        current_row = start_row
        all_rows = tag.get_all_rows()
        
        # Calculate the total number of columns for this tag
        # This includes: 1 column for analyte names + number of dates
        total_columns = 1 + len(tag.dates)
        
        # Write the first header row (Sample ID) as a merged cell
        if all_rows:
            first_row = all_rows[0]
            if len(first_row.values) > 1:
                # Merge across the entire width of the tag
                self.worksheet.merge_cells(
                    start_row=current_row, start_column=1,
                    end_row=current_row, end_column=total_columns
                )
                
                # Write the sample ID (location_id) in the merged cell
                sample_id_cell = self.worksheet.cell(row=current_row, column=1, value=tag.location_id)
                sample_id_cell.font = self._get_bold_font()
                sample_id_cell.fill = self._get_header_fill()
                sample_id_cell.border = self.black_border
                sample_id_cell.alignment = Alignment(horizontal='center', vertical='center')
                
                # Apply borders to the merged cell properly - ensure top border is visible
                self._apply_merged_cell_borders(current_row, 1, current_row, total_columns)
            
            current_row += 1
        
        # Write the remaining rows (starting from the second row)
        for row_idx, row in enumerate(all_rows[1:], 1):
            # Determine if this is a header row (only the date row is a header)
            # Row 1 = sample ID (merged), Row 2 = date header, Row 3+ = analyte data
            is_header_row = row_idx == 1  # Only the date row is a header
            
            # Write values to the current row
            for col_idx, value in enumerate(row.values, 1):
                cell = self.worksheet.cell(row=current_row, column=col_idx, value=value)
                
                # Apply base formatting
                cell.border = self.black_border
                
                # Apply fill color based on row type
                if is_header_row:
                    cell.fill = self._get_header_fill()
                    cell.font = self._get_bold_font()
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                else:
                    cell.fill = self.white_fill
                    cell.font = self._get_normal_font()
                    
                    # First column (analyte names) - check customization setting for alignment
                    if col_idx == 1:
                        if (self.customization_service and 
                            self.customization_service.get_center_analyte_names()):
                            # Center analyte names if setting is enabled
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                        else:
                            # Default left alignment
                            cell.alignment = Alignment(horizontal='left', vertical='center')
                    else:
                        cell.alignment = Alignment(horizontal='center', vertical='center')
                
                # Apply highlighting for analyte values (only for non-header rows)
                if not is_header_row and col_idx <= len(row.is_highlighted):
                    if row.is_highlighted[col_idx - 1]:
                        cell.font = self._get_bold_font()
                        cell.fill = self._get_exceedance_fill()
            
            current_row += 1
        
        return current_row
    
    def _apply_merged_cell_borders(self, start_row, start_col, end_row, end_col):
        """
        Apply borders to a merged cell by setting borders on the corner cells.
        
        Args:
            start_row: Starting row of the merged cell
            start_col: Starting column of the merged cell
            end_row: Ending row of the merged cell
            end_col: Ending column of the merged cell
        """
        # Apply borders to the corner cells of the merged range
        # Top-left corner
        top_left = self.worksheet.cell(row=start_row, column=start_col)
        top_left.border = Border(
            left=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000')
        )
        
        # Top-right corner
        top_right = self.worksheet.cell(row=start_row, column=end_col)
        top_right.border = Border(
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000')
        )
        
        # Bottom-left corner
        bottom_left = self.worksheet.cell(row=end_row, column=start_col)
        bottom_left.border = Border(
            left=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        
        # Bottom-right corner
        bottom_right = self.worksheet.cell(row=end_row, column=end_col)
        bottom_right.border = Border(
            right=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )
        
        # Also apply borders to the merged cell itself to ensure top border is visible
        merged_cell = self.worksheet.cell(row=start_row, column=start_col)
        merged_cell.border = self.black_border
        
        # Apply borders to all cells in the merged range to ensure complete border
        for col in range(start_col, end_col + 1):
            cell = self.worksheet.cell(row=start_row, column=col)
            cell.border = self.black_border
    
    def _auto_fit_columns(self):
        """
        Auto-fit column widths based on content.
        """
        for column in self.worksheet.columns:
            max_length = 0
            column_letter = None
            
            # Find the first cell in the column that has a column_letter attribute
            for cell in column:
                if hasattr(cell, 'column_letter'):
                    column_letter = cell.column_letter
                    break
            
            # Skip if we couldn't find a valid column letter (e.g., merged cells)
            if column_letter is None:
                continue
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            # Set a reasonable width (minimum 10, maximum 50)
            adjusted_width = min(max(max_length + 2, 10), 50)
            self.worksheet.column_dimensions[column_letter].width = adjusted_width
    
    def _apply_cell_formatting(self, cell, is_highlighted: bool):
        """
        Apply formatting to a cell based on highlighting status.
        
        Args:
            cell: The worksheet cell to format
            is_highlighted: Whether the cell should be highlighted
        """
        if is_highlighted:
            # Apply bold font and grey background for highlighted cells
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")
        # Leave unhighlighted cells with default formatting
    
    def _create_header_style(self):
        """
        Create the style for header rows.
        
        Returns:
            Font style for headers
        """
        # TODO: Implement header styling
        # - Return bold font style for header rows
        pass 