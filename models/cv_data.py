from typing import Dict, List, Optional

class CVData:
    def __init__(self):
        self.personal_info: Dict[str, str] = {}
        self.summary: Optional[str] = None
        self.education: List[Dict[str, str]] = []
        self.experience: List[Dict[str, str]] = []
        self.projects: List[Dict[str, str]] = []
        self.skills: List[str] = []
        self.certifications: List[Dict[str, str]] = []
        self.references: List[Dict[str, str]] = []

    def add_personal_info(self, name: str, email: str, phone: str, address: str) -> None:
        self.personal_info = {"name": name, "email": email, "phone": phone, "address": address}

    def add_summary(self, summary: str) -> None:
        self.summary = summary

    def add_education(self, institution: str, degree: str, year: str, details: str) -> None:
        self.education.append({"institution": institution, "degree": degree, "year": year, "details": details})

    def add_experience(self, company: str, role: str, start_date: str, end_date: str, description: str) -> None:
        self.experience.append({"company": company, "role": role, "start_date": start_date, "end_date": end_date, "description": description})

    def add_project(self, name: str, description: str, technologies: str) -> None:
        self.projects.append({"name": name, "description": description, "technologies": technologies})

    def add_skill(self, skill: str) -> None:
        self.skills.append(skill)

    def add_certification(self, name: str, issuer: str, year: str) -> None:
        self.certifications.append({"name": name, "issuer": issuer, "year": year})

    def add_reference(self, name: str, contact: str, relationship: str) -> None:
        self.references.append({"name": name, "contact": contact, "relationship": relationship})

    def to_dict(self) -> Dict:
        return {
            "personal_info": self.personal_info,
            "summary": self.summary,
            "education": self.education,
            "experience": self.experience,
            "projects": self.projects,
            "skills": self.skills,
            "certifications": self.certifications,
            "references": self.references
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'CVData':
        """Create a CVData instance from a dictionary."""
        cv_data = cls()
        cv_data.personal_info = data.get("personal_info", {})
        cv_data.summary = data.get("summary")
        cv_data.education = data.get("education", [])
        cv_data.experience = data.get("experience", [])
        cv_data.projects = data.get("projects", [])
        cv_data.skills = data.get("skills", [])
        cv_data.certifications = data.get("certifications", [])
        cv_data.references = data.get("references", [])
        return cv_data