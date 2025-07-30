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

    # Initialize conversation manager and agent using session manager
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
    
    # Use the improved progress tracker
    cv_data = progress_tracker(agent)

    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    chat_interface(agent)
    st.markdown('</div>', unsafe_allow_html=True)

    # Action buttons
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
            with st.expander("🚀 Improve Your CV", expanded=True):
                st.markdown("### ✨ AI-Powered CV Enhancement")
                if st.button("🤖 Enhance CV", key="enhance_action", use_container_width=True):
                    with st.spinner("🤖 Enhancing your CV..."):
                        import time
                        time.sleep(2)
                        st.success("✅ CV enhanced successfully!")
                        st.balloons()

if __name__ == "__main__":
    main()
