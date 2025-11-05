"""
File Upload Component Module

Handles file upload UI and file processing logic.
"""

import streamlit as st
from src.logic.parser import ExcelParser
from src.logic.preview_service import PreviewService
from src.utils.file_handlers import (
    validate_file_extension,
    save_uploaded_file_to_temp,
    cleanup_temp_file
)
from src.state.session_manager import (
    reset_file_state,
    reset_selection_state,
    clear_analyte_checkboxes,
    clear_date_checkboxes
)


def render_file_upload():
    """
    Render the file upload section with validation and parsing.
    
    This function handles:
    - File uploader widget
    - File validation
    - File parsing
    - Session state management for file-related data
    """
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
        is_valid, file_extension = validate_file_extension(uploaded_file.name)
        
        if not is_valid:
            st.error(f"❌ Invalid file type. Please upload an Excel file (.xlsx or .xls)")
            reset_file_state()
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
                    tmp_file_path = None
                    try:
                        # Save uploaded file to temporary file
                        tmp_file_path = save_uploaded_file_to_temp(uploaded_file, file_extension)
                        
                        if tmp_file_path is None:
                            st.error("❌ Failed to save uploaded file. Please try again.")
                            reset_file_state()
                        else:
                            # Create parser and load file
                            parser = ExcelParser()
                            success = parser.load_file(tmp_file_path)
                            
                            # Clean up temporary file
                            cleanup_temp_file(tmp_file_path)
                            
                            if success:
                                # Store parser in session state
                                st.session_state.parser = parser
                                st.session_state.file_loaded = True
                                # Initialize preview service with parser and customization service
                                st.session_state.preview_service = PreviewService(
                                    parser, 
                                    st.session_state.customization_service
                                )
                                # Clear previous selections when new file is loaded
                                reset_selection_state()
                                clear_analyte_checkboxes()
                                clear_date_checkboxes()
                            else:
                                st.error("❌ Failed to parse the file. Please check the file format.")
                                reset_file_state()
                                
                    except Exception as e:
                        st.error(f"❌ Error loading file: {str(e)}")
                        reset_file_state()
                        # Clean up temporary file on error
                        if tmp_file_path:
                            cleanup_temp_file(tmp_file_path)
            else:
                # File already loaded
                pass
    else:
        # Clear session state if no file
        reset_file_state()
        reset_selection_state()
        clear_analyte_checkboxes()
        clear_date_checkboxes()
        st.info("📁 Please select an Excel file to begin")

