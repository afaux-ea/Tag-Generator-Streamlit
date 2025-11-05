#!/usr/bin/env python3
"""
Tag Generator - Streamlit Application

A web-based application for generating formatted tags from environmental sampling data.
Last updated: 2025-01-27
This application allows users to:
- Upload Excel files containing sampling data
- Select locations, analytes, and sampling dates
- Customize tag appearance (colors, fonts, date formats, etc.)
- Preview generated tags before export
- Export tags to Excel format

The application is built with Streamlit and follows a modular component architecture
for maintainability and extensibility.
"""

import streamlit as st

# UI Components
from src.ui.styles.theme import inject_theme
from src.ui.components.header import render_header
from src.ui.components.file_upload import render_file_upload
from src.ui.components.location_selector import render_location_selector
from src.ui.components.analyte_selector import render_analyte_selector
from src.ui.components.date_selector import render_date_selector
from src.ui.components.preview_panel import render_preview_panel

# Sidebar Components
from src.ui.sidebar.customization_sidebar import render_customization_sidebar
from src.ui.sidebar.export_section import render_export_section

# State Management
from src.state.session_manager import initialize_session_state

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Tag Generator",
    page_icon="🏷️",
    layout="wide"
)

# ============================================================================
# Application Initialization
# ============================================================================

inject_theme()
initialize_session_state()

# ============================================================================
# Main Application Layout
# ============================================================================

# Header
render_header()

# File Upload
render_file_upload()

# Selection Panels (only shown when file is loaded)
if st.session_state.file_loaded and st.session_state.parser is not None:
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_location_selector(st.session_state.parser)
    
    with col2:
        render_analyte_selector(st.session_state.parser)
    
    with col3:
        render_date_selector(st.session_state.parser)

# Sidebar (Customization and Export)
with st.sidebar:
    render_customization_sidebar()
    render_export_section()

# Preview Panel (only shown when selections are complete)
render_preview_panel()

