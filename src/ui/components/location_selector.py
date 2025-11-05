"""
Location Selector Component Module

Handles location selection UI with multiselect and Select All/Clear All functionality.
"""

import streamlit as st
from src.state.session_manager import clear_date_checkboxes_for_location


def render_location_selector(parser):
    """
    Render the location selection component.
    
    Args:
        parser: ExcelParser instance to get available locations from
    """
    with st.container():
        st.markdown("### 📍 Locations")
        
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
                    clear_date_checkboxes_for_location(location_id)
            
            # Display selection count
            if selected_locations:
                st.success(f"✅ **{len(selected_locations)}** selected")
            else:
                st.warning("⚠️ Select locations")
        else:
            st.warning("⚠️ No locations found")

