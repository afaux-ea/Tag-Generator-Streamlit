#!/usr/bin/env python3
"""
Tag Generator - Streamlit Application

This is the Streamlit version of the Tag Generator application.
It converts the PyQt5 desktop application to a web-based interface.
"""

import streamlit as st
import os
import tempfile
import pandas as pd
import hashlib
from datetime import datetime
from src.logic.parser import ExcelParser
from src.logic.customization_service import CustomizationService
from src.logic.preview_service import PreviewService
from src.logic.tag_generator import TagGenerator
from src.logic.exporter import ExcelExporter

# Set page config
st.set_page_config(
    page_title="Tag Generator",
    page_icon="🏷️",
    layout="wide"
)

# Inject custom CSS to force blue theme for buttons and checkboxes
st.markdown(
    """
    <style>
    /* Override Streamlit's CSS variables for primary color */
    :root {
        --primary-color: #0066CC !important;
    }
    
    /* Override primary button color - all buttons */
    .stButton > button[kind="primary"],
    .stButton > button[data-kind="primary"],
    button[kind="primary"],
    button[data-kind="primary"] {
        background-color: #0066CC !important;
        color: white !important;
        border-color: #0066CC !important;
    }
    
    .stButton > button[kind="primary"]:hover,
    .stButton > button[data-kind="primary"]:hover,
    button[kind="primary"]:hover,
    button[data-kind="primary"]:hover {
        background-color: #0052A3 !important;
        border-color: #0052A3 !important;
    }
    
    /* Override checkbox checked color to blue - BaseWeb styling */
    /* Target the span element that contains the checkmark */
    [data-baseweb="checkbox"] span[style*="background"],
    [data-baseweb="checkbox"] span[style*="background-color"],
    [data-baseweb="checkbox"] > span,
    .stCheckbox [data-baseweb="checkbox"] > span {
        background-color: #0066CC !important;
        border-color: #0066CC !important;
    }
    
    /* Target when checkbox is checked - more specific selectors */
    [data-baseweb="checkbox"] input[type="checkbox"]:checked + span,
    [data-baseweb="checkbox"] input:checked ~ span,
    [data-baseweb="checkbox"]:has(input:checked) > span,
    [data-baseweb="checkbox"][aria-checked="true"] > span,
    [data-baseweb="checkbox"]:has([aria-checked="true"]) > span {
        background-color: #0066CC !important;
        border-color: #0066CC !important;
    }
    
    /* Override checkbox background image container */
    [data-baseweb="checkbox"] span[style*="background-image"] {
        background-color: #0066CC !important;
        border-color: #0066CC !important;
    }
    
    /* Override checkbox SVG fill color */
    [data-baseweb="checkbox"] [aria-checked="true"] svg,
    [data-baseweb="checkbox"]:has(input:checked) svg {
        fill: white !important;
    }
    
    /* Standard checkbox override */
    input[type="checkbox"]:checked {
        accent-color: #0066CC !important;
    }
    
    /* Force override all checkbox styling with higher specificity */
    div[data-baseweb="checkbox"] span,
    label[data-baseweb="checkbox"] span {
        background-color: transparent !important;
    }
    
    div[data-baseweb="checkbox"]:has(input:checked) span,
    label[data-baseweb="checkbox"]:has(input:checked) span,
    div[data-baseweb="checkbox"] input:checked + span,
    label[data-baseweb="checkbox"] input:checked + span {
        background-color: #0066CC !important;
        border-color: #0066CC !important;
    }
    
    /* Override multiselect selected items (tags) to blue */
    .stMultiSelect [data-baseweb="tag"],
    [data-baseweb="tag"] {
        background-color: #0066CC !important;
        color: white !important;
    }
    
    /* Override BaseWeb tag styling */
    [data-baseweb="tag"] span {
        color: white !important;
    }
    
    /* Override all primary-colored elements */
    [data-baseweb="button"][aria-selected="true"],
    [data-baseweb="button"].primary {
        background-color: #0066CC !important;
        color: white !important;
        border-color: #0066CC !important;
    }
    </style>
    <script>
    // Force checkboxes to blue after page load
    function forceCheckboxBlue() {
        const checkboxes = document.querySelectorAll('[data-baseweb="checkbox"]');
        checkboxes.forEach(function(cb) {
            const input = cb.querySelector('input[type="checkbox"]');
            if (input) {
                // Check initial state
                if (input.checked) {
                    const span = cb.querySelector('span');
                    if (span) {
                        span.style.setProperty('background-color', '#0066CC', 'important');
                        span.style.setProperty('border-color', '#0066CC', 'important');
                    }
                }
                // Watch for changes
                input.addEventListener('change', function() {
                    const span = cb.querySelector('span');
                    if (span) {
                        if (this.checked) {
                            span.style.setProperty('background-color', '#0066CC', 'important');
                            span.style.setProperty('border-color', '#0066CC', 'important');
                        }
                    }
                });
            }
        });
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceCheckboxBlue);
    } else {
        forceCheckboxBlue();
    }
    
    // Also run after a delay to catch dynamically loaded checkboxes
    setTimeout(forceCheckboxBlue, 500);
    setTimeout(forceCheckboxBlue, 1000);
    
    // Use MutationObserver to watch for new checkboxes
    const observer = new MutationObserver(function(mutations) {
        forceCheckboxBlue();
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    </script>
    """,
    unsafe_allow_html=True
)

# Initialize session state variables
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'parser' not in st.session_state:
    st.session_state.parser = None
if 'file_loaded' not in st.session_state:
    st.session_state.file_loaded = False
if 'selected_locations' not in st.session_state:
    st.session_state.selected_locations = []
if 'selected_analytes' not in st.session_state:
    st.session_state.selected_analytes = []
if 'selected_dates' not in st.session_state:
    st.session_state.selected_dates = []
if 'customization_service' not in st.session_state:
    st.session_state.customization_service = CustomizationService()
if 'preview_service' not in st.session_state:
    st.session_state.preview_service = None
if 'preview_data' not in st.session_state:
    st.session_state.preview_data = []
if 'current_preview_index' not in st.session_state:
    st.session_state.current_preview_index = 0
if 'export_excel_bytes' not in st.session_state:
    st.session_state.export_excel_bytes = None
if 'export_filename' not in st.session_state:
    st.session_state.export_filename = None
if 'export_tag_count' not in st.session_state:
    st.session_state.export_tag_count = 0

# Header section
col1, col2 = st.columns([1, 10])
with col1:
    try:
        st.image("src/images/EA.png", width=120)  # Increased from 60 to 120
    except:
        pass  # Image not found, continue without it

with col2:
    # Use markdown with custom styling for better alignment
    st.markdown(
        """
        <div style="display: flex; align-items: center; height: 100%;">
            <h1 style="margin: 0; padding: 0; vertical-align: middle;">Tag Generator</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# File Upload Section
st.subheader("File Selection")

# File uploader
uploaded_file = st.file_uploader(
    "Select Excel File",
    type=['xlsx', 'xls'],
    help="Upload an Excel file (.xlsx or .xls) containing environmental sampling data"
)

# File validation and parsing
if uploaded_file is not None:
    # Validate file extension
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    if file_extension not in ['.xlsx', '.xls']:
        st.error(f"❌ Invalid file type. Please upload an Excel file (.xlsx or .xls)")
        st.session_state.uploaded_file = None
        st.session_state.file_name = None
        st.session_state.parser = None
        st.session_state.file_loaded = False
    else:
        # Check if this is a new file (different from what's already loaded)
        is_new_file = (
            st.session_state.uploaded_file is None or 
            st.session_state.file_name != uploaded_file.name or
            not st.session_state.file_loaded
        )
        
        if is_new_file:
            # Store file in session state
            st.session_state.uploaded_file = uploaded_file
            st.session_state.file_name = uploaded_file.name
            
            # Save uploaded file to temporary file for parser
            with st.spinner("⏳ Loading and parsing file..."):
                try:
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_file_path = tmp_file.name
                    
                    # Create parser and load file
                    parser = ExcelParser()
                    success = parser.load_file(tmp_file_path)
                    
                    # Clean up temporary file
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass  # Ignore cleanup errors
                    
                    if success:
                        # Store parser in session state
                        st.session_state.parser = parser
                        st.session_state.file_loaded = True
                        # Initialize preview service with parser and customization service
                        st.session_state.preview_service = PreviewService(parser, st.session_state.customization_service)
                        # Clear previous selections when new file is loaded
                        st.session_state.selected_locations = []
                        st.session_state.selected_analytes = []
                        st.session_state.selected_dates = []
                        st.session_state.preview_data = []
                        st.session_state.current_preview_index = 0
                        st.session_state.export_excel_bytes = None
                        st.session_state.export_filename = None
                        st.session_state.export_tag_count = 0
                        # Clear all analyte checkbox states
                        for key in list(st.session_state.keys()):
                            if key.startswith("analyte_"):
                                del st.session_state[key]
                        # Clear all date checkbox states
                        for key in list(st.session_state.keys()):
                            if key.startswith("date_"):
                                del st.session_state[key]
                    else:
                        st.error("❌ Failed to parse the file. Please check the file format.")
                        st.session_state.parser = None
                        st.session_state.file_loaded = False
                        
                except Exception as e:
                    st.error(f"❌ Error loading file: {str(e)}")
                    st.session_state.parser = None
                    st.session_state.file_loaded = False
        else:
            # File already loaded
            pass
else:
    # Clear session state if no file
    st.session_state.uploaded_file = None
    st.session_state.file_name = None
    st.session_state.parser = None
    st.session_state.file_loaded = False
    st.session_state.selected_locations = []
    st.session_state.selected_analytes = []
    st.session_state.selected_dates = []
    # Clear all analyte checkbox states
    for key in list(st.session_state.keys()):
        if key.startswith("analyte_"):
            del st.session_state[key]
    # Clear all date checkbox states
    for key in list(st.session_state.keys()):
        if key.startswith("date_"):
            del st.session_state[key]
    st.info("📁 Please select an Excel file to begin")

# Selection Panels - Three Column Layout
if st.session_state.file_loaded and st.session_state.parser is not None:
    st.divider()
    
    # Create three-column layout for selections
    col1, col2, col3 = st.columns(3)
    
    # Column 1: Location Selection
    with col1:
        with st.container():
            st.markdown("### 📍 Locations")
            
            parser = st.session_state.parser
            available_locations = parser.get_locations()
            
            if available_locations:
                # Select All / Clear All buttons
                loc_btn_col1, loc_btn_col2 = st.columns([1, 1])
                with loc_btn_col1:
                    if st.button("Select All", key="select_all_locations", use_container_width=True):
                        st.session_state.selected_locations = available_locations.copy()
                        st.session_state.location_multiselect = available_locations.copy()
                        st.rerun()
                with loc_btn_col2:
                    if st.button("Clear All", key="clear_all_locations", use_container_width=True):
                        st.session_state.selected_locations = []
                        st.session_state.location_multiselect = []
                        st.rerun()
                
                # Initialize widget state from session state if it doesn't exist
                if "location_multiselect" not in st.session_state:
                    st.session_state.location_multiselect = st.session_state.selected_locations.copy()
                
                # Location multiselect
                # When a widget has a key, Streamlit uses st.session_state[key] as its value
                selected_locations = st.multiselect(
                    "Select Locations",
                    options=available_locations,
                    key="location_multiselect",
                    help="Select one or more locations to include in tag generation"
                )
                
                # Update session state
                previous_locations = set(st.session_state.selected_locations)
                current_locations = set(selected_locations)
                st.session_state.selected_locations = selected_locations
                
                # Clear date selections for locations that are no longer selected
                if previous_locations != current_locations:
                    # Remove date selections for deselected locations
                    for location_id in previous_locations - current_locations:
                        # Clear all date checkbox states for this location
                        for key in list(st.session_state.keys()):
                            if key.startswith(f"date_{location_id}_"):
                                del st.session_state[key]
                
                # Display selection count
                if selected_locations:
                    st.success(f"✅ **{len(selected_locations)}** selected")
                else:
                    st.warning("⚠️ Select locations")
            else:
                st.warning("⚠️ No locations found")
    
    # Column 2: Analyte Selection
    with col2:
        with st.container():
            st.markdown("### 🧪 Analytes")
            
            parser = st.session_state.parser
            categories = parser.get_categories()
            
            if categories:
                # Build list of selected analytes from checkbox states
                selected_analytes = []
                
                # Create expanders for each category
                for category in categories:
                    if category.analytes:  # Only show category if it has analytes
                        # Count selected analytes in this category
                        category_selected = [a.name for a in category.analytes 
                                           if st.session_state.get(f"analyte_{category.name}_{a.name}", False)]
                        
                        # Keep expander open if it has selections
                        should_expand = len(category_selected) > 0
                        
                        with st.expander(f"📁 {category.name} ({len(category_selected)}/{len(category.analytes)})", expanded=should_expand):
                            # Select All / Clear All buttons for this category
                            cat_col1, cat_col2 = st.columns([1, 1])
                            with cat_col1:
                                if st.button(f"All", key=f"select_all_{category.name}", use_container_width=True):
                                    # Select all analytes in this category
                                    for analyte in category.analytes:
                                        analyte_key = f"analyte_{category.name}_{analyte.name}"
                                        st.session_state[analyte_key] = True
                                    st.rerun()
                            with cat_col2:
                                if st.button(f"Clear", key=f"clear_all_{category.name}", use_container_width=True):
                                    # Clear all analytes in this category
                                    for analyte in category.analytes:
                                        analyte_key = f"analyte_{category.name}_{analyte.name}"
                                        st.session_state[analyte_key] = False
                                    st.rerun()
                            
                            st.divider()
                            
                            # Create checkboxes for each analyte in this category
                            for analyte in category.analytes:
                                analyte_key = f"analyte_{category.name}_{analyte.name}"
                                
                                # Create checkbox for this analyte
                                checked = st.checkbox(
                                    analyte.name,
                                    value=st.session_state.get(analyte_key, False),
                                    key=analyte_key,
                                    help=f"Category: {category.name}" + (f" | Threshold: {analyte.threshold}" if analyte.threshold is not None else "")
                                )
                                
                                # Add to selected list if checked
                                if checked:
                                    selected_analytes.append(analyte.name)
                
                # Update session state with selected analytes list
                st.session_state.selected_analytes = selected_analytes
                
                # Display selection count
                if selected_analytes:
                    st.success(f"✅ **{len(selected_analytes)}** selected")
                else:
                    st.warning("⚠️ Select analytes")
            else:
                st.warning("⚠️ No categories found")
    
    # Column 3: Date Selection
    with col3:
        with st.container():
            st.markdown("### 📅 Sampling Dates")
            
            parser = st.session_state.parser
            selected_locations = st.session_state.selected_locations
            
            if selected_locations:
                # Build list of selected dates from checkbox states
                selected_dates = []
                
                # Get dates for each selected location
                location_dates_dict = {}
                for location_id in selected_locations:
                    dates = parser.get_dates_by_location(location_id)
                    if dates:
                        location_dates_dict[location_id] = sorted(dates)
                
                if location_dates_dict:
                    # Create expanders for each location that has dates
                    for location_id in sorted(location_dates_dict.keys()):
                        dates = location_dates_dict[location_id]
                        
                        # Count selected dates for this location
                        location_selected = [f"DATE:{location_id}:{date}" for date in dates
                                           if st.session_state.get(f"date_{location_id}_{date}", False)]
                        
                        # Keep expander open if it has selections
                        should_expand = len(location_selected) > 0
                        
                        with st.expander(f"📍 {location_id} ({len(location_selected)}/{len(dates)})", expanded=should_expand):
                            # Select All / Clear All buttons for this location
                            date_col1, date_col2 = st.columns([1, 1])
                            with date_col1:
                                if st.button(f"All", key=f"select_all_dates_{location_id}", use_container_width=True):
                                    # Select all dates for this location
                                    for date in dates:
                                        date_key = f"date_{location_id}_{date}"
                                        st.session_state[date_key] = True
                                    st.rerun()
                            with date_col2:
                                if st.button(f"Clear", key=f"clear_all_dates_{location_id}", use_container_width=True):
                                    # Clear all dates for this location
                                    for date in dates:
                                        date_key = f"date_{location_id}_{date}"
                                        st.session_state[date_key] = False
                                    st.rerun()
                            
                            st.divider()
                            
                            # Create checkboxes for each date
                            for date in dates:
                                date_key = f"date_{location_id}_{date}"
                                
                                # Create checkbox for this date
                                checked = st.checkbox(
                                    date,
                                    value=st.session_state.get(date_key, False),
                                    key=date_key,
                                    help=f"Location: {location_id}"
                                )
                                
                                # Add to selected list if checked
                                if checked:
                                    selected_dates.append(f"DATE:{location_id}:{date}")
                    
                    # Update session state with selected dates list
                    st.session_state.selected_dates = selected_dates
                    
                    # Display selection count
                    if selected_dates:
                        st.success(f"✅ **{len(selected_dates)}** selected")
                    else:
                        st.warning("⚠️ Select dates")
                else:
                    st.warning("⚠️ No dates found")
            else:
                st.info("ℹ️ Select locations first")

# Customization Sidebar
with st.sidebar:
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
    
    # Analyte Name Mapping Section
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
    
    # Date Format Section
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
    
    # Tag Format Options Section
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
    
    # Colors Section
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
        
        # Exceedance fill color
        current_exceedance_color = customization_service.get_exceedance_fill_color()
        exceedance_color = st.color_picker(
            "Exceedance Fill Color",
            value=current_exceedance_color,
            key="exceedance_color_picker",
            help="Background color for cells that exceed threshold values"
        )
        
        # Update customization service
        if exceedance_color != current_exceedance_color:
            customization_service.set_exceedance_fill_color(exceedance_color)
        
        # Show current color value
        st.caption(f"Current: {exceedance_color}")
    
    # Fonts Section
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
    
    # Export Section
    st.divider()
    st.subheader("📥 Export Tags")
    
    # Check if selections are ready for export
    if (st.session_state.file_loaded and 
        st.session_state.parser is not None and
        st.session_state.selected_locations and
        st.session_state.selected_analytes and
        st.session_state.selected_dates):
        
        # Validate selections
        can_export = (
            len(st.session_state.selected_locations) > 0 and
            len(st.session_state.selected_analytes) > 0 and
            len(st.session_state.selected_dates) > 0
        )
        
        if can_export:
            # Create a hash of current selections AND customization settings to detect changes
            customization_service = st.session_state.customization_service
            
            # Build a hash string that includes selections and all customization settings
            hash_components = [
                str(sorted(st.session_state.selected_locations)),
                str(sorted(st.session_state.selected_analytes)),
                str(sorted(st.session_state.selected_dates)),
            ]
            
            # Add customization settings to hash
            if customization_service:
                # Analyte mappings (sorted for consistency)
                analyte_mappings = customization_service.get_analyte_mappings()
                hash_components.append(str(sorted(analyte_mappings.items())))
                
                # Date format settings
                hash_components.append(customization_service.get_date_format())
                hash_components.append(customization_service.get_date_header_text())
                
                # Tag format options
                hash_components.append(str(customization_service.get_show_non_detect_as_nd()))
                hash_components.append(str(customization_service.get_center_analyte_names()))
                
                # Colors
                hash_components.append(customization_service.get_header_fill_color())
                hash_components.append(customization_service.get_exceedance_fill_color())
                
                # Fonts
                hash_components.append(customization_service.get_font_family())
                hash_components.append(str(customization_service.get_font_size()))
            
            # Create hash from all components
            selection_hash = hashlib.md5(
                str(hash_components).encode()
            ).hexdigest()
            
            # Track last selection hash in session state
            if 'last_selection_hash' not in st.session_state:
                st.session_state.last_selection_hash = None
            
            # Auto-generate Excel file when selections or customizations change or don't exist
            needs_regeneration = (
                st.session_state.export_excel_bytes is None or
                st.session_state.last_selection_hash != selection_hash
            )
            
            if needs_regeneration:
                try:
                    with st.spinner("⏳ Generating tags..."):
                        # Initialize TagGenerator
                        tag_generator = TagGenerator(
                            st.session_state.parser,
                            st.session_state.customization_service
                        )
                        
                        # Generate tags
                        generated_tags = tag_generator.generate_tags(
                            st.session_state.selected_locations,
                            st.session_state.selected_analytes,
                            st.session_state.selected_dates
                        )
                        
                        if not generated_tags:
                            st.warning("⚠️ No tags were generated. Please check your selections.")
                            st.session_state.export_excel_bytes = None
                            st.session_state.export_filename = None
                            st.session_state.export_tag_count = 0
                            st.session_state.last_selection_hash = selection_hash
                        else:
                            # Initialize ExcelExporter
                            exporter = ExcelExporter(st.session_state.customization_service)
                            
                            # Save to temporary file first (ExcelExporter expects a file path)
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                                tmp_file_path = tmp_file.name
                            
                            # Export to temporary file
                            success = exporter.export_tags(generated_tags, tmp_file_path)
                            
                            if success:
                                # Read the file into bytes
                                with open(tmp_file_path, 'rb') as f:
                                    excel_bytes = f.read()
                                
                                # Clean up temporary file
                                os.unlink(tmp_file_path)
                                
                                # Generate filename
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"tags_{timestamp}.xlsx"
                                
                                # Store in session state
                                st.session_state.export_excel_bytes = excel_bytes
                                st.session_state.export_filename = filename
                                st.session_state.export_tag_count = len(generated_tags)
                                st.session_state.last_selection_hash = selection_hash
                            else:
                                st.error("❌ Failed to export tags to Excel. Please try again.")
                                st.session_state.export_excel_bytes = None
                                st.session_state.export_filename = None
                                st.session_state.export_tag_count = 0
                                st.session_state.last_selection_hash = selection_hash
                                # Clean up temporary file on error
                                if os.path.exists(tmp_file_path):
                                    os.unlink(tmp_file_path)
                
                except Exception as e:
                    st.error(f"❌ Error exporting tags: {str(e)}")
                    st.session_state.export_excel_bytes = None
                    st.session_state.export_filename = None
                    st.session_state.export_tag_count = 0
                    st.session_state.last_selection_hash = selection_hash
                    # Clean up temporary file on error
                    if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
            
            # Show download button if export is ready
            if st.session_state.export_excel_bytes is not None:
                st.success(f"✅ Ready to download {st.session_state.export_tag_count} tag(s)!")
                st.download_button(
                    label="📥 Download Excel File",
                    data=st.session_state.export_excel_bytes,
                    file_name=st.session_state.export_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.info("ℹ️ Please make selections for locations, analytes, and dates to export tags.")
    else:
        st.info("ℹ️ Please load a file and make selections to export tags.")

def _display_preview_table(preview):
    """Display a preview table with styling and highlighting."""
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

# Preview Panel - Collapsible bottom panel
if (st.session_state.file_loaded and 
    st.session_state.parser is not None and
    st.session_state.selected_locations and
    st.session_state.selected_analytes and
    st.session_state.selected_dates):
    
    # Update preview service if parser changed
    if st.session_state.preview_service is None:
        st.session_state.preview_service = PreviewService(
            st.session_state.parser,
            st.session_state.customization_service
        )
    else:
        # Update preview service with current parser and customization service
        st.session_state.preview_service = PreviewService(
            st.session_state.parser,
            st.session_state.customization_service
        )
    
    # Generate preview data
    try:
        preview_data = st.session_state.preview_service.generate_preview_data(
            st.session_state.selected_locations,
            st.session_state.selected_analytes,
            st.session_state.selected_dates
        )
        
        # Update session state
        st.session_state.preview_data = preview_data
        
        # Reset to first preview if index is out of bounds
        if st.session_state.current_preview_index >= len(preview_data):
            st.session_state.current_preview_index = 0
        
        # Show preview count in title
        preview_count = len(preview_data) if preview_data else 0
        preview_title = f"👁️ Preview ({preview_count} tag{'s' if preview_count != 1 else ''})"
        
        # Add separator before preview panel
        st.divider()
        
        # Preview panel at bottom (not collapsible)
        st.subheader(preview_title)
        
        if preview_data:
            # Navigation controls - left-aligned with minimal spacing
            col1, col2, col3, col4 = st.columns([1, 1, 1, 7])
            with col1:
                if st.button("← Previous", disabled=st.session_state.current_preview_index == 0, key="prev_preview"):
                    if st.session_state.current_preview_index > 0:
                        st.session_state.current_preview_index -= 1
                        st.rerun()
            
            with col2:
                st.markdown(f"**Tag {st.session_state.current_preview_index + 1} of {len(preview_data)}**")
            
            with col3:
                if st.button("Next →", disabled=st.session_state.current_preview_index >= len(preview_data) - 1, key="next_preview"):
                    if st.session_state.current_preview_index < len(preview_data) - 1:
                        st.session_state.current_preview_index += 1
                        st.rerun()
            
            # col4 is empty, used for spacing
            
            # Display current preview
            if st.session_state.current_preview_index < len(preview_data):
                current_preview = preview_data[st.session_state.current_preview_index]
                _display_preview_table(current_preview)
        else:
            st.info("No preview data available. Please check your selections.")
        
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")
        st.session_state.preview_data = []

