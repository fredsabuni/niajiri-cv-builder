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

# Custom CSS - Modern Dark Mode ChatGPT/Claude-inspired design
st.markdown("""
    <style>
        /* Import modern font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
        
        /* Base App Styling - Dark mode like ChatGPT */
        .stApp { 
            background: linear-gradient(180deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #e5e5e5; 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            min-height: 100vh;
        }
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Modern Header with CV Assistant branding - Dark mode */
        .main-header {
            background: #2d2d2d;
            border-bottom: 1px solid #404040;
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }
        
        .header-content {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .app-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #ffffff;
            margin: 0;
        }
        
        .app-subtitle {
            font-size: 0.875rem;
            color: #9ca3af;
            margin: 0;
        }
        
        /* Modern Progress Indicator - Dark mode */
        .progress-container {
            background: #404040;
            border-radius: 8px;
            padding: 12px 16px;
            margin: 16px 0;
            border: 1px solid #e5e7eb;
        }
        
        .progress-bar {
            background: #e5e7eb;
            border-radius: 6px;
            height: 6px;
            overflow: hidden;
            margin: 8px 0;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            height: 100%;
            border-radius: 6px;
            transition: width 0.3s ease;
        }
        
        .progress-text {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.875rem;
            color: #6b7280;
        }
        
        /* Chat Messages - ChatGPT style */
        .stChatMessage {
            background: transparent !important;
            border: none !important;
            padding: 24px 0 !important;
            margin: 0 !important;
        }
        
        .stChatMessage > div {
            max-width: 800px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        /* User/Assistant message styling with readable contrast on dark theme */
        .stChatMessage[data-testid="user-message"],
        .stChatMessage[data-testid="assistant-message"] {
            background: #ffffff !important;
            border-bottom: 1px solid #e5e7eb !important;
            color: #111827 !important;
        }
        .stChatMessage[data-testid="user-message"] *,
        .stChatMessage[data-testid="assistant-message"] * {
            color: #111827 !important;
        }
        
    /* (Chat input styling is now handled by chat_interface to be sticky with no margin) */
        
        /* Floating Action Buttons - Modern design */
        /* Actions toolbar (non-floating) */
        .actions-toolbar { 
            display: flex; 
            gap: 8px; 
            justify-content: center; 
            align-items: center; 
            padding: 8px 0 12px; 
        }
        
        /* Modern button styling */
        .stButton > button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 24px !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            font-family: 'Inter', sans-serif !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
            min-height: 44px !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
            background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        }
        
        /* Content container - proper spacing for fixed chat */
        .main-content {
            padding-bottom: 120px;
            margin: 0;
        }
        
        /* Modern expandable sections - Dark mode */
        .streamlit-expanderHeader {
            background: #404040 !important;
            border: 1px solid #555555 !important;
            border-radius: 8px !important;
            padding: 16px !important;
            font-weight: 500 !important;
            color: #e5e5e5 !important;
        }
        
        .streamlit-expanderContent {
            background: #333333 !important;
            border: 1px solid #555555 !important;
            border-top: none !important;
            border-radius: 0 0 8px 8px !important;
            padding: 20px !important;
            color: #e5e5e5 !important;
        }
        
        /* Modal/Popup styling - Dark mode */
        .modern-modal {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1001;
        }
        
        .modal-content {
            background: #2d2d2d;
            color: #e5e5e5;
            border-radius: 12px;
            padding: 24px;
            max-width: 90vw;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
            animation: modalSlideIn 0.3s ease;
        }
        
        @keyframes modalSlideIn {
            from { opacity: 0; transform: scale(0.9); }
            to { opacity: 1; transform: scale(1); }
        }
        
        /* Content spacing adjustments */
        .main-content {
            padding-bottom: 140px;
            max-width: 800px;
            margin: 0 auto;
            padding-left: 20px;
            padding-right: 20px;
        }
        
    /* (Floating actions removed) */
        
        /* Mobile responsiveness */
        @media (max-width: 768px) {
            .main-header { padding: 1rem; }
            .app-title { font-size: 1.25rem; }
            /* No floating actions on mobile (removed) */
            .main-content { 
                padding-left: 16px; 
                padding-right: 16px; 
                padding-bottom: 120px; 
            }
            .modal-content { 
                margin: 16px; 
                max-width: calc(100vw - 32px); 
            }
        }
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
    if "temp_message" not in st.session_state:
        st.session_state.temp_message = None
    if "temp_message_time" not in st.session_state:
        st.session_state.temp_message_time = None

    conversation_manager = session_manager.conversation_manager
    agent = CVAgent(conversation_manager)
    
    # Load current CV data
    cv_data = load_cv_data()
    
    # Check if all required sections are completed
    required_sections = ["personal_info", "summary", "experience", "education", "skills"]
    completed_required = sum(1 for section in required_sections if has_data_check(cv_data, section))
    all_required_completed = completed_required >= 5
    
    # Handle temporary message cleanup (3 seconds)
    import time
    if st.session_state.temp_message_time and time.time() - st.session_state.temp_message_time > 3:
        st.session_state.temp_message = None
        st.session_state.temp_message_time = None
    
    # Modern Header
    st.markdown("""
        <div class="main-header">
            <div class="header-content">
                <div>
                    <h1 class="app-title">🎯 Niajiri CV Assistant</h1>
                    <p class="app-subtitle">AI-Powered Professional CV Builder</p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Modern Progress Indicator
    progress_sections = ["personal_info", "summary", "experience", "education", "skills"]
    completed_sections = sum(1 for section in progress_sections if has_data_check(cv_data, section))
    progress_percentage = (completed_sections / len(progress_sections)) * 100
    
    # st.markdown(f"""
    #     <div class="progress-container">
    #         <div class="progress-text">
    #             <span>📊 CV Completion Progress</span>
    #             <span><strong>{completed_sections}/{len(progress_sections)} sections</strong></span>
    #         </div>
    #         <div class="progress-bar">
    #             <div class="progress-fill" style="width: {progress_percentage}%"></div>
    #         </div>
    #         <div style="text-align: center; font-size: 0.75rem; color: #9ca3af; margin-top: 4px;">
    #             {progress_percentage:.0f}% Complete
    #         </div>
    #     </div>
        
    #     <!-- Main Content Container -->
    #     <div class="main-content">
    # """, unsafe_allow_html=True)
    
    # Display temporary message if exists
    if st.session_state.temp_message:
        st.error(st.session_state.temp_message)
        st.rerun()  # Auto-refresh to clear message after timeout
    
    # Chat interface with updated CV data tracking (progress tracker)
    cv_data = progress_tracker(agent)
    
    # Initialize welcome message if needed
    if not st.session_state.messages:
        response = agent.start_session(st.session_state.session_id)
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Track message updates
    current_message_count = len(st.session_state.messages)
    if current_message_count > st.session_state.last_message_count:
        st.session_state.update_counter += 1
        st.session_state.last_message_count = current_message_count

    # Display last N chat messages for better mobile performance
    max_messages = 20
    messages_to_show = (
        st.session_state.messages[-max_messages:]
        if len(st.session_state.messages) > max_messages
        else st.session_state.messages
    )
    for message in messages_to_show:
        with st.chat_message(message["role"]):
            content = message["content"]
            if isinstance(content, str) and len(content) > 800:
                st.markdown(content[:800] + "…")
                with st.expander("Show full message"):
                    st.markdown(content)
            else:
                st.markdown(content) 

    # Hidden buttons for functionality (triggered by floating buttons)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👁️", help="Preview CV", key="preview-btn", type="secondary"): 
            st.session_state.show_preview = not st.session_state.show_preview
            st.session_state.show_download = False
            st.session_state.show_improve = False
            st.rerun()
    
    with col2:
        download_help = "Download CV" if all_required_completed else "Complete all mandatory sections first"
        if st.button("📥", help=download_help, key="download-btn", type="secondary"): 
            if all_required_completed:
                st.session_state.show_download = not st.session_state.show_download
                st.session_state.show_preview = False
                st.session_state.show_improve = False
                st.rerun()
            else:
                # Show temporary message
                import time
                st.session_state.temp_message = "Please complete all mandatory sections (Personal Info, Summary, Experience, Education, Skills)"
                st.session_state.temp_message_time = time.time()
                st.rerun()
    
    with col3:
        improve_help = "Improve CV" if all_required_completed else "Complete all mandatory sections first"
        if st.button("🚀", help=improve_help, key="improve-btn", type="secondary"): 
            if all_required_completed:
                st.session_state.show_improve = not st.session_state.show_improve
                st.session_state.show_preview = False
                st.session_state.show_download = False
                st.rerun()
            else:
                # Show temporary message
                import time
                st.session_state.temp_message = "Please complete all mandatory sections (Personal Info, Summary, Experience, Education, Skills)"
                st.session_state.temp_message_time = time.time()
                st.rerun()
    
    # Hide the hidden trigger button columns from layout
    st.markdown("""
        <style>
        [data-testid="column"]:has(button[key="preview-btn"]), 
        [data-testid="column"]:has(button[key="download-btn"]), 
        [data-testid="column"]:has(button[key="improve-btn"]) {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Dynamic CSS for disabled button styling
    if not all_required_completed:
        st.markdown(f"""
            <style>
            button[key="download-btn"], button[key="improve-btn"] {{
                background: #6b7280 !important;
                color: #9ca3af !important;
                cursor: not-allowed !important;
                opacity: 0.6 !important;
            }}
            button[key="download-btn"]:hover, button[key="improve-btn"]:hover {{
                transform: none !important;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
                background: #6b7280 !important;
            }}
            </style>
        """, unsafe_allow_html=True)
    
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

    # Close main content div
    st.markdown('</div>', unsafe_allow_html=True)

    # Sticky, native Streamlit chat input (handled by chat_interface)
    chat_interface(agent)

if __name__ == "__main__":
    main()
