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
    
    # Compact progress display for mobile
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #219680 0%, #1e7a68 100%); border-radius: 12px; padding: 15px; margin: 15px 0; color: white; box-shadow: 0 4px 15px rgba(33, 150, 128, 0.3);">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <div style="font-size: 18px; font-weight: bold;">📋 CV Progress</div>
                <div style="font-size: 13px; opacity: 0.9;">{completed_count}/{total_sections} sections • Required: {len(completed_required)}/{len(required_sections)} ✅</div>
            </div>
            <div style="font-size: 24px; font-weight: bold;">{progress_percentage}%</div>
        </div>
        <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.2); border-radius: 3px; overflow: hidden;">
            <div style="width: {progress_percentage}%; height: 100%; background: #ffffff; border-radius: 3px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Expandable detailed view
    with st.expander("📝 Section Details", expanded=False):
        st.markdown(f"### ✅ Completion Status ({completed_count}/{total_sections})")
        
        # Mobile-optimized grid layout
        for i in range(0, len(sections), 2):
            col1, col2 = st.columns(2)
            
            # First section
            section = sections[i]
            is_completed = has_section_data(cv_data, section["key"])
            required_text = "Required" if section["required"] else "Optional"
            
            with col1:
                if is_completed:
                    st.markdown(f"""
                    <div style="background-color: #d1e7dd; color: #0f5132; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #198754;">
                        <div style="font-weight: bold; font-size: 14px;">✅ {section['icon']} {section['name']}</div>
                        <div style="font-size: 11px; opacity: 0.8;">Complete ({required_text})</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    color_scheme = "#f8d7da; color: #842029; border-left: 4px solid #dc3545" if section["required"] else "#cff4fc; color: #055160; border-left: 4px solid #0dcaf0"
                    st.markdown(f"""
                    <div style="background-color: {color_scheme}; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <div style="font-weight: bold; font-size: 14px;">📝 {section['icon']} {section['name']}</div>
                        <div style="font-size: 11px; opacity: 0.8;">Pending ({required_text})</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Second section (if exists)
            if i + 1 < len(sections):
                section = sections[i + 1]
                is_completed = has_section_data(cv_data, section["key"])
                required_text = "Required" if section["required"] else "Optional"
                
                with col2:
                    if is_completed:
                        st.markdown(f"""
                        <div style="background-color: #d1e7dd; color: #0f5132; padding: 10px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #198754;">
                            <div style="font-weight: bold; font-size: 14px;">✅ {section['icon']} {section['name']}</div>
                            <div style="font-size: 11px; opacity: 0.8;">Complete ({required_text})</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        color_scheme = "#f8d7da; color: #842029; border-left: 4px solid #dc3545" if section["required"] else "#cff4fc; color: #055160; border-left: 4px solid #0dcaf0"
                        st.markdown(f"""
                        <div style="background-color: {color_scheme}; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                            <div style="font-weight: bold; font-size: 14px;">📝 {section['icon']} {section['name']}</div>
                            <div style="font-size: 11px; opacity: 0.8;">Pending ({required_text})</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Status messages
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
    
    st.session_state.cv_data = cv_data
    
    return cv_data
        
    
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
    
    st.session_state.cv_data = cv_data
    
    return cv_data