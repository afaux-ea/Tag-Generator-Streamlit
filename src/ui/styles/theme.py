"""
Theme Module

Contains custom CSS and JavaScript for applying the blue theme
to Streamlit components (buttons, checkboxes, etc.).
"""

import streamlit as st


def inject_theme():
    """
    Inject custom CSS and JavaScript to force blue theme for buttons and checkboxes.
    
    This function applies styling to override Streamlit's default colors and
    ensure all primary buttons and checked checkboxes use the blue theme (#0066CC).
    """
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
        
        /* Override checkbox checked color to blue - ONLY for checked checkboxes */
        /* Target when checkbox is checked - more specific selectors */
        [data-baseweb="checkbox"] input[type="checkbox"]:checked + span,
        [data-baseweb="checkbox"] input:checked ~ span,
        [data-baseweb="checkbox"]:has(input:checked) > span,
        [data-baseweb="checkbox"][aria-checked="true"] > span,
        [data-baseweb="checkbox"]:has([aria-checked="true"]) > span {
            background-color: #0066CC !important;
            border-color: #0066CC !important;
        }
        
        /* Ensure unchecked checkboxes have transparent/white background */
        [data-baseweb="checkbox"]:not(:has(input:checked)) > span,
        [data-baseweb="checkbox"]:not(:has([aria-checked="true"])) > span,
        [data-baseweb="checkbox"] input:not(:checked) + span {
            background-color: transparent !important;
        }
        
        /* Override checkbox SVG fill color - only for checked */
        [data-baseweb="checkbox"] [aria-checked="true"] svg,
        [data-baseweb="checkbox"]:has(input:checked) svg {
            fill: white !important;
        }
        
        /* Standard checkbox override */
        input[type="checkbox"]:checked {
            accent-color: #0066CC !important;
        }
        
        /* Force override checked checkbox styling with higher specificity */
        div[data-baseweb="checkbox"]:has(input:checked) span,
        label[data-baseweb="checkbox"]:has(input:checked) span,
        div[data-baseweb="checkbox"] input:checked + span,
        label[data-baseweb="checkbox"] input:checked + span {
            background-color: #0066CC !important;
            border-color: #0066CC !important;
        }
        
        /* Ensure unchecked checkboxes have default styling */
        div[data-baseweb="checkbox"]:not(:has(input:checked)) span,
        label[data-baseweb="checkbox"]:not(:has(input:checked)) span,
        div[data-baseweb="checkbox"] input:not(:checked) + span,
        label[data-baseweb="checkbox"] input:not(:checked) + span {
            background-color: transparent !important;
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
        // Force checkboxes to blue after page load (only checked ones)
        function forceCheckboxBlue() {
            const checkboxes = document.querySelectorAll('[data-baseweb="checkbox"]');
            checkboxes.forEach(function(cb) {
                const input = cb.querySelector('input[type="checkbox"]');
                if (input) {
                    const span = cb.querySelector('span');
                    if (span) {
                        // Apply blue only if checked, transparent if unchecked
                        if (input.checked) {
                            span.style.setProperty('background-color', '#0066CC', 'important');
                            span.style.setProperty('border-color', '#0066CC', 'important');
                        } else {
                            span.style.setProperty('background-color', 'transparent', 'important');
                        }
                    }
                    // Watch for changes
                    input.addEventListener('change', function() {
                        const span = cb.querySelector('span');
                        if (span) {
                            if (this.checked) {
                                span.style.setProperty('background-color', '#0066CC', 'important');
                                span.style.setProperty('border-color', '#0066CC', 'important');
                            } else {
                                span.style.setProperty('background-color', 'transparent', 'important');
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

