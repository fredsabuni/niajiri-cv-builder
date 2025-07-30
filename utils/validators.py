# import re
# from typing import Tuple, Optional
# from email_validator import validate_email, EmailNotValidError

# def validate_personal_info(name: str, email: str, phone: str, address: str) -> Tuple[bool, str]:
#     """Validate personal information fields."""
#     # Name: non-empty string
#     if not name.strip():
#         return False, "Name cannot be empty."

#     # Email: use email-validator
#     try:
#         validate_email(email.strip(), check_deliverability=False)
#     except EmailNotValidError as e:
#         return False, f"Invalid email format: {str(e)}"

#     # Phone: basic regex for international formats (e.g., +1234567890, 123-456-7890)
#     phone_pattern = r"^\+?[\d\s\-()]{7,15}$"
#     if not re.match(phone_pattern, phone.strip()):
#         return False, "Invalid phone format. Use formats like +1234567890 or 123-456-7890."

#     # Address: non-empty string (basic check, as formats vary widely)
#     if not address.strip():
#         return False, "Address cannot be empty."

#     return True, ""

# def validate_education(institution: str, degree: str, year: str, details: str) -> Tuple[bool, str]:
#     """Validate education fields."""
#     # Institution and degree: non-empty strings
#     if not institution.strip():
#         return False, "Institution cannot be empty."
#     if not degree.strip():
#         return False, "Degree cannot be empty."

#     # Year: 4-digit number between 1900 and current year
#     try:
#         year_int = int(year.strip())
#         if not (1900 <= year_int <= 2025):
#             return False, "Year must be between 1900 and 2025."
#     except ValueError:
#         return False, "Year must be a valid number."

#     # Details: optional, no validation needed
#     return True, ""

# def validate_experience(company: str, role: str, start_date: str, end_date: str, description: str) -> Tuple[bool, str]:
#     """Validate experience fields."""
#     # Company and role: non-empty strings
#     if not company.strip():
#         return False, "Company cannot be empty."
#     if not role.strip():
#         return False, "Role cannot be empty."

#     # Dates: MM/YYYY format
#     date_pattern = r"^(0[1-9]|1[0-2])\/[0-9]{4}$"
#     if not re.match(date_pattern, start_date.strip()):
#         return False, "Start date must be in MM/YYYY format."
#     if not re.match(date_pattern, end_date.strip()) and end_date.strip().lower() != "present":
#         return False, "End date must be in MM/YYYY format or 'present'."

#     # Description: non-empty
#     if not description.strip():
#         return False, "Description cannot be empty."

#     return True, ""

# def validate_project(name: str, description: str, technologies: str) -> Tuple[bool, str]:
#     """Validate project fields."""
#     # Name and description: non-empty strings
#     if not name.strip():
#         return False, "Project name cannot be empty."
#     if not description.strip():
#         return False, "Description cannot be empty."

#     # Technologies: optional, no strict validation
#     return True, ""

# def validate_skills(skills: list) -> Tuple[bool, str]:
#     """Validate skills list."""
#     if not skills or not any(skill.strip() for skill in skills):
#         return False, "At least one skill must be provided."
#     return True, ""

# def validate_certification(name: str, issuer: str, year: str) -> Tuple[bool, str]:
#     """Validate certification fields."""
#     # Name and issuer: non-empty strings
#     if not name.strip():
#         return False, "Certification name cannot be empty."
#     if not issuer.strip():
#         return False, "Issuer cannot be empty."

#     # Year: 4-digit number between 1900 and current year
#     try:
#         year_int = int(year.strip())
#         if not (1900 <= year_int <= 2025):
#             return False, "Year must be between 1900 and 2025."
#     except ValueError:
#         return False, "Year must be a valid number."

#     return True, ""

# def validate_reference(name: str, contact: str, relationship: str) -> Tuple[bool, str]:
#     """Validate reference fields."""
#     # Name and contact: non-empty strings
#     if not name.strip():
#         return False, "Reference name cannot be empty."
#     if not contact.strip():
#         return False, "Contact information cannot be empty."

#     # Relationship: optional
#     return True, ""

from typing import Tuple, List
import re

def validate_personal_info(name: str, email: str, phone: str, address: str) -> Tuple[bool, str]:
    if not all([name, email, phone]):
        return False, "Name, email, and phone are required."
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return False, "Invalid email format."
    if not re.match(r"^\+?\d{10,15}$", phone):
        return False, "Invalid phone format (e.g., +1234567890)."
    return True, ""

def validate_education(institution: str, degree: str, year: str, details: str) -> Tuple[bool, str]:
    if not all([institution, degree, year]):
        return False, "Institution, degree, and year are required."
    if not year.isdigit() or int(year) < 1900 or int(year) > 2025:
        return False, "Year must be a valid number between 1900 and 2025."
    return True, ""

def validate_experience(company: str, role: str, start_date: str, end_date: str, description: str) -> Tuple[bool, str]:
    if not all([company, role, start_date, end_date]):
        return False, "Company, role, start date, and end date are required."
    if not re.match(r"^\d{2}/\d{4}$", start_date) or not re.match(r"^\d{2}/\d{4}$|^present$", end_date):
        return False, "Dates must be in MM/YYYY format or 'present' for end date."
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