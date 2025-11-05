"""
Session State Manager Module

Centralized management of Streamlit session state variables.
Provides functions to initialize, reset, and clear session state.
"""

import streamlit as st
from src.logic.customization_service import CustomizationService


def initialize_session_state():
    """
    Initialize all session state variables with their default values.
    
    This function should be called at the start of the application
    to ensure all required session state variables exist.
    """
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
    if 'last_selection_hash' not in st.session_state:
        st.session_state.last_selection_hash = None


def reset_file_state():
    """
    Reset all file-related session state variables.
    
    This clears the uploaded file, parser, and file_loaded flag.
    """
    st.session_state.uploaded_file = None
    st.session_state.file_name = None
    st.session_state.parser = None
    st.session_state.file_loaded = False


def reset_selection_state():
    """
    Reset all selection-related session state variables.
    
    This clears selected locations, analytes, dates, preview data,
    export data, and resets the preview index.
    """
    st.session_state.selected_locations = []
    st.session_state.selected_analytes = []
    st.session_state.selected_dates = []
    st.session_state.preview_data = []
    st.session_state.current_preview_index = 0
    st.session_state.export_excel_bytes = None
    st.session_state.export_filename = None
    st.session_state.export_tag_count = 0
    st.session_state.last_selection_hash = None


def clear_analyte_checkboxes():
    """
    Clear all analyte checkbox states from session state.
    
    This removes all keys that start with "analyte_" from session state.
    """
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("analyte_")]
    for key in keys_to_delete:
        del st.session_state[key]


def clear_date_checkboxes():
    """
    Clear all date checkbox states from session state.
    
    This removes all keys that start with "date_" from session state.
    """
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith("date_")]
    for key in keys_to_delete:
        del st.session_state[key]


def clear_date_checkboxes_for_location(location_id: str):
    """
    Clear date checkbox states for a specific location.
    
    Args:
        location_id: The location ID to clear date checkboxes for
    """
    prefix = f"date_{location_id}_"
    keys_to_delete = [key for key in st.session_state.keys() if key.startswith(prefix)]
    for key in keys_to_delete:
        del st.session_state[key]


def reset_all_state():
    """
    Reset all session state (file and selections).
    
    This is a convenience function that calls both reset_file_state()
    and reset_selection_state(), and also clears all checkbox states.
    """
    reset_file_state()
    reset_selection_state()
    clear_analyte_checkboxes()
    clear_date_checkboxes()

