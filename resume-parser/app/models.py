from typing import List, Optional
from pydantic import BaseModel, Field


class Experience(BaseModel):
    company: Optional[str] = Field(None, description="Company name or 'Personal Project' / 'Academic Project'")
    role: Optional[str] = Field(None, description="Job title, role, or Project Name")
    duration: Optional[str] = Field(None, description="Duration of employment or project")
    responsibilities: Optional[List[str]] = Field(default_factory=list, description="List of key responsibilities, features built, or achievements")
    is_project: Optional[bool] = Field(False, description="True if this is an academic or personal project rather than formal employment")

class Education(BaseModel):
    degree: Optional[str] = Field(None, description="Degree obtained")
    institution: Optional[str] = Field(None, description="Name of the institution or university")
    year: Optional[str] = Field(None, description="Year of graduation or study period")

class ContactInfo(BaseModel):
    name: Optional[str] = Field(None, description="Full name of the candidate")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Location or address")

class ResumeData(BaseModel):
    contact_information: Optional[ContactInfo] = Field(None, description="Contact information of the candidate")
    professional_summary: Optional[str] = Field(None, description="Professional summary or objective")
    work_experience: Optional[List[Experience]] = Field(default_factory=list, description="Work experience details")
    education: Optional[List[Education]] = Field(default_factory=list, description="Educational background details")
    skills: Optional[List[str]] = Field(default_factory=list, description="List of technical and soft skills")
    certifications: Optional[List[str]] = Field(default_factory=list, description="List of certifications")


class UploadResponse(BaseModel):
    document_id: str = Field(..., description="Unique ID for the uploaded document")
    status: str = Field(..., description="Status of the extraction process")
    message: str = Field(..., description="Additional message regarding the upload")
    data: Optional[ResumeData] = Field(None, description="Extracted resume data")

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Detailed error message")
