"""
Preview Panel Component Module

Handles the preview panel UI with navigation and preview table display.
"""

import streamlit as st
from src.logic.preview_service import PreviewService
from .preview_table import display_preview_table


def render_preview_panel():
    """
    Render the preview panel if conditions are met.
    
    Conditions:
    - File is loaded
    - Parser exists
    - Locations, analytes, and dates are selected
    """
    # Check if conditions are met
    if not (st.session_state.file_loaded and 
            st.session_state.parser is not None and
            st.session_state.selected_locations and
            st.session_state.selected_analytes and
            st.session_state.selected_dates):
        return
    
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
                display_preview_table(current_preview)
        else:
            st.info("No preview data available. Please check your selections.")
        
    except Exception as e:
        st.error(f"Error generating preview: {str(e)}")
        st.session_state.preview_data = []

