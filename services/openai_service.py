import os
from typing import Dict, Optional, Tuple
from openai import OpenAI
import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import cost settings
try:
    from config.cost_settings import MODEL_CONFIGS, DEFAULT_COST_MODE
except ImportError:
    # Fallback if config doesn't exist
    MODEL_CONFIGS = {
        "budget": {
            "model": "gpt-3.5-turbo",
            "max_tokens": 150,
            "temperature": 0.6,
            "estimated_cost_per_improvement": 0.008
        }
    }
    DEFAULT_COST_MODE = "balanced"

class OpenAIService:
    def __init__(self, cost_mode: str = DEFAULT_COST_MODE):
        try:
            # Try to get API key from Streamlit secrets (for cloud deployment)
            api_key = st.secrets["OPENAI_API_KEY"]
        except (KeyError, AttributeError):
            # Fallback to environment variable for local development
            api_key = os.getenv("OPENAI_API_KEY")
            
        if not api_key:
            logger.error("OPENAI_API_KEY not found in Streamlit secrets or environment variables.")
            raise ValueError("OPENAI_API_KEY not set. Please configure it in Streamlit secrets or environment variables.")
        
        self.client = OpenAI(api_key=api_key)
        
        # Set configuration based on cost mode
        self.cost_mode = cost_mode
        self.config = MODEL_CONFIGS.get(cost_mode, MODEL_CONFIGS[DEFAULT_COST_MODE])
        self.model = self.config["model"]
        self.max_tokens = self.config["max_tokens"]
        self.temperature = self.config["temperature"]
        
        # Cost tracking (approximate costs for gpt-3.5-turbo)
        self.cost_per_1k_input_tokens = 0.0015  # $0.0015 per 1K input tokens
        self.cost_per_1k_output_tokens = 0.002   # $0.002 per 1K output tokens
        self.session_cost = 0.0  # Track session costs

    def get_cost_info(self) -> Dict:
        """Get information about current cost settings."""
        return {
            "mode": self.cost_mode,
            "model": self.model,
            "description": self.config.get("description", ""),
            "estimated_cost_per_improvement": self.config.get("estimated_cost_per_improvement", 0.01),
            "session_cost": self.session_cost
        }

    def estimate_improvement_cost(self, cv_data: Dict) -> float:
        """Estimate the cost of improving CV data."""
        try:
            # Rough token estimation (1 token ≈ 4 characters for English text)
            total_chars = 0
            
            if cv_data.get("summary"):
                total_chars += len(cv_data["summary"])
            
            if cv_data.get("experience") and isinstance(cv_data["experience"], list):
                for exp in cv_data["experience"][:3]:  # We limit to 3 experiences
                    if exp.get("description"):
                        total_chars += len(exp["description"])
            
            if cv_data.get("skills"):
                skills_text = str(cv_data["skills"])
                total_chars += len(skills_text)
            
            # Add prompt overhead (roughly 200 characters)
            total_chars += 200
            
            # Convert to tokens (rough estimate: 1 token ≈ 4 characters)
            estimated_input_tokens = total_chars / 4
            estimated_output_tokens = self.max_tokens * 2   
            
            # Calculate cost
            input_cost = (estimated_input_tokens / 1000) * self.cost_per_1k_input_tokens
            output_cost = (estimated_output_tokens / 1000) * self.cost_per_1k_output_tokens
            
            total_cost = input_cost + output_cost
            return round(total_cost, 4)
            
        except Exception as e:
            logger.error(f"Cost estimation error: {e}")
            return 0.01  # Default small cost estimate

    def get_session_cost(self) -> float:
        """Get the total cost for this session."""
        return round(self.session_cost, 4)

    def reset_session_cost(self):
        """Reset the session cost counter."""
        self.session_cost = 0.0

    def parse_natural_language(self, input_text: str, section: str) -> Tuple[Optional[Dict], str]:
        """Parse natural language input into structured CV data for a given section. Cost-optimized."""
        try:
            prompt = self._build_parse_prompt(input_text, section)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Extract structured CV data from text. Return only JSON, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=self.max_tokens
            )
            result = response.choices[0].message.content
            try:
                import json
                parsed_data = json.loads(result)
            except json.JSONDecodeError:
                # Fallback: try to eval for simple dict-like strings
                try:
                    parsed_data = eval(result)
                except:
                    logger.error(f"Failed to parse OpenAI response: {result}")
                    return None, "Failed to parse response. Please try a different format."
                    
            if not isinstance(parsed_data, dict) or not parsed_data:
                return None, "Failed to parse input. Please provide details in a clear format."
            return parsed_data, ""
        except Exception as e:
            logger.error(f"OpenAI parsing error for section {section}: {e}")
            return None, "Error processing input. Please try again or use the structured format."

    def enhance_summary(self, summary: str) -> str:
        """Enhance a professional summary with AI suggestions. Cost-optimized."""
        try:
            prompt = f"Improve this CV summary professionally and concisely: {summary}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Improve CV summaries professionally."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI summary enhancement error: {e}")
            return summary  # Return original summary on error

    def improve_cv_comprehensively(self, cv_data: Dict) -> Dict:
        """Use OpenAI to comprehensively improve all sections of a CV with professional language, action verbs, and ATS optimization.
        Optimized for cost-efficiency by batching improvements in fewer API calls."""
        try:
            improved_data = cv_data.copy()
            
            # COST OPTIMIZATION: Batch multiple improvements in a single API call
            batch_improvements = self.batch_improve_cv_sections(cv_data)
            
            if batch_improvements:
                # Apply the batched improvements
                if batch_improvements.get("summary"):
                    improved_data["summary"] = batch_improvements["summary"]
                
                if batch_improvements.get("experience_improvements") and cv_data.get("experience"):
                    for i, exp in enumerate(improved_data.get("experience", [])):
                        if i < len(batch_improvements["experience_improvements"]):
                            exp["description"] = batch_improvements["experience_improvements"][i]
                
                if batch_improvements.get("skills"):
                    improved_data["skills"] = batch_improvements["skills"]
            
            return improved_data
            
        except Exception as e:
            logger.error(f"Comprehensive CV improvement error: {e}")
            return cv_data  # Return original data on error

    def batch_improve_cv_sections(self, cv_data: Dict) -> Dict:
        """Batch improve multiple CV sections in a single API call for cost efficiency."""
        try:
            # Prepare sections for improvement
            sections_to_improve = []
            
            if cv_data.get("summary"):
                sections_to_improve.append(f"SUMMARY: {cv_data['summary']}")
            
            if cv_data.get("experience") and isinstance(cv_data["experience"], list):
                for i, exp in enumerate(cv_data["experience"][:3]):  # Limit to first 3 experiences
                    if exp.get("description"):
                        role = exp.get('role', exp.get('position', f'Role {i+1}'))
                        sections_to_improve.append(f"EXPERIENCE_{i+1} ({role}): {exp['description']}")
            
            if cv_data.get("skills"):
                skills_text = cv_data["skills"] if isinstance(cv_data["skills"], str) else ", ".join(cv_data["skills"]) if isinstance(cv_data["skills"], list) else ""
                sections_to_improve.append(f"SKILLS: {skills_text}")
            
            if not sections_to_improve:
                return {}
            
            # Create a concise batch prompt
            prompt = f"""Improve these CV sections professionally. Return JSON format only:

{chr(10).join(sections_to_improve)}

Requirements:
- Use action verbs, professional language, ATS keywords
- Keep original meaning, make concise
- Return JSON: {{"summary": "improved text", "experience_improvements": ["improved desc 1", "improved desc 2"], "skills": ["skill1", "skill2"]}}"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a CV optimization expert. Return only valid JSON with improved CV sections."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens * 2  # Allow more tokens for batch response
            )
            
            # Track actual usage if available
            if hasattr(response, 'usage'):
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens
                cost = ((input_tokens / 1000) * self.cost_per_1k_input_tokens + 
                       (output_tokens / 1000) * self.cost_per_1k_output_tokens)
                self.session_cost += cost
                logger.info(f"API call cost: ${cost:.4f}, Session total: ${self.session_cost:.4f}")
            
            result = response.choices[0].message.content.strip()
            
            # Parse JSON response
            import json
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Fallback: try to extract improvements manually
                logger.warning("Failed to parse JSON response, using fallback")
                return self.fallback_batch_improvements(cv_data)
                
        except Exception as e:
            logger.error(f"Batch improvement error: {e}")
            return self.fallback_batch_improvements(cv_data)

    def fallback_batch_improvements(self, cv_data: Dict) -> Dict:
        """Fallback improvements that don't require API calls."""
        improvements = {}
        
        # Simple summary improvement
        if cv_data.get("summary"):
            summary = cv_data["summary"].strip()
            if len(summary) < 100:
                improvements["summary"] = f"Results-oriented professional with expertise in {summary.lower()}. Committed to delivering excellence and driving organizational success."
        
        # Simple experience improvements
        if cv_data.get("experience") and isinstance(cv_data["experience"], list):
            action_verbs = ["Achieved", "Implemented", "Led", "Managed", "Developed", "Optimized"]
            experience_improvements = []
            for i, exp in enumerate(cv_data["experience"][:3]):
                if exp.get("description"):
                    desc = exp["description"]
                    if not any(verb in desc for verb in action_verbs):
                        improved_desc = f"{action_verbs[i % len(action_verbs)]} {desc.lower()}"
                        experience_improvements.append(improved_desc)
                    else:
                        experience_improvements.append(desc)
            improvements["experience_improvements"] = experience_improvements
        
        # Simple skills improvement
        if cv_data.get("skills"):
            if isinstance(cv_data["skills"], str):
                skills_list = [skill.strip().title() for skill in cv_data["skills"].split(",")]
                improvements["skills"] = skills_list + ["Communication", "Problem-Solving", "Teamwork"]
            elif isinstance(cv_data["skills"], list):
                improvements["skills"] = cv_data["skills"] + ["Communication", "Problem-Solving", "Teamwork"]
        
        return improvements

    def enhance_professional_summary(self, summary: str) -> str:
        """Enhance professional summary with industry-standard language and keywords. Cost-optimized."""
        try:
            # Shorter, more focused prompt for cost efficiency
            prompt = f"""Improve this CV summary professionally and concisely:
"{summary}"

Make it: professional, ATS-friendly, 2-3 sentences, action-focused. Return only the improved text."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a CV writer. Improve summaries professionally and concisely."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content.strip().replace('"', '')
        except Exception as e:
            logger.error(f"Summary enhancement error: {e}")
            return summary

    def enhance_experience_entry(self, experience: Dict) -> Dict:
        """Enhance a single experience entry with action verbs and professional language."""
        try:
            improved_exp = experience.copy()
            
            if experience.get("description"):
                prompt = f"""
                Improve this job experience description to be more professional and ATS-friendly:
                
                Role: {experience.get('role', experience.get('position', 'Professional Role'))}
                Company: {experience.get('company', 'Company')}
                Original Description: "{experience['description']}"
                
                Requirements:
                - Start with strong action verbs (Achieved, Implemented, Led, Managed, etc.)
                - Quantify achievements where possible (even if estimated)
                - Use professional, concise language
                - Include relevant keywords for the role
                - Focus on accomplishments rather than just duties
                - Keep it to 2-3 bullet points or a brief paragraph
                
                Return only the improved description text.
                """
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional CV writer specializing in creating impactful experience descriptions that highlight achievements and use strong action verbs."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6
                )
                improved_exp["description"] = response.choices[0].message.content.strip().replace('"', '')
                
                # Add ATS keywords based on role
                improved_exp["ats_keywords"] = self.generate_ats_keywords(experience.get('role', experience.get('position', '')))
            
            return improved_exp
        except Exception as e:
            logger.error(f"Experience enhancement error: {e}")
            return experience

    def optimize_skills_for_ats(self, skills) -> list:
        """Optimize skills list for ATS compatibility and professional presentation."""
        try:
            skills_text = skills if isinstance(skills, str) else ", ".join(skills) if isinstance(skills, list) else ""
            
            prompt = f"""
            Optimize this skills list for ATS compatibility and professional presentation:
            
            Original Skills: "{skills_text}"
            
            Requirements:
            - Format as a clean, professional list
            - Add relevant complementary skills where appropriate
            - Use industry-standard terminology
            - Group similar skills logically
            - Include both technical and soft skills
            - Ensure skills are spelled correctly and professionally formatted
            
            Return as a JSON array of skill strings, for example: ["Skill 1", "Skill 2", "Skill 3"]
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a CV optimization expert who specializes in ATS-friendly skills formatting."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result = response.choices[0].message.content.strip()
            # Parse the JSON array response
            import json
            try:
                return json.loads(result)
            except:
                # Fallback: split by comma if JSON parsing fails
                return [skill.strip() for skill in result.replace('[', '').replace(']', '').replace('"', '').split(',')]
        except Exception as e:
            logger.error(f"Skills optimization error: {e}")
            return skills if isinstance(skills, list) else [skills] if skills else []

    def enhance_education_entry(self, education: Dict) -> Dict:
        """Enhance education entry with professional descriptions."""
        try:
            improved_edu = education.copy()
            
            prompt = f"""
            Create a professional description for this education entry:
            
            Institution: {education.get('institution', education.get('school', 'Institution'))}
            Degree: {education.get('degree', education.get('course', 'Course'))}
            Year: {education.get('year', 'Year')}
            Current Details: {education.get('details', 'None')}
            
            Requirements:
            - Create a brief, professional description if none exists
            - Enhance existing description to be more professional
            - Mention relevant coursework, achievements, or honors if appropriate
            - Keep it concise (1-2 sentences)
            
            Return only the improved details text.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a CV writer who creates professional education descriptions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            improved_edu["details"] = response.choices[0].message.content.strip().replace('"', '')
            return improved_edu
        except Exception as e:
            logger.error(f"Education enhancement error: {e}")
            return education

    def enhance_project_entry(self, project: Dict) -> Dict:
        """Enhance project entry with professional language."""
        try:
            improved_proj = project.copy()
            
            if project.get("description"):
                prompt = f"""
                Improve this project description to be more professional and impactful:
                
                Project Name: {project.get('name', 'Project')}
                Technologies: {project.get('technologies', 'Various')}
                Original Description: "{project['description']}"
                
                Requirements:
                - Use professional, technical language
                - Highlight key achievements and outcomes
                - Mention technologies used
                - Focus on impact and results
                - Keep it concise but descriptive
                
                Return only the improved description text.
                """
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a technical CV writer who creates compelling project descriptions."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.6
                )
                improved_proj["description"] = response.choices[0].message.content.strip().replace('"', '')
            
            return improved_proj
        except Exception as e:
            logger.error(f"Project enhancement error: {e}")
            return project

    def generate_ats_keywords(self, role: str) -> list:
        """Generate relevant ATS keywords based on job role."""
        try:
            prompt = f"""
            Generate 5-7 relevant ATS keywords for this job role: "{role}"
            
            Requirements:
            - Include industry-specific terms
            - Add relevant skills and technologies
            - Use standard professional terminology
            - Focus on keywords recruiters search for
            
            Return as a JSON array of keyword strings.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an ATS optimization expert who generates relevant keywords for job roles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5
            )
            
            result = response.choices[0].message.content.strip()
            import json
            try:
                return json.loads(result)
            except:
                # Fallback
                return ["teamwork", "leadership", "communication", "problem-solving", "efficiency"]
        except Exception as e:
            logger.error(f"ATS keywords generation error: {e}")
            return ["teamwork", "leadership", "communication", "problem-solving", "efficiency"]

    def _build_parse_prompt(self, input_text: str, section: str) -> str:
        """Build a prompt for parsing natural language input based on the CV section."""
        prompts = {
            "personal_info": f"Extract name, email, phone, and address from: '{input_text}'. Return a JSON object with keys: name, email, phone, address. Use empty string \"\" for missing fields, never use null or omit keys.",
            "education": f"Extract a single education entry with institution, degree, year, and details from: '{input_text}'. Return a JSON object with keys: institution, degree, year, details. Use empty string \"\" for missing fields.",
            "experience": f"Extract a single experience entry with company, role, start_date, end_date, and description from: '{input_text}'. Return a JSON object with keys: company, role, start_date, end_date, description. Use MM/YYYY format for dates (e.g., 01/2021), or 'now'/'present' for end_date if ongoing. Use empty string \"\" for missing fields.",
            "projects": f"Extract a single project entry with name, description, and technologies from: '{input_text}'. Return a JSON object with keys: name, description, technologies. Use empty string \"\" for missing fields.",
            "skills": f"Extract a list of skills from: '{input_text}'. Return a JSON object with a single key 'skills' containing a list of skill strings.",
            "certifications": f"Extract a single certification entry with name, issuer, and year from: '{input_text}'. Return a JSON object with keys: name, issuer, year. Use empty string \"\" for missing fields.",
            "references": f"Extract a single reference entry with name, contact, and relationship from: '{input_text}'. Return a JSON object with keys: name, contact, relationship. Use empty string \"\" for missing fields."
        }
        return prompts.get(section, "Invalid section.")