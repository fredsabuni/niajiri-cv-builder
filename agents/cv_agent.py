from typing import Optional, Dict, Tuple
from agents.conversation_manager import ConversationManager, Session
from models.cv_data import CVData
from utils.validators import (
    validate_personal_info,
    validate_education,
    validate_experience,
    validate_project,
    validate_skills,
    validate_certification,
    validate_reference
)
from services.openai_service import OpenAIService
import re
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CVAgent:
    def __init__(self, conversation_manager: ConversationManager):
        self.conversation_manager = conversation_manager
        self.openai_service = OpenAIService()
        self.sections = [
            "personal_info",
            "summary",
            "education",
            "experience",
            "projects",
            "skills",
            "certifications",
            "references"
        ]
        self.repeatable_sections = ["education", "experience", "projects", "certifications", "references"]
        self.section_prompts = {
            "personal_info": "Hello! I’m Niajiri, your CV Building Assistant. Please tell me your personal details (name, email, phone, address). You can type them like: name, email, phone, address (e.g., John Doe, john@example.com, +255712345678, Dar es Salaam), or just describe them naturally if that’s easier.",
            "summary": "Great! Tell me a bit about yourself professionally. For example, say something like 'I’ve worked as a teacher for 3 years' or 'I run a small shop.' Type 'skip' if you’d rather skip this.",
            "education": "Awesome! Let me know about your education or training (e.g., school, course, year). Try: school, course, year, extra details (e.g., University of Dar es Salaam, Certificate in IT, 2020), or describe it naturally. Type 'done' when finished or 'skip' to move on.",
            "experience": "Wonderful! Share your work or activity history (e.g., job, role, start month/year, end month/year or 'now', what you did). Use: company, role, start date, end date, description (e.g., Vodacom, Sales Assistant, 01/2021, now, Helped customers), or describe naturally. Type 'done' when finished or 'skip' to move on.",
            "projects": "Fantastic! Tell me about a project or task you’ve done (e.g., name, what it was, tools used). Try: name, description, tools (e.g., My Shop Website, Online store, WordPress), or describe naturally. Type 'done' when finished or 'skip' to move on.",
            "skills": "Excellent! List any skills you have (e.g., cooking, coding, driving). Just type them like: skill1, skill2, ... or describe them naturally.",
            "certifications": "Amazing! Mention any certificates or awards (e.g., name, who gave it, year). Try: name, issuer, year (e.g., First Aid, Red Cross, 2022), or describe naturally. Type 'done' when finished or 'skip' to move on.",
            "references": "Perfect! Add someone who can vouch for you (e.g., name, contact, how they know you). Use: name, contact, relationship (e.g., Amina Hassan, amina@example.com, Boss), or describe naturally. Type 'done' when finished or 'skip' to move on."
        }

    def start_session(self, session_id: str) -> str:
        session = self.conversation_manager.load_session(session_id)
        if not session:
            session = self.conversation_manager.create_session(session_id)
            welcome_message = "Karibu! I’m Niajiri, your CV Building Assistant, here to help everyone—tech or non-tech, formal or informal jobs—create a great CV. Let’s start! You can use the formats I suggest or just chat naturally."
            self.conversation_manager.add_message("assistant", welcome_message)
            self.conversation_manager.set_current_section(self.sections[0])
            self.conversation_manager.current_session = session
            self.conversation_manager.save_session(session_id)
            return f"{welcome_message}\n\n{self.section_prompts[self.sections[0]]}"
        else:
            current_section = session.current_section or self.sections[0]
            resume_message = f"Welcome back! I’m Niajiri—let’s continue with {current_section.replace('_', ' ').title()}."
            self.conversation_manager.add_message("assistant", resume_message)
            self.conversation_manager.current_session = session
            self.conversation_manager.save_session(session_id)
            return f"{resume_message}\n\n{self.section_prompts[current_section]}"

    def process_input(self, session_id: str, user_input: str) -> str:
        session = self.conversation_manager.load_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        self.conversation_manager.current_session = session
        self.conversation_manager.add_message("user", user_input)
        current_section = session.current_section or self.sections[0]
        cv_data = self.conversation_manager.get_cv_data()

        # Recognize greetings and respond warmly
        if re.match(r"^(hello|hi|hey|good morning|good afternoon|karibu)", user_input.lower()):
            return f"Nice to hear from you! I’m Niajiri—{self.section_prompts[current_section]}"

        # Handle post-completion input
        if not current_section:
            if user_input.lower() == "yes":
                return "Great! You can review your CV by clicking 'Review CV', export it by selecting a template and clicking 'Export to PDF', or get an improved version by typing 'improve'."
            elif user_input.lower() == "improve":
                improved_cv = self._generate_improved_cv(cv_data)
                self.conversation_manager.update_cv_data(improved_cv)
                return "Here’s an improved version of your CV based on your details:\n" + self.format_improved_cv(improved_cv) + "\nWould you like to review, export, or adjust it further?"

        response, success, advance = self._handle_section_input(current_section, user_input, cv_data)
        
        if success and advance:
            current_index = self.sections.index(current_section) if current_section else -1
            if current_index < len(self.sections) - 1 and current_section:
                next_section = self.sections[current_index + 1]
                self.conversation_manager.set_current_section(next_section)
                response += f"\n\n{self.section_prompts[next_section]}"
            else:
                response += "\n\nAll sections complete! Your CV is ready. Would you like to review, export, or get an improved version?"
                self.conversation_manager.set_current_section(None)
        elif success and not advance and current_section in self.repeatable_sections:
            response += f"\n\n{self.section_prompts[current_section]}"
        else:
            response += f"\n\n{self.section_prompts[current_section]}"

        self.conversation_manager.add_message("assistant", response)
        self.conversation_manager.save_session(session_id)
        return response

    def _handle_section_input(self, section: str, input: str, cv_data: CVData) -> tuple[str, bool, bool]:
        logger.debug(f"Handling section input for {section}: '{input}'")
        
        if input.lower() in ["skip", "done"] and section in self.repeatable_sections:
            if input.lower() == "skip":
                return f"{section.replace('_', ' ').title()} skipped, retaining existing data.", True, True
            return f"{section.replace('_', ' ').title()} entries completed.", True, True

        structured_response, structured_success, advance = self._process_structured_input(section, input, cv_data)
        logger.debug(f"Structured input result: success={structured_success}, response='{structured_response[:100]}...'")
        
        if structured_success:
            return structured_response, True, advance

        parsed_data, error = self.openai_service.parse_natural_language(input, section)
        logger.debug(f"OpenAI parsing result for {section}: parsed_data={parsed_data}, error='{error}'")
        
        if parsed_data and not error:
            # Contextual validation for each section
            if section == "summary" and not self._is_valid_summary(parsed_data.get("summary", "")):
                return "That doesn’t sound like a professional summary. Please share a bit about your work or skills (e.g., 'I’ve been a teacher for 3 years' or 'I sell clothes').", False, False
            elif section == "education" and not self._is_valid_education(parsed_data):
                return "That doesn’t seem like a valid education or training entry. Please include a school or course and year (e.g., 'Vocational Training, Carpentry, 2019').", False, False
            elif section == "experience" and not self._is_valid_experience(parsed_data):
                return "That doesn’t seem like a valid work or activity. Please include where you worked, what you did, and when (e.g., 'Market Stall, Vendor, 2022, now').", False, False
            elif section == "projects" and not self._is_valid_project(parsed_data):
                return "That doesn’t seem like a valid project. Please include a name and what it was (e.g., 'My Shop, Selling goods').", False, False
            elif section == "skills" and not self._is_valid_skills(parsed_data.get("skills", [])):
                return "That doesn’t seem like a valid skill list. Please list at least one skill (e.g., 'cooking, sewing').", False, False
            elif section == "certifications" and not self._is_valid_certification(parsed_data):
                return "That doesn’t seem like a valid certificate. Please include a name and when you got it (e.g., 'Driving License, 2021').", False, False
            elif section == "references" and not self._is_valid_reference(parsed_data):
                return "That doesn’t seem like a valid reference. Please include a name and how to reach them (e.g., 'John, john@example.com').", False, False
            response, success = self._process_parsed_data(section, parsed_data, cv_data)
            advance = section not in self.repeatable_sections
            return response, success, advance

        return f"{error or 'Oops! I didn’t understand that. Please use the format I suggested or describe it naturally—I’m here to help!'}", False, False

    def _process_structured_input(self, section: str, input: str, cv_data: CVData) -> tuple[str, bool, bool]:
        try:
            if section == "personal_info":
                name, email, phone, *address = [part.strip() for part in input.split(",")]
                address = address[0] if address else ""
                is_valid, error = validate_personal_info(name, email, phone, address)
                if not is_valid:
                    return error, False, False
                cv_data.add_personal_info(name, email, phone, address)
                return "Personal information added successfully! Let’s move forward.", True, True
            
            elif section == "summary":
                if not self._is_valid_summary(input.strip()):
                    return "That doesn’t sound like a professional summary. Please share a bit about your work or skills (e.g., 'I’ve been a teacher for 3 years' or 'I sell clothes').", False, False
                enhanced_summary = self.openai_service.enhance_summary(input.strip())
                cv_data.add_summary(enhanced_summary)
                return f"Summary added successfully: {enhanced_summary}. Great job!", True, True
            
            elif section in self.repeatable_sections:
                if section == "education":
                    institution, degree, year, *details = [part.strip() for part in input.split(",")]
                    details = details[0] if details else ""
                    is_valid, error = validate_education(institution, degree, year, details)
                    if not is_valid:
                        return error, False, False
                    cv_data.add_education(institution, degree, year, details)
                    return "Education entry added successfully! Add another or type 'done' to finish.", True, False
                
                elif section == "experience":
                    parts = [part.strip() for part in input.split(",")]
                    logger.debug(f"Experience input parts: {parts}")
                    
                    if len(parts) < 5:
                        return f"Experience needs 5 parts: company, role, start date, end date, description. You provided {len(parts)} parts. Please try: Vodacom, Sales Assistant, 01/2021, now, Helped customers", False, False
                    
                    company, role, start_date, end_date = parts[:4]
                    description = ", ".join(parts[4:])  # Join remaining parts as description
                    
                    logger.debug(f"Parsed experience: company='{company}', role='{role}', start_date='{start_date}', end_date='{end_date}', description='{description}'")
                    
                    is_valid, error = validate_experience(company, role, start_date, end_date, description)
                    if not is_valid:
                        logger.debug(f"Validation failed: {error}")
                        return error, False, False
                    cv_data.add_experience(company, role, start_date, end_date, description)
                    return "Experience entry added successfully! Add another or type 'done' to finish.", True, False
                
                elif section == "projects":
                    name, description, *technologies = [part.strip() for part in input.split(",")]
                    technologies = technologies[0] if technologies else ""
                    is_valid, error = validate_project(name, description, technologies)
                    if not is_valid:
                        return error, False, False
                    cv_data.add_project(name, description, technologies)
                    return "Project entry added successfully! Add another or type 'done' to finish.", True, False
                
                elif section == "certifications":
                    name, issuer, year = [part.strip() for part in input.split(",")]
                    is_valid, error = validate_certification(name, issuer, year)
                    if not is_valid:
                        return error, False, False
                    cv_data.add_certification(name, issuer, year)
                    return "Certification added successfully! Add another or type 'done' to finish.", True, False
                
                elif section == "references":
                    name, contact, *relationship = [part.strip() for part in input.split(",")]
                    relationship = relationship[0] if relationship else ""
                    is_valid, error = validate_reference(name, contact, relationship)
                    if not is_valid:
                        return error, False, False
                    cv_data.add_reference(name, contact, relationship)
                    return "Reference entry added successfully! Add another or type 'done' to finish.", True, False
            
            elif section == "skills":
                skills = [skill.strip() for skill in input.split(",") if skill.strip()]
                if not skills:
                    return "Please provide at least one skill.", False, False
                is_valid, error = validate_skills(skills)
                if not is_valid:
                    return error, False, False
                for skill in skills:
                    cv_data.add_skill(skill)
                return "Skills added successfully! Looking good!", True, True
            
        except ValueError as e:
            logger.debug(f"ValueError in structured input for {section}: {e}")
            return f"Invalid format for {section.replace('_', ' ').title()}. Please check the format: {self.section_prompts[section]}", False, False
        except Exception as e:
            logger.error(f"Unexpected error in structured input for {section}: {e}")
            return f"Error processing {section.replace('_', ' ').title()}. Please try the suggested format or describe naturally.", False, False
        return "Unknown section.", False, False

    def _process_parsed_data(self, section: str, parsed_data: Dict, cv_data: CVData) -> Tuple[str, bool]:
        if section == "personal_info":
            is_valid, error = validate_personal_info(
                parsed_data.get("name", ""),
                parsed_data.get("email", ""),
                parsed_data.get("phone", ""),
                parsed_data.get("address", "")
            )
            if not is_valid:
                return error, False
            cv_data.add_personal_info(
                parsed_data["name"],
                parsed_data["email"],
                parsed_data["phone"],
                parsed_data["address"]
            )
            return "Personal information added successfully! Let’s move forward.", True
        
        elif section == "summary":
            if not self._is_valid_summary(parsed_data.get("summary", "")):
                return "That doesn’t sound like a professional summary. Please share a bit about your work or skills (e.g., 'I’ve been a teacher for 3 years' or 'I sell clothes').", False, False
            enhanced_summary = self.openai_service.enhance_summary(parsed_data.get("summary", ""))
            cv_data.add_summary(enhanced_summary)
            return f"Summary added successfully: {enhanced_summary}. Great job!", True
        
        elif section in self.repeatable_sections:
            if section == "education":
                is_valid, error = validate_education(
                    parsed_data.get("institution", ""),
                    parsed_data.get("degree", ""),
                    parsed_data.get("year", ""),
                    parsed_data.get("details", "")
                )
                if not is_valid:
                    return error, False
                cv_data.add_education(
                    parsed_data["institution"],
                    parsed_data["degree"],
                    parsed_data["year"],
                    parsed_data.get("details", "")
                )
                return "Education entry added successfully! Add another or type 'done' to finish.", True
            
            elif section == "experience":
                is_valid, error = validate_experience(
                    parsed_data.get("company", ""),
                    parsed_data.get("role", ""),
                    parsed_data.get("start_date", ""),
                    parsed_data.get("end_date", ""),
                    parsed_data.get("description", "")
                )
                if not is_valid:
                    return error, False
                cv_data.add_experience(
                    parsed_data["company"],
                    parsed_data["role"],
                    parsed_data["start_date"],
                    parsed_data["end_date"],
                    parsed_data["description"]
                )
                return "Experience entry added successfully! Add another or type 'done' to finish.", True
            
            elif section == "projects":
                is_valid, error = validate_project(
                    parsed_data.get("name", ""),
                    parsed_data.get("description", ""),
                    parsed_data.get("technologies", "")
                )
                if not is_valid:
                    return error, False
                cv_data.add_project(
                    parsed_data["name"],
                    parsed_data["description"],
                    parsed_data.get("technologies", "")
                )
                return "Project entry added successfully! Add another or type 'done' to finish.", True
            
            elif section == "certifications":
                is_valid, error = validate_certification(
                    parsed_data.get("name", ""),
                    parsed_data.get("issuer", ""),
                    parsed_data.get("year", "")
                )
                if not is_valid:
                    return error, False
                cv_data.add_certification(
                    parsed_data["name"],
                    parsed_data["issuer"],
                    parsed_data["year"]
                )
                return "Certification added successfully! Add another or type 'done' to finish.", True
            
            elif section == "references":
                is_valid, error = validate_reference(
                    parsed_data.get("name", ""),
                    parsed_data.get("contact", ""),
                    parsed_data.get("relationship", "")
                )
                if not is_valid:
                    return error, False
                cv_data.add_reference(
                    parsed_data["name"],
                    parsed_data["contact"],
                    parsed_data.get("relationship", "")
                )
                return "Reference entry added successfully! Add another or type 'done' to finish.", True
        
        elif section == "skills":
            skills = parsed_data.get("skills", [])
            if not skills:
                return "No skills provided. Please list at least one skill.", False
            is_valid, error = validate_skills(skills)
            if not is_valid:
                return error, False
            for skill in skills:
                cv_data.add_skill(skill)
            return "Skills added successfully! Looking good!", True
        
        return "Unknown section.", False

    def _is_valid_summary(self, text: str) -> bool:
        """Check if the text resembles a professional summary for any background."""
        if not text or len(text.split()) < 3:
            return False
        work_terms = ["work", "job", "experience", "skilled", "years", "run", "sell", "teach"]
        return any(term in text.lower() for term in work_terms)

    def _is_valid_education(self, data: Dict) -> bool:
        return bool(data.get("institution") or data.get("degree") and data.get("year"))

    def _is_valid_experience(self, data: Dict) -> bool:
        return bool(data.get("company") or data.get("role") and (data.get("start_date") or data.get("description")))

    def _is_valid_project(self, data: Dict) -> bool:
        return bool(data.get("name") and data.get("description"))

    def _is_valid_skills(self, skills: list) -> bool:
        return bool(skills and all(s.strip() for s in skills))

    def _is_valid_certification(self, data: Dict) -> bool:
        return bool(data.get("name") and (data.get("issuer") or data.get("year")))

    def _is_valid_reference(self, data: Dict) -> bool:
        return bool(data.get("name") and data.get("contact"))

    def _generate_improved_cv(self, cv_data: CVData) -> CVData:
        """Generate an improved CV by enhancing details using the cost-optimized OpenAI service."""
        try:
            # Convert CVData to dictionary format for the OpenAI service
            cv_dict = {
                "personal_info": cv_data.personal_info,
                "summary": cv_data.summary,
                "education": cv_data.education,
                "experience": cv_data.experience,
                "projects": cv_data.projects,
                "skills": cv_data.skills,
                "certifications": cv_data.certifications,
                "references": cv_data.references
            }
            
            # Use the cost-optimized comprehensive improvement
            improved_dict = self.openai_service.improve_cv_comprehensively(cv_dict)
            
            # Convert back to CVData format
            improved_data = CVData()
            if improved_dict.get("personal_info"):
                improved_data.personal_info = improved_dict["personal_info"]
            if improved_dict.get("summary"):
                improved_data.add_summary(improved_dict["summary"])
            
            # Add improved education entries
            for edu in improved_dict.get("education", []):
                improved_data.add_education(
                    edu.get("institution", ""),
                    edu.get("degree", ""),
                    edu.get("year", ""),
                    edu.get("details", "")
                )
            
            # Add improved experience entries
            for exp in improved_dict.get("experience", []):
                improved_data.add_experience(
                    exp.get("company", ""),
                    exp.get("role", ""),
                    exp.get("start_date", ""),
                    exp.get("end_date", ""),
                    exp.get("description", "")
                )
            
            # Add improved project entries
            for proj in improved_dict.get("projects", []):
                improved_data.add_project(
                    proj.get("name", ""),
                    proj.get("description", ""),
                    proj.get("technologies", "")
                )
            
            # Add skills (improved)
            for skill in improved_dict.get("skills", []):
                improved_data.add_skill(skill)
            
            # Add certifications
            for cert in improved_dict.get("certifications", []):
                improved_data.add_certification(
                    cert.get("name", ""),
                    cert.get("issuer", ""),
                    cert.get("year", "")
                )
            
            # Add references (unchanged)
            for ref in improved_dict.get("references", []):
                improved_data.add_reference(
                    ref.get("name", ""),
                    ref.get("contact", ""),
                    ref.get("relationship", "")
                )
            
            return improved_data
            
        except Exception as e:
            logger.error(f"Error generating improved CV: {e}")
            # Return original data if improvement fails
            return cv_data

    def format_improved_cv(self, cv_data: CVData) -> str:
        """Format the improved CV as a string for display."""
        result = "Improved CV by Niajiri:\n"
        if cv_data.personal_info:
            result += f"Personal Info: {cv_data.personal_info['name']}, {cv_data.personal_info['email']}, {cv_data.personal_info['phone']}, {cv_data.personal_info['address']}\n"
        if cv_data.summary:
            result += f"Summary: {cv_data.summary}\n"
        if cv_data.education:
            result += "Education:\n" + "\n".join([f"- {entry['institution']}, {entry['degree']}, {entry['year']}, {entry['details']}" for entry in cv_data.education]) + "\n"
        if cv_data.experience:
            result += "Experience:\n" + "\n".join([f"- {entry['company']}, {entry['role']}, {entry['start_date']} - {entry['end_date']}, {entry['description']}" for entry in cv_data.experience]) + "\n"
        if cv_data.projects:
            result += "Projects:\n" + "\n".join([f"- {entry['name']}: {entry['description']}, {entry.get('technologies', '')}" for entry in cv_data.projects]) + "\n"
        if cv_data.skills:
            result += f"Skills: {', '.join(cv_data.skills)}\n"
        if cv_data.certifications:
            result += "Certifications:\n" + "\n".join([f"- {entry['name']}, {entry['issuer']}, {entry['year']}" for entry in cv_data.certifications]) + "\n"
        if cv_data.references:
            result += "References:\n" + "\n".join([f"- {entry['name']}, {entry['contact']}, {entry.get('relationship', '')}" for entry in cv_data.references]) + "\n"
        return result

    def get_current_section(self, session_id: str) -> Optional[str]:
        session = self.conversation_manager.load_session(session_id)
        return session.current_section if session else None