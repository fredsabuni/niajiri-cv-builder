"""
Professional CV PDF generation service with multiple templates.
This module provides comprehensive PDF generation for CV data with modern, professional styling.
"""

import io
from typing import Dict, Any
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Frame, PageTemplate, BaseDocTemplate, PageBreak
)
from reportlab.platypus.flowables import HRFlowable, Image
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from datetime import datetime


class ModernCVTemplate:
    """Modern, clean CV template with professional styling."""
    
    def __init__(self):
        self.primary_color = HexColor("#219680")
        self.secondary_color = HexColor("#1e7a68") 
        self.accent_color = HexColor("#f8fafc")
        self.text_color = HexColor("#1f2937")
        self.light_grey = HexColor("#6b7280")
        
        # Custom styles
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create custom paragraph styles for modern template."""
        styles = getSampleStyleSheet()
        
        # Header style
        styles.add(ParagraphStyle(
            name='CVHeader',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=self.primary_color,
            spaceAfter=0.2*inch,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Contact style
        styles.add(ParagraphStyle(
            name='Contact',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.light_grey,
            alignment=TA_CENTER,
            spaceAfter=0.3*inch
        ))
        
        # Section heading
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            spaceBefore=0.2*inch,
            spaceAfter=0.1*inch,
            borderWidth=0,
            borderPadding=0,
            leftIndent=0,
            borderColor=self.primary_color,
        ))
        
        # Subsection (job title, education, etc.)
        styles.add(ParagraphStyle(
            name='SubHeader',
            parent=styles['Normal'],
            fontSize=13,
            fontName='Helvetica-Bold',
            textColor=self.text_color,
            spaceBefore=0.1*inch,
            spaceAfter=0.05*inch
        ))
        
        # Detail text (dates, locations)
        styles.add(ParagraphStyle(
            name='Detail',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.light_grey,
            fontName='Helvetica-Oblique',
            spaceAfter=0.05*inch
        ))
        
        # Body text
        styles.add(ParagraphStyle(
            name='Body',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            alignment=TA_JUSTIFY,
            spaceAfter=0.1*inch,
            leading=14
        ))
        
        # Skills style
        styles.add(ParagraphStyle(
            name='Skills',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            spaceAfter=0.05*inch
        ))
        
        return styles
    
    def generate_pdf(self, cv_data: Dict[str, Any]) -> io.BytesIO:
        """Generate a modern CV PDF."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        story = []
        
        # Header section
        story.extend(self._create_header(cv_data))
        
        # Professional summary
        if cv_data.get("summary"):
            story.extend(self._create_summary(cv_data["summary"]))
        
        # Experience section
        if cv_data.get("experience"):
            story.extend(self._create_experience(cv_data["experience"]))
        
        # Education section
        if cv_data.get("education"):
            story.extend(self._create_education(cv_data["education"]))
        
        # Skills section
        if cv_data.get("skills"):
            story.extend(self._create_skills(cv_data["skills"]))
        
        # Projects section
        if cv_data.get("projects"):
            story.extend(self._create_projects(cv_data["projects"]))
        
        # Certifications section
        if cv_data.get("certifications"):
            story.extend(self._create_certifications(cv_data["certifications"]))
        
        # References section
        if cv_data.get("references"):
            story.extend(self._create_references(cv_data["references"]))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def _create_header(self, cv_data: Dict[str, Any]) -> list:
        """Create the header section with name and contact info."""
        elements = []
        personal = cv_data.get("personal_info", {})
        
        # Name
        name = personal.get("name", "Your Name")
        elements.append(Paragraph(name, self.styles['CVHeader']))
        
        # Contact information
        contact_info = []
        if personal.get('email'):
            contact_info.append(f"📧 {personal['email']}")
        if personal.get('phone'):
            contact_info.append(f"📱 {personal['phone']}")
        if personal.get('address'):
            contact_info.append(f"📍 {personal['address']}")
        
        if contact_info:
            elements.append(Paragraph(" • ".join(contact_info), self.styles['Contact']))
        
        # Separator line
        elements.append(HRFlowable(width="100%", thickness=1, color=self.primary_color))
        elements.append(Spacer(1, 0.2*inch))
        
        return elements
    
    def _create_summary(self, summary: str) -> list:
        """Create professional summary section."""
        elements = []
        elements.append(Paragraph("Professional Summary", self.styles['SectionHeader']))
        elements.append(Paragraph(summary, self.styles['Body']))
        elements.append(Spacer(1, 0.15*inch))
        return elements
    
    def _create_experience(self, experience: list) -> list:
        """Create work experience section."""
        elements = []
        elements.append(Paragraph("Professional Experience", self.styles['SectionHeader']))
        
        for exp in experience:
            # Job title and company
            title = exp.get('role', exp.get('position', 'Position'))
            company = exp.get('company', 'Company')
            elements.append(Paragraph(f"{title} • {company}", self.styles['SubHeader']))
            
            # Dates and location
            start_date = exp.get('start_date', '')
            end_date = exp.get('end_date', exp.get('duration', ''))
            if start_date and end_date:
                date_str = f"{start_date} - {end_date}"
            elif exp.get('duration'):
                date_str = exp['duration']
            else:
                date_str = ""
            
            if date_str:
                elements.append(Paragraph(date_str, self.styles['Detail']))
            
            # Description
            if exp.get('description'):
                elements.append(Paragraph(exp['description'], self.styles['Body']))
            
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_education(self, education: list) -> list:
        """Create education section."""
        elements = []
        elements.append(Paragraph("Education", self.styles['SectionHeader']))
        
        for edu in education:
            # Degree and institution
            degree = edu.get('degree', edu.get('course', 'Course'))
            institution = edu.get('institution', edu.get('school', 'Institution'))
            elements.append(Paragraph(f"{degree} • {institution}", self.styles['SubHeader']))
            
            # Year and details
            year = edu.get('year', '')
            if year:
                elements.append(Paragraph(year, self.styles['Detail']))
            
            if edu.get('details'):
                elements.append(Paragraph(edu['details'], self.styles['Body']))
            
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_skills(self, skills: list) -> list:
        """Create skills section."""
        elements = []
        elements.append(Paragraph("Skills", self.styles['SectionHeader']))
        
        if isinstance(skills, list) and skills:
            # Create a formatted skills list
            skills_text = " • ".join(str(skill).strip() for skill in skills if str(skill).strip())
            elements.append(Paragraph(skills_text, self.styles['Skills']))
        elif isinstance(skills, str) and skills.strip():
            elements.append(Paragraph(skills, self.styles['Skills']))
        
        elements.append(Spacer(1, 0.15*inch))
        return elements
    
    def _create_projects(self, projects: list) -> list:
        """Create projects section."""
        elements = []
        elements.append(Paragraph("Projects", self.styles['SectionHeader']))
        
        for project in projects:
            # Project name
            name = project.get('name', 'Project')
            elements.append(Paragraph(name, self.styles['SubHeader']))
            
            # Technologies
            if project.get('technologies'):
                tech_text = f"Technologies: {project['technologies']}"
                elements.append(Paragraph(tech_text, self.styles['Detail']))
            
            # Description
            if project.get('description'):
                elements.append(Paragraph(project['description'], self.styles['Body']))
            
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_certifications(self, certifications: list) -> list:
        """Create certifications section."""
        elements = []
        elements.append(Paragraph("Certifications", self.styles['SectionHeader']))
        
        for cert in certifications:
            # Certification name and issuer
            name = cert.get('name', 'Certification')
            issuer = cert.get('issuer', '')
            if issuer:
                cert_text = f"{name} • {issuer}"
            else:
                cert_text = name
            elements.append(Paragraph(cert_text, self.styles['SubHeader']))
            
            # Year
            if cert.get('year'):
                elements.append(Paragraph(cert['year'], self.styles['Detail']))
            
            elements.append(Spacer(1, 0.05*inch))
        
        elements.append(Spacer(1, 0.1*inch))
        return elements
    
    def _create_references(self, references: list) -> list:
        """Create references section."""
        elements = []
        elements.append(Paragraph("References", self.styles['SectionHeader']))
        
        for ref in references:
            # Reference name and relationship
            name = ref.get('name', 'Reference')
            relationship = ref.get('relationship', '')
            if relationship:
                ref_text = f"{name} • {relationship}"
            else:
                ref_text = name
            elements.append(Paragraph(ref_text, self.styles['SubHeader']))
            
            # Contact
            if ref.get('contact'):
                elements.append(Paragraph(ref['contact'], self.styles['Detail']))
            
            elements.append(Spacer(1, 0.05*inch))
        
        return elements


class ClassicCVTemplate:
    """Traditional, formal CV template."""
    
    def __init__(self):
        self.primary_color = HexColor("#2c3e50")
        self.secondary_color = HexColor("#34495e")
        self.text_color = black
        self.light_grey = HexColor("#7f8c8d")
        
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create styles for classic template."""
        styles = getSampleStyleSheet()
        
        # Header style
        styles.add(ParagraphStyle(
            name='CVHeader',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.primary_color,
            spaceAfter=0.2*inch,
            alignment=TA_CENTER,
            fontName='Times-Bold'
        ))
        
        # Contact style
        styles.add(ParagraphStyle(
            name='Contact',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            alignment=TA_CENTER,
            spaceAfter=0.3*inch,
            fontName='Times-Roman'
        ))
        
        # Section heading
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.primary_color,
            fontName='Times-Bold',
            spaceBefore=0.2*inch,
            spaceAfter=0.1*inch,
            borderWidth=1,
            borderPadding=3,
            borderColor=self.primary_color,
        ))
        
        # Other styles similar to modern but with Times font
        styles.add(ParagraphStyle(
            name='SubHeader',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Times-Bold',
            textColor=self.text_color,
            spaceBefore=0.1*inch,
            spaceAfter=0.05*inch
        ))
        
        styles.add(ParagraphStyle(
            name='Detail',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.light_grey,
            fontName='Times-Italic',
            spaceAfter=0.05*inch
        ))
        
        styles.add(ParagraphStyle(
            name='Body',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            alignment=TA_JUSTIFY,
            spaceAfter=0.1*inch,
            fontName='Times-Roman',
            leading=13
        ))
        
        styles.add(ParagraphStyle(
            name='Skills',
            parent=styles['Normal'],
            fontSize=11,
            textColor=self.text_color,
            spaceAfter=0.05*inch,
            fontName='Times-Roman'
        ))
        
        return styles
    
    def generate_pdf(self, cv_data: Dict[str, Any]) -> io.BytesIO:
        """Generate a classic CV PDF."""
        # Use the same structure as ModernCVTemplate but with classic styles
        template = ModernCVTemplate()
        template.styles = self.styles
        template.primary_color = self.primary_color
        return template.generate_pdf(cv_data)


class MinimalCVTemplate:
    """Clean, minimal CV template."""
    
    def __init__(self):
        self.primary_color = HexColor("#000000")
        self.secondary_color = HexColor("#666666")
        self.text_color = black
        self.light_grey = HexColor("#999999")
        
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create styles for minimal template."""
        styles = getSampleStyleSheet()
        
        styles.add(ParagraphStyle(
            name='CVHeader',
            parent=styles['Heading1'],
            fontSize=26,
            textColor=self.primary_color,
            spaceAfter=0.1*inch,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Contact',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.light_grey,
            alignment=TA_LEFT,
            spaceAfter=0.2*inch,
            fontName='Helvetica'
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=self.primary_color,
            fontName='Helvetica-Bold',
            spaceBefore=0.15*inch,
            spaceAfter=0.05*inch,
            textTransform='uppercase',
        ))
        
        styles.add(ParagraphStyle(
            name='SubHeader',
            parent=styles['Normal'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=self.text_color,
            spaceBefore=0.05*inch,
            spaceAfter=0.02*inch
        ))
        
        styles.add(ParagraphStyle(
            name='Detail',
            parent=styles['Normal'],
            fontSize=9,
            textColor=self.light_grey,
            fontName='Helvetica',
            spaceAfter=0.02*inch
        ))
        
        styles.add(ParagraphStyle(
            name='Body',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            alignment=TA_LEFT,
            spaceAfter=0.05*inch,
            fontName='Helvetica',
            leading=12
        ))
        
        styles.add(ParagraphStyle(
            name='Skills',
            parent=styles['Normal'],
            fontSize=10,
            textColor=self.text_color,
            spaceAfter=0.02*inch,
            fontName='Helvetica'
        ))
        
        return styles
    
    def generate_pdf(self, cv_data: Dict[str, Any]) -> io.BytesIO:
        """Generate a minimal CV PDF."""
        template = ModernCVTemplate()
        template.styles = self.styles
        template.primary_color = self.primary_color
        return template.generate_pdf(cv_data)


class CVPDFGenerator:
    """Main CV PDF generator with multiple template support."""
    
    def __init__(self):
        self.templates = {
            "Modern": ModernCVTemplate(),
            "Classic": ClassicCVTemplate(),
            "Minimal": MinimalCVTemplate()
        }
    
    def generate_pdf(self, cv_data: Dict[str, Any], template_name: str = "Modern") -> io.BytesIO:
        """Generate a CV PDF using the specified template."""
        if template_name not in self.templates:
            template_name = "Modern"
        
        template = self.templates[template_name]
        return template.generate_pdf(cv_data)
    
    def get_available_templates(self) -> list:
        """Get list of available template names."""
        return list(self.templates.keys())
