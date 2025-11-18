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
        # Check if sample depth is enabled (use session state to reflect current checkbox state)
        has_sample_depth = st.session_state.get('has_sample_depth', False) if parser else False
        
        # Update heading based on sample depth setting
        heading_text = "### 📅 Sampling Dates/Depths" if has_sample_depth else "### 📅 Sampling Dates"
        st.markdown(heading_text)
        
        selected_locations = st.session_state.selected_locations
        
        if selected_locations:
            # Build list of selected dates from checkbox states
            selected_dates = []
            
            if has_sample_depth:
                # Get date-depth combinations for each selected location
                location_combinations_dict = {}
                for location_id in selected_locations:
                    combinations = parser.get_date_depth_combinations(location_id)
                    if combinations:
                        location_combinations_dict[location_id] = combinations
                
                if location_combinations_dict:
                    # Select All Dates / Clear All Dates buttons for all selected locations
                    all_dates_col1, all_dates_col2 = st.columns([1, 1])
                    with all_dates_col1:
                        if st.button("Select All Dates/Depths", key="select_all_dates_all_locations", use_container_width=True):
                            # Select all date-depth combinations for all selected locations
                            for location_id, combinations in location_combinations_dict.items():
                                for date, depth in combinations:
                                    date_key = f"date_{location_id}_{date}_{depth}"
                                    st.session_state[date_key] = True
                            st.rerun()
                    with all_dates_col2:
                        if st.button("Clear All Dates", key="clear_all_dates_all_locations", use_container_width=True):
                            # Clear all date-depth combinations for all selected locations
                            for location_id, combinations in location_combinations_dict.items():
                                for date, depth in combinations:
                                    date_key = f"date_{location_id}_{date}_{depth}"
                                    st.session_state[date_key] = False
                            st.rerun()
                    
                    # Create expanders for each location that has date-depth combinations
                    for location_id in sorted(location_combinations_dict.keys()):
                        combinations = location_combinations_dict[location_id]
                        
                        # Count selected combinations for this location
                        location_selected = [f"DATE:{location_id}:{date}:{depth}" 
                                           for date, depth in combinations
                                           if st.session_state.get(f"date_{location_id}_{date}_{depth}", False)]
                        
                        # Always set expanded to False to prevent auto-expansion
                        with st.expander(f"📍 {location_id} ({len(location_selected)}/{len(combinations)})", expanded=False):
                            # Select All / Clear All buttons for this location
                            date_col1, date_col2 = st.columns([1, 1])
                            with date_col1:
                                if st.button(f"All", key=f"select_all_dates_{location_id}", use_container_width=True):
                                    # Select all combinations for this location
                                    for date, depth in combinations:
                                        date_key = f"date_{location_id}_{date}_{depth}"
                                        st.session_state[date_key] = True
                                    st.rerun()
                            with date_col2:
                                if st.button(f"Clear", key=f"clear_all_dates_{location_id}", use_container_width=True):
                                    # Clear all combinations for this location
                                    for date, depth in combinations:
                                        date_key = f"date_{location_id}_{date}_{depth}"
                                        st.session_state[date_key] = False
                                    st.rerun()
                            
                            st.divider()
                            
                            # Create checkboxes for each date-depth combination
                            for date, depth in combinations:
                                date_key = f"date_{location_id}_{date}_{depth}"
                                display_label = f"{date} ({depth})"
                                
                                # Create checkbox for this date-depth combination
                                checked = st.checkbox(
                                    display_label,
                                    value=st.session_state.get(date_key, False),
                                    key=date_key,
                                    help=f"Location: {location_id}, Depth: {depth}"
                                )
                                
                                # Add to selected list if checked
                                if checked:
                                    selected_dates.append(f"DATE:{location_id}:{date}:{depth}")
                    
                    # Update session state with selected dates list (works for both with and without depth)
                    st.session_state.selected_dates = selected_dates
                    
                    # Display selection count
                    if selected_dates:
                        st.success(f"✅ **{len(selected_dates)}** selected")
                    else:
                        st.warning("⚠️ Select dates")
                else:
                    st.warning("⚠️ No date-depth combinations found")
            else:
                # Original behavior: Get dates for each selected location (no sample depth)
                location_dates_dict = {}
                for location_id in selected_locations:
                    dates = parser.get_dates_by_location(location_id)
                    if dates:
                        location_dates_dict[location_id] = sorted(dates)
                
                if location_dates_dict:
                    # Select All Dates / Clear All Dates buttons for all selected locations
                    all_dates_col1, all_dates_col2 = st.columns([1, 1])
                    with all_dates_col1:
                        if st.button("Select All Dates", key="select_all_dates_all_locations", use_container_width=True):
                            # Select all dates for all selected locations
                            for location_id, dates in location_dates_dict.items():
                                for date in dates:
                                    date_key = f"date_{location_id}_{date}"
                                    st.session_state[date_key] = True
                            st.rerun()
                    with all_dates_col2:
                        if st.button("Clear All Dates", key="clear_all_dates_all_locations", use_container_width=True):
                            # Clear all dates for all selected locations
                            for location_id, dates in location_dates_dict.items():
                                for date in dates:
                                    date_key = f"date_{location_id}_{date}"
                                    st.session_state[date_key] = False
                            st.rerun()
                    
                    # Create expanders for each location that has dates
                    for location_id in sorted(location_dates_dict.keys()):
                        dates = location_dates_dict[location_id]
                        
                        # Count selected dates for this location
                        location_selected = [f"DATE:{location_id}:{date}" for date in dates
                                           if st.session_state.get(f"date_{location_id}_{date}", False)]
                        
                        # Always set expanded to False to prevent auto-expansion
                        # This ensures expanders only open when user manually clicks them
                        # They won't auto-expand when selections change or customization options are modified
                        with st.expander(f"📍 {location_id} ({len(location_selected)}/{len(dates)})", expanded=False):
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
                
                    # Update session state with selected dates list (works for both with and without depth)
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

