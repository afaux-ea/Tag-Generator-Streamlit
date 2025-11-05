"""
Date Selector Component Module

Handles date selection UI with location-based expanders and checkboxes.
"""

import streamlit as st


def render_date_selector(parser):
    """
    Render the date selection component.
    
    Args:
        parser: ExcelParser instance to get available dates by location from
    """
    with st.container():
        st.markdown("### 📅 Sampling Dates")
        
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

