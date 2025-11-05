"""
Analyte Selector Component Module

Handles analyte selection UI with categorized expanders and checkboxes.
"""

import streamlit as st


def render_analyte_selector(parser):
    """
    Render the analyte selection component.
    
    Args:
        parser: ExcelParser instance to get available categories and analytes from
    """
    with st.container():
        st.markdown("### 🧪 Analytes")
        
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

