"""
Preview Table Component Module

Handles rendering of preview tables with styling and highlighting.
"""

import streamlit as st


def display_preview_table(preview):
    """
    Display a preview table with styling and highlighting.
    
    Args:
        preview: Dictionary containing preview data with keys:
            - 'rows': List of row data dictionaries
            - 'total_columns': Total number of columns in the table
    """
    rows = preview['rows']
    total_columns = preview['total_columns']
    customization_service = st.session_state.customization_service
    
    # Get customization colors
    header_color = customization_service.get_header_fill_color() if customization_service else "#E0E0E0"
    exceedance_color = customization_service.get_exceedance_fill_color() if customization_service else "#999999"
    font_family = customization_service.get_font_family() if customization_service else "Arial"
    font_size = customization_service.get_font_size() if customization_service else 10
    center_analyte_names = customization_service.get_center_analyte_names() if customization_service else False
    
    # Build HTML table with all rows
    html_rows = []
    
    for row_data in rows:
        row_type = row_data.get('type', '')
        values = row_data['values']
        is_highlighted = row_data.get('is_highlighted', [False] * len(values))
        
        # Pad values to match total_columns
        padded_values = values[:total_columns] + [''] * (total_columns - len(values))
        padded_highlighting = is_highlighted[:total_columns] + [False] * (total_columns - len(is_highlighted))
        
        if row_type == 'location_header':
            # Location header row - merge across all columns
            location_id = padded_values[0] if padded_values else ""
            # Escape HTML special characters
            escaped_location_id = str(location_id).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            style_str = f"background-color: {header_color}; font-weight: bold; text-align: center; font-family: {font_family}; font-size: {font_size}pt; border: 1px solid #000; padding: 8px;"
            html_rows.append(f'<tr><td colspan="{total_columns}" style="{style_str}">{escaped_location_id}</td></tr>')
        else:
            # Regular row (header or analyte)
            cells = []
            for col_idx, value in enumerate(padded_values):
                # Determine cell styling
                cell_styles = []
                
                if row_type == 'header':
                    # Header rows - use header fill color
                    cell_styles.append(f'background-color: {header_color}')
                    cell_styles.append('font-weight: bold')
                    cell_styles.append('text-align: center')
                elif col_idx < len(padded_highlighting) and padded_highlighting[col_idx]:
                    # Exceedance cells - use exceedance fill color
                    cell_styles.append(f'background-color: {exceedance_color}')
                    cell_styles.append('font-weight: bold')
                    cell_styles.append('text-align: center')
                else:
                    # Regular cells
                    cell_styles.append('background-color: white')
                    if row_type == 'analyte' and col_idx == 0:
                        # Analyte name column
                        if center_analyte_names:
                            cell_styles.append('text-align: center')
                        else:
                            cell_styles.append('text-align: left')
                    elif row_type == 'analyte':
                        # Value columns
                        cell_styles.append('text-align: center')
                
                # Common styles for all cells
                cell_styles.append(f'font-family: {font_family}')
                cell_styles.append(f'font-size: {font_size}pt')
                cell_styles.append('border: 1px solid #000')
                cell_styles.append('padding: 6px')
                
                # Add width constraints to make columns fit content
                if col_idx == 0:
                    # First column (analyte names) - fit to content
                    cell_styles.append('white-space: nowrap')
                else:
                    # Date/value columns - fit to content with reasonable minimum
                    cell_styles.append('white-space: nowrap')
                    cell_styles.append('max-width: 120px')
                
                # Escape HTML special characters in value
                escaped_value = str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                
                cells.append(f'<td style="{"; ".join(cell_styles)}">{escaped_value}</td>')
            
            html_rows.append(f'<tr>{"".join(cells)}</tr>')
    
    # Create complete HTML table with auto width to fit content, left-aligned
    html_table = f'<div style="overflow-x: auto; width: 100%;"><table style="border-collapse: collapse; border: 1px solid #000; table-layout: auto; width: auto; margin: 0;">{"".join(html_rows)}</table></div>'
    
    # Display the HTML table
    st.markdown(html_table, unsafe_allow_html=True)

