from typing import Optional, Dict, Tuple
from agents.conversation_manager import ConversationManager, Session
from models.cv_data import CVData
from utils.validators import (
    validate_personal_info,
    validate_summary,
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
            welcome_message = "Karibu!"
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
        """Handle input for any section using AI-first approach with structured fallback."""
        logger.debug(f"Handling section input for {section}: '{input}'")
        
        if input.lower() in ["skip", "done"]:
            return self._handle_control_commands(section, input.lower())
        
        try:
            ai_analysis = self._analyze_input_with_ai(input, section, cv_data)
            
            # Process based on AI analysis
            if ai_analysis["intent"] == "update_previous":
                return self._handle_previous_section_update(ai_analysis, cv_data)
            elif ai_analysis["intent"] == "current_section":
                return self._handle_current_section_input(section, ai_analysis, cv_data)
            else:
                # General chat or unclear - ask for clarification
                return self._handle_unclear_input(section, ai_analysis)
                
        except Exception as e:
            logger.error(f"Error in AI analysis for {section}: {e}")
            return self._fallback_to_structured_processing(section, input, cv_data)

    def _handle_control_commands(self, section: str, command: str) -> tuple[str, bool, bool]:
        """Handle skip/done commands."""
        if command == "skip":
            if section in self.repeatable_sections:
                return f"{section.replace('_', ' ').title()} skipped. Let's move on!", True, True
            else:
                return f"{section.replace('_', ' ').title()} skipped.", True, True
        elif command == "done":
            if section in self.repeatable_sections:
                return f"{section.replace('_', ' ').title()} entries completed. Moving forward!", True, True
            else:
                return "Got it! Moving to the next section.", True, True
        return "Unknown command.", False, False

    def _analyze_input_with_ai(self, user_input: str, current_section: str, cv_data: CVData) -> Dict:
        """Use OpenAI to analyze the input and determine intent and data extraction."""
        
        cv_context = self._build_cv_context(cv_data)
        
        analysis_prompt = f"""
You are Niajiri, a smart CV building assistant. Analyze the user's input and determine:

1. Intent: Is this for the current section, updating a previous section, or unclear?
2. Extract relevant data from the input
3. Provide an appropriate response

Current CV state:
{cv_context}

Current section we're working on: {current_section}
Section description: {self.section_prompts[current_section]}

User input: "{user_input}"

Respond in JSON format:
{{
    "intent": "current_section" | "update_previous" | "unclear",
    "target_section": "section_name_if_updating_previous_or_current",
    "extracted_data": {{
        "field_name": "value"
    }},
    "confidence": 0.0-1.0,
    "response_message": "Your response to the user",
    "should_advance": true/false,
    "validation_notes": "Any concerns about the data quality"
}}

Guidelines:
- If user provides personal info (phone/email/address) while in other sections and personal_info is incomplete, set intent to "update_previous"
- If input clearly answers the current section question, set intent to "current_section"
- If input is unclear or off-topic, set intent to "unclear"
- Be encouraging and conversational
- For repeatable sections (education, experience, projects, certifications, references), set should_advance to false unless they explicitly say "done"
- Extract data in the expected format for each section
"""

        try:
            response = self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.3,
                max_tokens=600
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            logger.debug(f"AI analysis result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                "intent": "current_section",
                "target_section": current_section,
                "extracted_data": {},
                "confidence": 0.0,
                "response_message": f"I'll help you with {current_section.replace('_', ' ')}. {self.section_prompts[current_section]}",
                "should_advance": False,
                "validation_notes": "AI analysis failed, using fallback"
            }

    def _handle_previous_section_update(self, ai_analysis: Dict, cv_data: CVData) -> tuple[str, bool, bool]:
        """Handle updates to previous sections."""
        target_section = ai_analysis["target_section"]
        extracted_data = ai_analysis["extracted_data"]
        
        update_success = self._update_section_with_data(target_section, extracted_data, cv_data)
        
        if update_success:
            response = ai_analysis["response_message"]
            return response, True, False   
        else:
            return f"I had trouble updating your {target_section.replace('_', ' ')}. {ai_analysis['response_message']}", False, False

    def _handle_current_section_input(self, section: str, ai_analysis: Dict, cv_data: CVData) -> tuple[str, bool, bool]:
        """Handle input for the current section."""
        extracted_data = ai_analysis["extracted_data"]
        confidence = ai_analysis.get("confidence", 0.0)
        
        if confidence < 0.6:
            return self._ask_for_clarification(section, ai_analysis)
        
        if extracted_data:
            update_success = self._update_section_with_data(section, extracted_data, cv_data)
            if update_success:
                response = ai_analysis["response_message"]
                should_advance = ai_analysis.get("should_advance", section not in self.repeatable_sections)
                return response, True, should_advance
            else:
                return f"I had some trouble with that information. {self.section_prompts[section]}", False, False
        else:
            return ai_analysis["response_message"], False, False

    def _handle_unclear_input(self, section: str, ai_analysis: Dict) -> tuple[str, bool, bool]:
        """Handle unclear or off-topic input."""
        response = ai_analysis.get("response_message", 
            f"I'm not sure I understand. Let's focus on {section.replace('_', ' ')}. {self.section_prompts[section]}")
        return response, False, False

    def _ask_for_clarification(self, section: str, ai_analysis: Dict) -> tuple[str, bool, bool]:
        """Ask for clarification when confidence is low."""
        clarification_prompts = {
            "personal_info": "I want to make sure I get your details right. Could you provide your name, email, phone, and address more clearly?",
            "summary": "I would like to better understand your professional background. Could you tell me more about your work experience or main skills?",
            "education": "I want to capture your education correctly. Could you tell me the school/institution, what you studied, and when?",
            "experience": "I want to record your work experience properly. Could you share the company/place, your role, when you worked there, and what you did?",
            "projects": "I would like to understand your project better. Could you tell me the project name, what it involved, and any tools/skills used?",
            "skills": "I want to list your skills clearly. Could you tell me what specific skills you have?",
            "certifications": "I want to record your certification properly. Could you share the certificate name, who issued it, and when?",
            "references": "I want to get your reference details right. Could you provide their name, contact information, and how they know you?"
        }
        
        base_message = ai_analysis.get("response_message", "")
        clarification = clarification_prompts.get(section, f"Could you provide more details about your {section.replace('_', ' ')}?")
        
        return f"{base_message} {clarification}", False, False

    def _update_section_with_data(self, section: str, data: Dict, cv_data: CVData) -> bool:
        """Universal method to update any section with extracted data."""
        try:
            if section == "personal_info":
                return self._update_personal_info(data, cv_data)
            elif section == "summary":
                return self._update_summary(data, cv_data)
            elif section == "education":
                return self._update_education(data, cv_data)
            elif section == "experience":
                return self._update_experience(data, cv_data)
            elif section == "projects":
                return self._update_projects(data, cv_data)
            elif section == "skills":
                return self._update_skills(data, cv_data)
            elif section == "certifications":
                return self._update_certifications(data, cv_data)
            elif section == "references":
                return self._update_references(data, cv_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating section {section}: {e}")
            return False

    def _update_personal_info(self, data: Dict, cv_data: CVData) -> bool:
        """Update personal info with safe handling of missing fields."""
        current_info = cv_data.personal_info or {}
        
        if data.get("name"): current_info["name"] = data["name"]
        if data.get("email"): current_info["email"] = data["email"] 
        if data.get("phone"): current_info["phone"] = data["phone"]
        if data.get("address"): current_info["address"] = data["address"]
        
        is_valid, error = validate_personal_info(
            current_info.get("name", ""),
            current_info.get("email", ""),
            current_info.get("phone", ""),
            current_info.get("address", "")
        )
        
        if is_valid:
            cv_data.add_personal_info(
                current_info.get("name", ""),
                current_info.get("email", ""),
                current_info.get("phone", ""),
                current_info.get("address", "")
            )
            return True
        
        logger.warning(f"Personal info validation failed: {error}")
        return False

    def _update_summary(self, data: Dict, cv_data: CVData) -> bool: 
        summary_text = data.get("summary", "")
        logger.debug(f"Attempting to update summary with: {summary_text}")
        
        if summary_text: 
            is_valid, error = validate_summary(summary_text)
            if is_valid:
                enhanced_summary = self.openai_service.enhance_summary(summary_text)
                cv_data.add_summary(enhanced_summary)
                logger.debug(f"Summary updated successfully: {enhanced_summary}")
                return True
            else:
                logger.warning(f"Summary validation failed: {error}")
                return False
        else:
            logger.warning("No summary text found in extracted data")
            return False

    def _update_education(self, data: Dict, cv_data: CVData) -> bool:
        """Update education section."""
        if all(data.get(field) for field in ["institution", "degree", "year"]):
            is_valid, error = validate_education(
                data["institution"], data["degree"], data["year"], data.get("details", "")
            )
            if is_valid:
                cv_data.add_education(
                    data["institution"], data["degree"], data["year"], data.get("details", "")
                )
                return True
        return False

    def _update_experience(self, data: Dict, cv_data: CVData) -> bool:
        """Update experience section."""
        required_fields = ["company", "role", "start_date", "end_date", "description"]
        if all(data.get(field) for field in required_fields):
            is_valid, error = validate_experience(
                data["company"], data["role"], data["start_date"], data["end_date"], data["description"]
            )
            if is_valid:
                cv_data.add_experience(
                    data["company"], data["role"], data["start_date"], data["end_date"], data["description"]
                )
                return True
        return False

    def _update_projects(self, data: Dict, cv_data: CVData) -> bool:
        """Update projects section."""
        if all(data.get(field) for field in ["name", "description"]):
            is_valid, error = validate_project(
                data["name"], data["description"], data.get("technologies", "")
            )
            if is_valid:
                cv_data.add_project(
                    data["name"], data["description"], data.get("technologies", "")
                )
                return True
        return False

    def _update_skills(self, data: Dict, cv_data: CVData) -> bool: 
        skills = data.get("skills", [])
        if isinstance(skills, str):
            skills = [s.strip() for s in skills.split(",") if s.strip()]
        
        if skills:
            is_valid, error = validate_skills(skills)
            if is_valid:
                for skill in skills:
                    cv_data.add_skill(skill.strip())
                return True
            else:
                logger.warning(f"Skills validation failed: {error}")
                return False
        return False

    def _update_certifications(self, data: Dict, cv_data: CVData) -> bool:
        """Update certifications section."""
        if all(data.get(field) for field in ["name", "issuer", "year"]):
            is_valid, error = validate_certification(
                data["name"], data["issuer"], data["year"]
            )
            if is_valid:
                cv_data.add_certification(
                    data["name"], data["issuer"], data["year"]
                )
                return True
        return False

    def _update_references(self, data: Dict, cv_data: CVData) -> bool:
        """Update references section."""
        if all(data.get(field) for field in ["name", "contact"]):
            is_valid, error = validate_reference(
                data["name"], data["contact"], data.get("relationship", "")
            )
            if is_valid:
                cv_data.add_reference(
                    data["name"], data["contact"], data.get("relationship", "")
                )
                return True
        return False

    def _build_cv_context(self, cv_data: CVData) -> str:
        """Build a summary of current CV state for AI context."""
        context = []
        
        if cv_data.personal_info:
            pi = cv_data.personal_info
            missing = []
            if not pi.get('phone'): missing.append('phone')
            if not pi.get('email'): missing.append('email')
            if not pi.get('address'): missing.append('address')
            
            context.append(f"Personal Info: Name: {pi.get('name', 'missing')}, Email: {pi.get('email', 'missing')}, Phone: {pi.get('phone', 'missing')}, Address: {pi.get('address', 'missing')}")
            if missing:
                context.append(f"Missing personal info: {', '.join(missing)}")
        else:
            context.append("Personal Info: Not provided yet")
        
        context.append(f"Summary: {'Provided' if cv_data.summary else 'Not provided yet'}")
        context.append(f"Education entries: {len(cv_data.education or [])}")
        context.append(f"Experience entries: {len(cv_data.experience or [])}")
        context.append(f"Projects: {len(cv_data.projects or [])}")
        context.append(f"Skills: {len(cv_data.skills or [])}")
        context.append(f"Certifications: {len(cv_data.certifications or [])}")
        context.append(f"References: {len(cv_data.references or [])}")
        
        return "\n".join(context)

    def _fallback_to_structured_processing(self, section: str, input: str, cv_data: CVData) -> tuple[str, bool, bool]:
        """Fallback to the original structured processing when AI fails."""
        logger.info(f"Falling back to structured processing for {section}")
        
        # Try original OpenAI parsing
        try:
            parsed_data, error = self.openai_service.parse_natural_language(input, section)
            if parsed_data and not error:
                response, success = self._process_parsed_data(section, parsed_data, cv_data)
                advance = section not in self.repeatable_sections
                return response, success, advance
        except Exception as e:
            logger.error(f"Fallback OpenAI parsing failed: {e}")
        
        # Final fallback
        return f"I'm having trouble understanding. Please try using the suggested format for {section.replace('_', ' ')}: {self.section_prompts[section]}", False, False