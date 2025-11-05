"""
Export Section Component Module

Handles tag generation, Excel export, and download functionality.
"""

import streamlit as st
import os
import tempfile
import hashlib
from datetime import datetime
from src.logic.tag_generator import TagGenerator
from src.logic.exporter import ExcelExporter


def _calculate_selection_hash(customization_service):
    """
    Calculate a hash of current selections and customization settings.
    
    Args:
        customization_service: CustomizationService instance
        
    Returns:
        MD5 hash string of all selections and customization settings
    """
    # Build a hash string that includes selections and all customization settings
    hash_components = [
        str(sorted(st.session_state.selected_locations)),
        str(sorted(st.session_state.selected_analytes)),
        str(sorted(st.session_state.selected_dates)),
    ]
    
    # Add customization settings to hash
    if customization_service:
        # Analyte mappings (sorted for consistency)
        analyte_mappings = customization_service.get_analyte_mappings()
        hash_components.append(str(sorted(analyte_mappings.items())))
        
        # Date format settings
        hash_components.append(customization_service.get_date_format())
        hash_components.append(customization_service.get_date_header_text())
        
        # Tag format options
        hash_components.append(str(customization_service.get_show_non_detect_as_nd()))
        hash_components.append(str(customization_service.get_center_analyte_names()))
        
        # Colors
        hash_components.append(customization_service.get_header_fill_color())
        hash_components.append(customization_service.get_exceedance_fill_color())
        
        # Fonts
        hash_components.append(customization_service.get_font_family())
        hash_components.append(str(customization_service.get_font_size()))
    
    # Create hash from all components
    return hashlib.md5(str(hash_components).encode()).hexdigest()


def render_export_section():
    """
    Render the export section with tag generation and download functionality.
    
    This function handles:
    - Validating selections are ready for export
    - Generating tags when selections or customizations change
    - Exporting tags to Excel
    - Providing download button for the generated Excel file
    """
    st.divider()
    st.subheader("📥 Export Tags")
    
    # Check if selections are ready for export
    if (st.session_state.file_loaded and 
        st.session_state.parser is not None and
        st.session_state.selected_locations and
        st.session_state.selected_analytes and
        st.session_state.selected_dates):
        
        # Validate selections
        can_export = (
            len(st.session_state.selected_locations) > 0 and
            len(st.session_state.selected_analytes) > 0 and
            len(st.session_state.selected_dates) > 0
        )
        
        if can_export:
            # Create a hash of current selections AND customization settings to detect changes
            customization_service = st.session_state.customization_service
            selection_hash = _calculate_selection_hash(customization_service)
            
            # Auto-generate Excel file when selections or customizations change or don't exist
            needs_regeneration = (
                st.session_state.export_excel_bytes is None or
                st.session_state.last_selection_hash != selection_hash
            )
            
            if needs_regeneration:
                try:
                    with st.spinner("⏳ Generating tags..."):
                        # Initialize TagGenerator
                        tag_generator = TagGenerator(
                            st.session_state.parser,
                            st.session_state.customization_service
                        )
                        
                        # Generate tags
                        generated_tags = tag_generator.generate_tags(
                            st.session_state.selected_locations,
                            st.session_state.selected_analytes,
                            st.session_state.selected_dates
                        )
                        
                        if not generated_tags:
                            st.warning("⚠️ No tags were generated. Please check your selections.")
                            st.session_state.export_excel_bytes = None
                            st.session_state.export_filename = None
                            st.session_state.export_tag_count = 0
                            st.session_state.last_selection_hash = selection_hash
                        else:
                            # Initialize ExcelExporter
                            exporter = ExcelExporter(st.session_state.customization_service)
                            
                            # Save to temporary file first (ExcelExporter expects a file path)
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                                tmp_file_path = tmp_file.name
                            
                            # Export to temporary file
                            success = exporter.export_tags(generated_tags, tmp_file_path)
                            
                            if success:
                                # Read the file into bytes
                                with open(tmp_file_path, 'rb') as f:
                                    excel_bytes = f.read()
                                
                                # Clean up temporary file
                                os.unlink(tmp_file_path)
                                
                                # Generate filename
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"tags_{timestamp}.xlsx"
                                
                                # Store in session state
                                st.session_state.export_excel_bytes = excel_bytes
                                st.session_state.export_filename = filename
                                st.session_state.export_tag_count = len(generated_tags)
                                st.session_state.last_selection_hash = selection_hash
                            else:
                                st.error("❌ Failed to export tags to Excel. Please try again.")
                                st.session_state.export_excel_bytes = None
                                st.session_state.export_filename = None
                                st.session_state.export_tag_count = 0
                                st.session_state.last_selection_hash = selection_hash
                                # Clean up temporary file on error
                                if os.path.exists(tmp_file_path):
                                    os.unlink(tmp_file_path)
                
                except Exception as e:
                    st.error(f"❌ Error exporting tags: {str(e)}")
                    st.session_state.export_excel_bytes = None
                    st.session_state.export_filename = None
                    st.session_state.export_tag_count = 0
                    st.session_state.last_selection_hash = selection_hash
                    # Clean up temporary file on error
                    if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                        os.unlink(tmp_file_path)
            
            # Show download button if export is ready
            if st.session_state.export_excel_bytes is not None:
                st.success(f"✅ Ready to download {st.session_state.export_tag_count} tag(s)!")
                st.download_button(
                    label="📥 Download Excel File",
                    data=st.session_state.export_excel_bytes,
                    file_name=st.session_state.export_filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.info("ℹ️ Please make selections for locations, analytes, and dates to export tags.")
    else:
        st.info("ℹ️ Please load a file and make selections to export tags.")

