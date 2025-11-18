"""
Customization Sidebar Component Module

Handles customization options in the sidebar including analyte mapping,
date format, tag format options, colors, and fonts.
"""

import streamlit as st
from src.logic.preview_service import PreviewService


def render_analyte_mapping_section():
    """Render the Analyte Name Mapping section."""
    with st.expander("📝 Analyte Name Mapping", expanded=False):
        customization_service = st.session_state.customization_service
        selected_analytes = st.session_state.selected_analytes
        
        if selected_analytes:
            st.write("Customize display names for selected analytes:")
            st.caption("Leave blank to use original name")
            
            # Sort analytes for consistent display
            sorted_analytes = sorted(selected_analytes)
            
            # Create input fields for each selected analyte
            for analyte_name in sorted_analytes:
                # Get current display name (or original if not set)
                current_display_name = customization_service.get_analyte_display_name(analyte_name)
                # If display name is same as original, show empty (user hasn't customized yet)
                if current_display_name == analyte_name:
                    current_display_name = ""
                
                # Create input field
                display_name_key = f"analyte_display_{analyte_name}"
                new_display_name = st.text_input(
                    f"**{analyte_name}**",
                    value=current_display_name,
                    key=display_name_key,
                    placeholder=analyte_name,
                    help=f"Enter custom display name for {analyte_name}"
                )
                
                # Update customization service when value changes
                if new_display_name.strip():
                    # User entered a custom name
                    customization_service.update_analyte_mapping(analyte_name, new_display_name.strip())
                else:
                    # User cleared the field, remove the mapping (use original name)
                    # Set mapping to empty string to clear it (CustomizationSettings.set_analyte_display_name handles this)
                    customization_service.settings.set_analyte_display_name(analyte_name, "")
        else:
            st.info("ℹ️ Select analytes in the main panel to customize their display names")


def render_date_format_section():
    """Render the Date Format section."""
    with st.expander("📅 Date Format", expanded=False):
        customization_service = st.session_state.customization_service
        
        # Date format selection
        date_format_options = [
            "YYYY-MM-DD",
            "MM/DD/YYYY",
            "DD/MM/YYYY",
            "MM-DD-YYYY",
            "DD-MM-YYYY",
            "MMM DD, YYYY",
            "MMMM DD, YYYY",
            "YYYY/MM/DD",
            "MMMM, YYYY",
            "MMM, YYYY"
        ]
        
        # Get current date format
        current_format = customization_service.get_date_format()
        
        # Find current index
        current_index = 0
        if current_format in date_format_options:
            current_index = date_format_options.index(current_format)
        
        # Date format selectbox
        selected_format = st.selectbox(
            "Date Format",
            options=date_format_options,
            index=current_index,
            key="date_format_select",
            help="Select the format for displaying dates in generated tags"
        )
        
        # Update customization service
        if selected_format != current_format:
            customization_service.set_date_format(selected_format)
        
        # Date header text
        current_header_text = customization_service.get_date_header_text()
        date_header_text = st.text_input(
            "Date Header Text",
            value=current_header_text,
            key="date_header_text_input",
            help="Text to display in the first column of the date header row"
        )
        
        # Update customization service
        if date_header_text != current_header_text:
            customization_service.set_date_header_text(date_header_text)


def render_tag_format_section():
    """Render the Tag Format Options section."""
    with st.expander("🏷️ Tag Format Options", expanded=False):
        customization_service = st.session_state.customization_service
        
        # Non-detect setting
        current_non_detect = customization_service.get_show_non_detect_as_nd()
        show_non_detect = st.checkbox(
            "Show Non-Detect Values as ND",
            value=current_non_detect,
            key="non_detect_checkbox",
            help="When enabled, values that start with '<' and end with 'U' will be displayed as 'ND' in the generated tags"
        )
        
        # Update customization service
        if show_non_detect != current_non_detect:
            customization_service.set_show_non_detect_as_nd(show_non_detect)
        
        # Center analyte names
        current_center = customization_service.get_center_analyte_names()
        center_analyte_names = st.checkbox(
            "Center Analyte Names",
            value=current_center,
            key="center_analyte_names_checkbox",
            help="When enabled, analyte names will be centered in their cells on the generated tags"
        )
        
        # Update customization service
        if center_analyte_names != current_center:
            customization_service.set_center_analyte_names(center_analyte_names)


def render_exceedance_handling_section():
    """Render the Exceedance Handling section."""
    with st.expander("⚠️ Exceedance Handling", expanded=False):
        # Add CSS to reduce spacing between color pickers and separator lines
        st.markdown("""
        <style>
        /* Reduce spacing after color picker widgets */
        div[data-testid="stColorPicker"] {
            margin-bottom: 0 !important;
        }
        /* Reduce spacing in the widget container */
        div[data-testid="stColorPicker"] > div {
            margin-bottom: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        customization_service = st.session_state.customization_service
        
        # Check if parser is loaded and has standards columns
        parser = st.session_state.get('parser')
        if not parser or not st.session_state.get('file_loaded', False):
            st.info("ℹ️ Upload a file to configure exceedance handling")
            return
        
        # Get standards columns from parser
        standards_columns = parser.get_standards_columns()
        
        if not standards_columns:
            st.info("ℹ️ No standards columns detected in the uploaded file")
            return
        
        # Global settings
        # Bold exceedances checkbox
        current_bold = customization_service.get_exceedance_bold()
        exceedance_bold = st.checkbox(
            "Bold Exceedances",
            value=current_bold,
            key="exceedance_bold_checkbox",
            help="When enabled, values that exceed any standard will be displayed in bold"
        )
        
        # Update customization service
        if exceedance_bold != current_bold:
            customization_service.set_exceedance_bold(exceedance_bold)
        
        # Exceedance fill color
        current_fill_color = customization_service.get_exceedance_fill_color()
        exceedance_fill_color = st.color_picker(
            "Exceedance Fill Color",
            value=current_fill_color,
            key="exceedance_fill_color_picker",
            help="Background color for cells that exceed any standard"
        )
        
        # Update customization service
        if exceedance_fill_color != current_fill_color:
            customization_service.set_exceedance_fill_color(exceedance_fill_color)
        
        # Per-standards-column settings
        # Display settings for each standards column
        # Use enumerate to ensure unique keys even if there are duplicate column names
        for idx, standards_col_name in enumerate(standards_columns):
            # Add separator before NYSDEC SCO COM1
            if "NYSDEC SCO COM1" in standards_col_name or standards_col_name == "NYSDEC SCO COM1":
                st.markdown('<hr style="margin-top: 0.5rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
            
            # Enable/disable checkbox
            # Use index in key to ensure uniqueness even with duplicate column names
            current_enabled = customization_service.get_standards_enabled(standards_col_name)
            enabled = st.checkbox(
                f"Enable {standards_col_name}",
                value=current_enabled,
                key=f"standards_enabled_{idx}_{standards_col_name}",
                help=f"Enable exceedance checking for {standards_col_name}"
            )
            
            # Update customization service
            if enabled != current_enabled:
                customization_service.set_standards_enabled(standards_col_name, enabled)
            
            # Text color picker
            # Use index in key to ensure uniqueness even with duplicate column names
            current_text_color = customization_service.get_standards_text_color(standards_col_name)
            text_color = st.color_picker(
                f"Text Color for {standards_col_name}",
                value=current_text_color,
                key=f"standards_text_color_{idx}_{standards_col_name}",
                help=f"Text color to use when value exceeds {standards_col_name}"
            )
            
            # Update customization service
            if text_color != current_text_color:
                customization_service.set_standards_text_color(standards_col_name, text_color)
            
            # Add spacing between standards columns
            st.markdown('<hr style="margin-top: 0.25rem; margin-bottom: 0.5rem;">', unsafe_allow_html=True)
        
        # Update preview service when customization changes
        if st.session_state.parser and st.session_state.file_loaded:
            st.session_state.preview_service = PreviewService(
                st.session_state.parser, 
                st.session_state.customization_service
            )


def render_colors_section():
    """Render the Colors section."""
    with st.expander("🎨 Colors", expanded=False):
        customization_service = st.session_state.customization_service
        
        # Header fill color
        current_header_color = customization_service.get_header_fill_color()
        header_color = st.color_picker(
            "Header Fill Color",
            value=current_header_color,
            key="header_color_picker",
            help="Background color for header rows in generated tags"
        )
        
        # Update customization service
        if header_color != current_header_color:
            customization_service.set_header_fill_color(header_color)
        
        # Show current color value
        st.caption(f"Current: {header_color}")


def render_fonts_section():
    """Render the Fonts section."""
    with st.expander("🔤 Fonts", expanded=False):
        customization_service = st.session_state.customization_service
        
        # Font family selection
        font_family_options = [
            "Arial",
            "Calibri",
            "Times New Roman",
            "Helvetica",
            "Verdana",
            "Georgia",
            "Tahoma",
            "Trebuchet MS",
            "Courier New",
            "Impact"
        ]
        
        current_font_family = customization_service.get_font_family()
        
        # Find current index
        font_index = 0
        if current_font_family in font_family_options:
            font_index = font_family_options.index(current_font_family)
        
        font_family = st.selectbox(
            "Font Family",
            options=font_family_options,
            index=font_index,
            key="font_family_select",
            help="Font family for text in generated tags"
        )
        
        # Update customization service
        if font_family != current_font_family:
            customization_service.set_font_family(font_family)
        
        # Font size selection
        current_font_size = customization_service.get_font_size()
        font_size = st.number_input(
            "Font Size (points)",
            min_value=6,
            max_value=72,
            value=current_font_size,
            step=1,
            key="font_size_input",
            help="Font size in points for text in generated tags"
        )
        
        # Update customization service
        if font_size != current_font_size:
            customization_service.set_font_size(font_size)
        
        # Update preview service when customization changes
        if st.session_state.parser and st.session_state.file_loaded:
            st.session_state.preview_service = PreviewService(
                st.session_state.parser, 
                st.session_state.customization_service
            )


def render_customization_sidebar():
    """
    Render the customization sidebar with all customization options.
    
    This function renders the sidebar header and all customization sections:
    - Analyte Name Mapping
    - Date Format
    - Tag Format Options
    - Exceedance Handling
    - Colors
    - Fonts
    """
    # Use negative margin to pull header up and reduce empty space
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] h2:first-of-type {
            margin-top: -3.5rem !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.header("⚙️ Customization Options")
    
    # Render customization sections
    render_analyte_mapping_section()
    render_date_format_section()
    render_tag_format_section()
    render_exceedance_handling_section()
    render_colors_section()
    render_fonts_section()

