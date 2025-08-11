from typing import Tuple, List
import re

def validate_personal_info(name: str, email: str, phone: str, address: str) -> Tuple[bool, str]:
    if not name.strip():
        return False, "Name is required." 
    if not email.strip() and not phone.strip():
        return False, "At least one contact method (email or phone) is required."
    if email.strip() and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format." 
    if phone.strip() and not re.match(r"^\+?[\d\s\-()]{7,15}$", phone):
        return False, "Invalid phone format (e.g., +1234567890 or 0712345678)."
    
    return True, ""

def validate_education(institution: str, degree: str, year: str, details: str) -> Tuple[bool, str]:
    if not all([institution, degree, year]):
        return False, "Institution, degree, and year are required."
    if not year.isdigit() or int(year) < 1900 or int(year) > 2025:
        return False, "Year must be a valid number between 1900 and 2025."
    return True, ""

def validate_experience(company: str, role: str, start_date: str, end_date: str, description: str) -> Tuple[bool, str]:
    if not all([company, role, start_date, end_date, description]):
        return False, "Company, role, start date, end date, and description are required."
    if not re.match(r"^\d{2}/\d{4}$", start_date):
        return False, "Start date must be in MM/YYYY format (e.g., 01/2021)."
    if not re.match(r"^\d{2}/\d{4}$", end_date) and end_date.lower() not in ["present", "now", "current"]:
        return False, "End date must be in MM/YYYY format or 'present'/'now' for current positions."
    return True, ""

def validate_project(name: str, description: str, technologies: str) -> Tuple[bool, str]:
    if not all([name, description]):
        return False, "Name and description are required."
    return True, ""

def validate_skills(skills: List[str]) -> Tuple[bool, str]:
    if not skills or not all(s.strip() for s in skills):
        return False, "At least one skill is required."
    return True, ""

def validate_certification(name: str, issuer: str, year: str) -> Tuple[bool, str]:
    if not all([name, issuer, year]):
        return False, "Name, issuer, and year are required."
    if not year.isdigit() or int(year) < 1900 or int(year) > 2025:
        return False, "Year must be a valid number between 1900 and 2025."
    return True, ""

def validate_reference(name: str, contact: str, relationship: str) -> Tuple[bool, str]:
    if not all([name, contact]):
        return False, "Name and contact are required."
    if not re.match(r"[^@]+@[^@]+\.[^@]+|\+\d{10,15}", contact) and not contact.lower() == "n/a":
        return False, "Contact must be an email or phone number, or 'N/A'."
    return True, ""

def validate_summary(summary: str) -> Tuple[bool, str]:
    """Validate summary format and basic requirements."""
    if not summary or not summary.strip():
        return False, "Summary is required." 
    summary = summary.strip() 
    if len(summary) < 10:
        return False, "Summary should be at least 10 characters long." 
    if len(summary) > 500:
        return False, "Summary should not exceed 500 characters." 
    words = summary.split()
    if len(words) < 3:
        return False, "Summary should contain at least 3 words." 
    meaningful_words = [word for word in words if len(word) > 1]
    if len(meaningful_words) < 2:
        return False, "Summary should contain meaningful words."
    
    return True, ""