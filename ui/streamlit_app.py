import sys
from pathlib import Path
import json
import os
import io

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import streamlit as st
from agents.cv_agent import CVAgent
from agents.conversation_manager import ConversationManager
from ui.components.chat_interface import chat_interface
from ui.components.progress_tracker import progress_tracker
from utils.session_manager import get_session_manager
from services.pdf_generator import CVPDFGenerator
import streamlit.components.v1 as components

st.set_page_config(page_title="Niajiri CV Building Assistant", layout="centered", initial_sidebar_state="collapsed")

# Custom CSS
st.markdown("""
    <style>
        .stApp { background-color: #3A4040; color: #E0E0E0; height: 100vh; overflow-y: auto; }
        .chat-container { position: fixed; bottom: 0; width: 100%; max-width: 800px; margin: 0 auto; background-color: #2A3030; padding: 10px; border-top: 2px solid #219680; z-index: 1000; }
        .stTextArea textarea { background-color: #219680; color: #FFFFFF; border: 1px solid #1A5C50; border-radius: 5px; font-size: 16px; }
        .stTextArea label { color: #E0E0E0; font-size: 16px; }
        .icon-button { display: inline-flex; align-items: center; justify-content: center; width: 40px; height: 40px; background-color: #219680; color: white; border: 1px solid #1A5C50; border-radius: 50%; margin: 5px; cursor: pointer; font-size: 18px; }
        .icon-button:hover { background-color: #1A5C50; }
        .quick-actions { position: fixed; bottom: 70px; right: 20px; z-index: 1001; display: flex; flex-direction: column; align-items: flex-end; }
        .popup { display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: #2A3030; padding: 20px; border: 2px solid #219680; border-radius: 10px; z-index: 1002; max-height: 80vh; overflow-y: auto; color: #E0E0E0; }
        .popup.active { display: block; }
        .popup-close { position: absolute; top: 10px; right: 10px; cursor: pointer; font-size: 20px; color: #E0E0E0; }
        .overlay { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); z-index: 1001; }
        .overlay.active { display: block; }
        .circular-progress { width: 60px; height: 60px; border: 6px solid #E0E0E0; border-top: 6px solid #219680; border-radius: 50%; animation: spin 1s linear infinite; position: fixed; top: 20px; right: 20px; z-index: 1000; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .progress-text { position: fixed; top: 85px; right: 20px; color: #219680; font-size: 14px; text-align: center; width: 60px; }
        @media (max-width: 768px) { .chat-container { max-width: 100%; padding: 5px; } .stTextArea textarea { font-size: 14px; } .stTextArea label { font-size: 14px; } .icon-button { width: 35px; height: 35px; font-size: 16px; } .quick-actions { right: 10px; bottom: 80px; } .popup { width: 90%; padding: 15px; } .circular-progress { width: 50px; height: 50px; top: 10px; right: 10px; } .progress-text { top: 65px; right: 10px; font-size: 12px; } }
        .stChatMessage { background-color: #2A3030; border-radius: 10px; padding: 10px; color: #E0E0E0; margin-bottom: 5px; }
        .stButton > button { background: linear-gradient(135deg, #219680 0%, #1e7a68 100%); color: white; border: none; border-radius: 12px; padding: 12px 24px; font-size: 16px; font-weight: 500; margin: 5px; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(33, 150, 128, 0.3); min-height: 44px; }
        .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(33, 150, 128, 0.4); background: linear-gradient(135deg, #1e7a68 0%, #196b5b 100%); }
        .stButton > button:active { transform: translateY(0); }
        button[key="preview_btn"], button[key="download_btn"], button[key="improve_btn"] { border-radius: 50% !important; width: 60px !important; height: 60px !important; font-size: 24px !important; padding: 0 !important; }
        div[data-testid="column"]:has(button[key="preview_btn"]), div[data-testid="column"]:has(button[key="download_btn"]), div[data-testid="column"]:has(button[key="improve_btn"]) { position: fixed; bottom: 100px; right: 20px; z-index: 1000; }
        div[data-testid="column"]:has(button[key="download_btn"]) { bottom: 170px; }
        div[data-testid="column"]:has(button[key="improve_btn"]) { bottom: 240px; }
        .stDownloadButton > button { background: linear-gradient(135deg, #059669 0%, #047857 100%); color: white; border: none; border-radius: 12px; padding: 12px 24px; font-size: 16px; font-weight: 500; transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3); }
        .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(5, 150, 105, 0.4); background: linear-gradient(135deg, #047857 0%, #065f46 100%); }
        .stSelectbox > div > div { border-radius: 12px; border: 2px solid #e5e7eb; background: white; color: #1f2937; }
        .stSelectbox > div > div:focus-within { border-color: #219680; box-shadow: 0 0 0 3px rgba(33, 150, 128, 0.1); }
        .streamlit-expanderHeader { background: #f8fafc; border-radius: 12px; border: 1px solid #e5e7eb; }
        .streamlit-expanderContent { background: white; border-radius: 0 0 12px 12px; border: 1px solid #e5e7eb; border-top: none; }
    </style>
""", unsafe_allow_html=True)

def load_cv_data():
    """Centralized function to load CV data using session manager"""
    session_manager = get_session_manager()
    return session_manager.get_cv_data()

def has_data_check(cv_data, section_key):
    """Helper function to check if a section has data"""
    data = cv_data.get(section_key) if cv_data else None
    if data is None:
        return False
    if section_key == "personal_info" and isinstance(data, dict):
        return any(str(v).strip() for v in data.values())
    if section_key == "summary" and isinstance(data, str):
        return bool(data.strip())
    if section_key in ["experience", "education", "projects", "certifications", "references"] and isinstance(data, list):
        return any(any(str(v).strip() for v in item.values()) if isinstance(item, dict) else False for item in data)
    if section_key == "skills" and (isinstance(data, list) or isinstance(data, str)):
        return bool(data.strip()) if isinstance(data, str) else any(str(skill).strip() for skill in data)
    return False

def generate_pdf(cv_data, template="Modern"):
    """Generate PDF using the new professional PDF generator"""
    pdf_generator = CVPDFGenerator()
    return pdf_generator.generate_pdf(cv_data, template)

def improve_cv_data(cv_data, cost_mode="budget"):
    """Improve CV data using AI-powered enhancements with cost optimization"""
    if not cv_data:
        return cv_data
    
    try: 
        from services.openai_service import OpenAIService
        openai_service = OpenAIService(cost_mode=cost_mode)
        
        improved_data = openai_service.improve_cv_comprehensively(cv_data) 
        improved_data = clean_placeholder_text(improved_data)
        
        return improved_data
        
    except Exception as e:
        print(f"AI improvement error: {str(e)}")
        
        improved_data = {key: value.copy() if isinstance(value, dict) else value[:] if isinstance(value, list) else value for key, value in cv_data.items()}
        
        if improved_data.get("summary") and isinstance(improved_data["summary"], str):
            summary = improved_data["summary"].strip()
            if len(summary) < 100: 
                improved_data["summary"] = f"Results-oriented professional with expertise in {summary.lower()}. Committed to delivering high-quality outcomes and driving organizational success."
        
        if improved_data.get("experience") and isinstance(improved_data["experience"], list):
            action_verbs = ["Achieved", "Implemented", "Led", "Managed", "Developed", "Created", "Optimized"]
            for i, exp in enumerate(improved_data["experience"]):
                if exp.get("description") and not any(verb in exp["description"] for verb in action_verbs):
                    exp["description"] = f"{action_verbs[i % len(action_verbs)]} {exp['description'].lower()}"
        
        if improved_data.get("skills") and isinstance(improved_data.get("skills"), str):
            skills_list = [skill.strip().title() for skill in improved_data["skills"].split(",")]
            improved_data["skills"] = skills_list
        
        return improved_data

def clean_placeholder_text(cv_data):
    """Remove placeholder text patterns from AI-generated content"""
    import re
    
    def clean_text(text):
        if not isinstance(text, str):
            return text
        
        placeholder_pattern = r'\[([^\]]*)\]' 
        cleaned = re.sub(placeholder_pattern, '', text)
        
        cleaned = re.sub(r'\s+', ' ', cleaned) 
        cleaned = re.sub(r'\s*,\s*,', ',', cleaned) 
        cleaned = re.sub(r'\s*\.\s*\.', '.', cleaned) 
        cleaned = cleaned.strip()
        
        return cleaned
    
    def clean_dict_or_list(obj):
        if isinstance(obj, dict):
            return {key: clean_dict_or_list(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [clean_dict_or_list(item) for item in obj]
        elif isinstance(obj, str):
            return clean_text(obj)
        else:
            return obj
    
    return clean_dict_or_list(cv_data)

def save_cv_data(session_id, cv_data):
    """Save CV data to session file"""
    session_file = os.path.join("sessions", f"{session_id}.json")
    with open(session_file, 'w') as f:
        json.dump(cv_data, f, indent=4)

def main():
    # Initialize session manager
    session_manager = get_session_manager()
    
    # Initialize session state variables
    if "session_id" not in st.session_state:
        st.session_state.session_id = session_manager.get_session_id()
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "cv_data" not in st.session_state:
        st.session_state.cv_data = {}
    if "template" not in st.session_state:
        st.session_state.template = "Modern"
    if "show_preview" not in st.session_state:
        st.session_state.show_preview = False
    if "show_download" not in st.session_state:
        st.session_state.show_download = False
    if "show_improve" not in st.session_state:
        st.session_state.show_improve = False 
    if "update_counter" not in st.session_state:
        st.session_state.update_counter = 0 
    if "last_message_count" not in st.session_state:
        st.session_state.last_message_count = 0

    conversation_manager = session_manager.conversation_manager
    agent = CVAgent(conversation_manager)

    if not st.session_state.messages:
        response = agent.start_session(st.session_state.session_id)
        st.session_state.messages.append({"role": "assistant", "content": response})

    current_message_count = len(st.session_state.messages)
    if current_message_count > st.session_state.last_message_count:
        st.session_state.update_counter += 1
        st.session_state.last_message_count = current_message_count

    st.markdown("""
    <div style="text-align: center; padding: 15px; margin-bottom: 20px;">
        <h1 style="color: #219680; margin: 0;">🚀 CV Builder</h1>
        <p style="color: #666; margin: 5px 0;">Let's build your professional CV together!</p>
    </div>
    """, unsafe_allow_html=True)
    
    cv_data = progress_tracker(agent)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    chat_interface(agent)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("👁️", help="Preview CV", key="preview_btn"): 
            st.session_state.show_preview = not st.session_state.show_preview
            st.session_state.show_download = False
            st.session_state.show_improve = False
            st.rerun()
    
    with col2:
        if st.button("📥", help="Download CV", key="download_btn"): 
            st.session_state.show_download = not st.session_state.show_download
            st.session_state.show_preview = False
            st.session_state.show_improve = False
            st.rerun()
    
    with col3:
        if st.button("🚀", help="Improve CV", key="improve_btn"): 
            st.session_state.show_improve = not st.session_state.show_improve
            st.session_state.show_preview = False
            st.session_state.show_download = False
            st.rerun()
            
    # This line was overwriting the real-time data from the progress tracker.
    # By removing it, we ensure the UI always reflects the latest session state.
    # cv_data = load_cv_data()

    # Preview Section
    if st.session_state.show_preview:
        if not cv_data:
            st.warning("🔍 No CV data found yet. Start chatting with the assistant to build your CV!")
        else:
            with st.expander("📋 CV Preview", expanded=True):
                st.markdown("### 👁️ Your CV Preview")
                
                # Personal Information
                if cv_data.get("personal_info"):
                    st.markdown("#### 👤 Personal Details")
                    personal = cv_data["personal_info"]
                    if personal.get('name'):
                        st.write(f"**👤 Name:** {personal['name']}")
                    if personal.get('email'):
                        st.write(f"**📧 Email:** {personal['email']}")
                    if personal.get('phone'):
                        st.write(f"**📱 Phone:** {personal['phone']}")
                    if personal.get('location'):
                        st.write(f"**📍 Location:** {personal['location']}")
                    st.divider()
                
                # Professional Summary
                if cv_data.get("summary"):
                    st.markdown("#### 📝 Professional Summary")
                    st.write(cv_data['summary'])
                    st.divider()
                
                # Work Experience
                if cv_data.get("experience"):
                    st.markdown("#### 💼 Work Experience")
                    for exp in cv_data["experience"]:
                        st.write(f"**{exp.get('position', 'Position')}** at **{exp.get('company', 'Company')}**")
                        if exp.get('duration'):
                            st.write(f"📅 {exp['duration']}")
                        if exp.get('description'):
                            st.write(f"📋 {exp['description']}")
                        st.markdown("---")
                    st.divider()
                
                # Education
                if cv_data.get("education"):
                    st.markdown("#### 🎓 Education")
                    for edu in cv_data["education"]:
                        st.write(f"**{edu.get('degree', 'Degree')}**")
                        if edu.get('institution'):
                            st.write(f"🏫 {edu['institution']}")
                        if edu.get('year'):
                            st.write(f"📅 {edu['year']}")
                        if edu.get('grade'):
                            st.write(f"🏆 Grade: {edu['grade']}")
                        st.markdown("---")
                    st.divider()
                
                # Skills
                if cv_data.get("skills"):
                    st.markdown("#### ⚡ Skills")
                    skills = cv_data["skills"]
                    if isinstance(skills, list):
                        for skill in skills:
                            st.write(f"• {skill}")
                    elif isinstance(skills, str):
                        st.write(skills)
                    st.divider()
                
                # Projects
                if cv_data.get("projects"):
                    st.markdown("#### 🚀 Projects")
                    for proj in cv_data["projects"]:
                        st.write(f"**{proj.get('name', 'Project')}**")
                        if proj.get('description'):
                            st.write(f"📝 {proj['description']}")
                        if proj.get('technologies'):
                            st.write(f"🔧 Technologies: {proj['technologies']}")
                        st.markdown("---")
                    st.divider()
                
                # Certifications
                if cv_data.get("certifications"):
                    st.markdown("#### 🏆 Certifications")
                    for cert in cv_data["certifications"]:
                        st.write(f"**{cert.get('name', 'Certification')}**")
                        if cert.get('issuer'):
                            st.write(f"🏢 Issued by: {cert['issuer']}")
                        if cert.get('date'):
                            st.write(f"📅 {cert['date']}")
                        st.markdown("---")
                    st.divider()
                
                # References
                if cv_data.get("references"):
                    st.markdown("#### 👥 References")
                    for ref in cv_data["references"]:
                        st.write(f"**{ref.get('name', 'Reference')}**")
                        if ref.get('position'):
                            st.write(f"💼 {ref['position']}")
                        if ref.get('company'):
                            st.write(f"🏢 {ref['company']}")
                        if ref.get('contact'):
                            st.write(f"📞 {ref['contact']}")
                        st.markdown("---")

    # Download Section
    if st.session_state.show_download:
        if not cv_data:
            st.warning("📥 No CV data available for download. Please build your CV first!")
        else:
            with st.expander("📥 Download Your CV", expanded=True):
                required_sections = ["personal_info", "summary", "experience", "education", "skills"]
                completed_required = sum(1 for section in required_sections if has_data_check(cv_data, section))
                
                if completed_required < 5:
                    st.warning("⚠️ Please complete all required sections before downloading your CV.")
                    missing_sections = [section for section in required_sections if not has_data_check(cv_data, section)]
                    st.error(f"Missing sections: {', '.join(missing_sections)}")
                else:
                    st.markdown("### 🎨 Choose Your Professional CV Template")
                    st.markdown("Select a template that best fits your industry and personal style:")
                    
                    # Template descriptions
                    template_info = {
                        "Modern": {
                            "description": "Clean, contemporary design with accent colors. Perfect for tech, creative, and modern industries.",
                            "features": ["🎨 Modern color scheme", "📐 Clean typography", "💼 Professional layout"],
                            "emoji": "📄"
                        },
                        "Classic": {
                            "description": "Traditional, formal design. Ideal for conservative industries like finance, law, and academia.",
                            "features": ["🏛️ Traditional styling", "📚 Formal typography", "⚖️ Conservative layout"],
                            "emoji": "📋"
                        },
                        "Minimal": {
                            "description": "Ultra-clean, distraction-free design. Great for any industry, focuses on content.",
                            "features": ["✨ Minimalist design", "📖 Easy to read", "🎯 Content-focused"],
                            "emoji": "📝"
                        }
                    }
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"#### {template_info['Modern']['emoji']} Modern Template")
                        st.markdown(template_info['Modern']['description'])
                        for feature in template_info['Modern']['features']:
                            st.markdown(f"• {feature}")
                        st.markdown("---")
                        pdf_buffer = generate_pdf(cv_data, "Modern")
                        st.download_button(
                            label="📄 Download Modern CV",
                            data=pdf_buffer.getvalue(),
                            file_name="CV_Modern.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col2:
                        st.markdown(f"#### {template_info['Classic']['emoji']} Classic Template")
                        st.markdown(template_info['Classic']['description'])
                        for feature in template_info['Classic']['features']:
                            st.markdown(f"• {feature}")
                        st.markdown("---")
                        pdf_buffer = generate_pdf(cv_data, "Classic")
                        st.download_button(
                            label="📋 Download Classic CV",
                            data=pdf_buffer.getvalue(),
                            file_name="CV_Classic.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    with col3:
                        st.markdown(f"#### {template_info['Minimal']['emoji']} Minimal Template")
                        st.markdown(template_info['Minimal']['description'])
                        for feature in template_info['Minimal']['features']:
                            st.markdown(f"• {feature}")
                        st.markdown("---")
                        pdf_buffer = generate_pdf(cv_data, "Minimal")
                        st.download_button(
                            label="📝 Download Minimal CV",
                            data=pdf_buffer.getvalue(),
                            file_name="CV_Minimal.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    
                    st.markdown("---")
                    st.info("💡 **Tip:** Try downloading different templates to see which one best represents your professional image!")

    # Improve Section
    if st.session_state.show_improve:
        if not cv_data:
            st.warning("🚀 No CV data available to improve. Please build your CV first!")
        else:
            with st.expander("🚀 Improve Your CV with AI", expanded=True):
                st.markdown("### ✨ AI-Powered CV Enhancement")
                
                # Cost mode selection
                col_info, col_mode = st.columns([2, 1])
                with col_info:
                    st.markdown("""
                    Our AI-powered enhancement will improve your CV with:
                    - 🤖 **Professional Language**: Industry-standard terminology
                    - 🎯 **Smart Action Verbs**: Powerful, contextual action words  
                    - 🔍 **ATS Optimization**: Better applicant tracking compatibility
                    - � **Cost-Effective**: Optimized for affordability
                    """)
                
                with col_mode:
                    cost_modes = {
                        "ultra_budget": "💰 Ultra Budget (~$0.005)",
                        "budget": "💵 Budget (~$0.008)", 
                        "balanced": "⚖️ Balanced (~$0.012)",
                        "premium": "💎 Premium (~$0.025)"
                    }
                    
                    # Set default cost mode (selectbox hidden)
                    selected_mode = "budget"
                    
                    # selected_mode = st.selectbox(
                    #     "Cost Mode",
                    #     options=list(cost_modes.keys()),
                    #     index=1,   
                    #     format_func=lambda x: cost_modes[x],
                    #     help="Choose your preferred cost/quality balance"
                    # )
                
                # Show cost estimate
                try:
                    from services.openai_service import OpenAIService
                    openai_service = OpenAIService(cost_mode=selected_mode)
                    cost_info = openai_service.get_cost_info()
                    
                    st.info(f"**We use AI to enhance your CV with Niajiri**")
                except Exception as e:
                    st.info("**We use AI to enhance your CV with Niajiri**")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🤖 Enhance CV with AI", key="enhance_action", use_container_width=True):
                        with st.spinner("🤖 AI is analyzing and enhancing your CV... This may take a moment."):
                            # Improve the CV data using AI with selected cost mode
                            improved_cv_data = improve_cv_data(cv_data, cost_mode=selected_mode)
                            
                            # Update session data
                            session_manager = get_session_manager()
                            session_manager.update_cv_data(improved_cv_data)
                            
                            # Update streamlit session state
                            st.session_state.cv_data = improved_cv_data
                            
                            st.success("✅ CV enhanced successfully with AI-powered improvements!")
                            st.balloons()
                            
                            # Show cost information
                            try:
                                openai_service = OpenAIService(cost_mode=selected_mode)
                                session_cost = openai_service.get_session_cost()
                                if session_cost > 0:
                                    st.info(f"💰 Actual cost: ${session_cost} USD")
                                else:
                                    st.info(f"💰 Estimated cost: ~${cost_info['estimated_cost_per_improvement']} USD")
                            except:
                                pass
                            
                            # Show what was improved with more detail
                            improvements = []
                            if improved_cv_data.get("summary") != cv_data.get("summary"):
                                improvements.append("📝 Professional summary enhanced with AI-generated language")
                            if improved_cv_data.get("experience") != cv_data.get("experience"):
                                improvements.append("💼 Experience descriptions improved with AI-powered action verbs and keywords")
                            if improved_cv_data.get("skills") != cv_data.get("skills"):
                                improvements.append("⚡ Skills optimized for ATS compatibility using AI analysis")
                            if improved_cv_data.get("education") != cv_data.get("education"):
                                improvements.append("🎓 Education descriptions professionally enhanced")
                            if improved_cv_data.get("projects") != cv_data.get("projects"):
                                improvements.append("🚀 Project descriptions improved with professional language")
                            
                            if improvements:
                                st.info("**AI Improvements Applied:**\n" + "\n".join(f"• {imp}" for imp in improvements))
                            else:
                                st.info("🎯 Your CV is already well-optimized! No improvements needed.")
                            
                            # Auto-refresh the page to show updated data
                            st.rerun()
                
                with col2:
                    if st.button("📊 Show Enhancement Preview", key="preview_enhancement", use_container_width=True):
                        # Set session state to show preview
                        st.session_state.show_enhancement_preview = True
                        st.rerun()
                
                # Enhancement Preview Section (outside columns to use full width)
                if st.session_state.get("show_enhancement_preview", False):
                    st.markdown("---")
                    st.markdown("#### 🔍 AI Enhancement Preview")
                    
                    # Show summary comparison
                    if cv_data.get("summary"):
                        st.markdown("**📝 Summary Enhancement:**")
                        col_before, col_after = st.columns(2)
                        
                        with col_before:
                            st.markdown("*Before:*")
                            st.text_area("Original Summary", cv_data["summary"], height=100, disabled=True, key="original_summary")
                        
                        with col_after:
                            improved_preview = improve_cv_data(cv_data)
                            st.markdown("*After:*")
                            st.text_area("Enhanced Summary", improved_preview["summary"], height=100, disabled=True, key="enhanced_summary")

                    # Show experience improvement
                    if cv_data.get("experience") and len(cv_data["experience"]) > 0:
                        st.markdown("**💼 Experience Enhancement:**")
                        original_desc = cv_data["experience"][0].get("description", "")
                        if original_desc:
                            col_before_exp, col_after_exp = st.columns(2)
                            
                            with col_before_exp:
                                st.markdown("*Before:*")
                                st.text_area("Original Experience", original_desc, height=80, disabled=True, key="original_experience")
                            
                            with col_after_exp:
                                improved_preview = improve_cv_data(cv_data)
                                enhanced_desc = improved_preview["experience"][0].get("description", "")
                                st.markdown("*After:*")
                                st.text_area("Enhanced Experience", enhanced_desc, height=80, disabled=True, key="enhanced_experience")
                    
                    # Close preview button
                    col_close_left, col_close_center, col_close_right = st.columns([1, 1, 1])
                    with col_close_left:
                        if st.button("❌ Close", key="close_preview", help="Close preview and go back"):
                            st.session_state.show_enhancement_preview = False
                            st.rerun()

if __name__ == "__main__":
    main()
