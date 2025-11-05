"""
Header Component Module

Renders the application header with logo and title.
"""

import streamlit as st


def render_header(image_path: str = "src/images/EA.png", image_width: int = 120):
    """
    Render the application header with logo and title.
    
    Args:
        image_path: Path to the logo image file (default: "src/images/EA.png")
        image_width: Width of the logo image in pixels (default: 120)
    """
    col1, col2 = st.columns([1, 10])
    
    with col1:
        try:
            st.image(image_path, width=image_width)
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

