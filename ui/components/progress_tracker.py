import streamlit as st
import json
import os
from typing import Dict, Any
from utils.session_manager import get_session_manager

def load_session_data(session_id: str) -> Dict[str, Any]:
    """Load CV data from session file using centralized session manager"""
    session_manager = get_session_manager()
    return session_manager.load_session_data(session_id)

def has_section_data(cv_data: Dict[str, Any], section_key: str) -> bool:
    """Check if a CV section has meaningful data"""
    session_manager = get_session_manager()
    return session_manager.has_section_data(cv_data, section_key)

def progress_tracker(agent):
    """Display progress tracking for CV completion using centralized session management."""
    session_manager = get_session_manager()
    session_id = session_manager.get_session_id()
    
    # Load CV data using centralized session manager
    cv_data = session_manager.get_cv_data(session_id)
    
    # Define sections with metadata
    sections = [
        {"key": "personal_info", "name": "Personal Details", "icon": "👤", "required": True},
        {"key": "summary", "name": "Professional Summary", "icon": "📝", "required": True},
        {"key": "experience", "name": "Work Experience", "icon": "💼", "required": True},
        {"key": "education", "name": "Education", "icon": "🎓", "required": True},
        {"key": "skills", "name": "Skills", "icon": "⚡", "required": True},
        {"key": "projects", "name": "Projects", "icon": "🚀", "required": False},
        {"key": "certifications", "name": "Certifications", "icon": "🏆", "required": False},
        {"key": "references", "name": "References", "icon": "👥", "required": False},
    ]
    
    # Calculate progress
    completed_sections = [s for s in sections if has_section_data(cv_data, s["key"])]
    total_sections = len(sections)
    completed_count = len(completed_sections)
    progress_percentage = int((completed_count / total_sections) * 100)
    
    # Required sections progress
    required_sections = [s for s in sections if s["required"]]
    completed_required = [s for s in completed_sections if s["required"]]
    required_progress = len(completed_required) / len(required_sections) if required_sections else 0
    
    # Main progress display
    if completed_count == 0:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #219680 0%, #1e7a68 100%); border-radius: 15px; padding: 20px; margin: 20px 0; color: white; text-align: center; box-shadow: 0 4px 15px rgba(33, 150, 128, 0.3);">
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">📋 Your CV Progress</div>
            <div style="font-size: 36px; font-weight: bold; margin: 15px 0;">0%</div>
            <div style="font-size: 16px; opacity: 0.9;">0 of 8 sections completed</div>
            <div style="font-size: 14px; opacity: 0.8; margin-top: 10px;">🚀 Ready to start? Just chat with me!</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #219680 0%, #1e7a68 100%); border-radius: 15px; padding: 20px; margin: 20px 0; color: white; text-align: center; box-shadow: 0 4px 15px rgba(33, 150, 128, 0.3);">
            <div style="font-size: 24px; font-weight: bold; margin-bottom: 10px;">📋 Your CV Progress</div>
            <div style="font-size: 36px; font-weight: bold; margin: 15px 0;">{progress_percentage}%</div>
            <div style="font-size: 16px; opacity: 0.9;">{completed_count} of {total_sections} sections completed</div>
            <div style="font-size: 14px; opacity: 0.8; margin-top: 10px;">Required: {len(completed_required)}/{len(required_sections)} ✅</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bar
    st.progress(progress_percentage / 100)
    
    # Expandable detailed view
    with st.expander("📝 Section Details", expanded=(completed_count < 3)):
        st.markdown(f"### ✅ Completion Status ({completed_count}/{total_sections})")
        
        # Create two columns for better layout
        col1, col2 = st.columns(2)
        
        for i, section in enumerate(sections):
            column = col1 if i % 2 == 0 else col2
            
            with column:
                is_completed = has_section_data(cv_data, section["key"])
                required_text = "Required" if section["required"] else "Optional"
                
                if is_completed:
                    st.markdown(f"""
                    <div style="background-color: #d1e7dd; color: #0f5132; padding: 12px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #198754;">
                        <div style="font-weight: bold;">✅ {section['icon']} {section['name']}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Complete ({required_text})</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    color_scheme = "#f8d7da; color: #842029; border-left: 4px solid #dc3545" if section["required"] else "#cff4fc; color: #055160; border-left: 4px solid #0dcaf0"
                    st.markdown(f"""
                    <div style="background-color: {color_scheme}; padding: 12px; border-radius: 8px; margin-bottom: 10px;">
                        <div style="font-weight: bold;">📝 {section['icon']} {section['name']}</div>
                        <div style="font-size: 12px; opacity: 0.8;">Pending ({required_text})</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Quick navigation buttons
        st.markdown("---")
        st.markdown("#### 🎯 Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if len(completed_required) < len(required_sections):
                next_required = next((s for s in sections if s["required"] and not has_section_data(cv_data, s["key"])), None)
                if next_required:
                    if st.button(f"📝 Complete {next_required['name']}", use_container_width=True):
                        st.info(f"💬 Tell me about your {next_required['name'].lower()} in the chat below!")
        
        with col2:
            if completed_count > 0:
                if st.button("👁️ Preview CV", use_container_width=True):
                    st.session_state.show_preview = True
                    st.session_state.show_download = False
                    st.session_state.show_improve = False
                    st.rerun()
        
        with col3:
            if len(completed_required) == len(required_sections):
                if st.button("📥 Download CV", use_container_width=True):
                    st.session_state.show_download = True
                    st.session_state.show_preview = False
                    st.session_state.show_improve = False
                    st.rerun()
    
    # Motivational messages
    if completed_count == 0:
        st.info("🚀 **Let's get started!** Just tell me about yourself and I'll help build your professional CV.")
    elif len(completed_required) < len(required_sections):
        remaining = len(required_sections) - len(completed_required)
        st.warning(f"⚠️ **{remaining} required section{'s' if remaining > 1 else ''} remaining!** These are essential for your CV.")
    elif completed_count < total_sections:
        remaining = total_sections - completed_count
        st.info(f"🎯 **Almost perfect!** Just {remaining} optional section{'s' if remaining > 1 else ''} left to make your CV even better.")
    else:
        st.success("🎉 **Congratulations!** Your CV is complete with all 8 sections and ready to download!")
        st.balloons()
    
    # Ensure session state is synchronized with the latest CV data
    st.session_state.cv_data = cv_data
    
    return cv_data