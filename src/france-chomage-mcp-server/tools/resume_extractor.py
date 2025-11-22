"""MCP tool for Resume Extraction using a VLM."""

import base64
import json
import os
from io import BytesIO

from openai import OpenAI
from pdf2image import convert_from_path
from pydantic import BaseModel, Field


class Experience(BaseModel):
    """Model for a single professional experience entry."""

    organization: str = Field(..., description="Name of the organization (company, institution, etc.)")
    role: str = Field(..., description="Role or position held")
    start_date: str = Field(..., description="Start date of the experience")
    end_date: str = Field(..., description="End date of the experience or 'Present' if ongoing")
    description: str = Field(..., description="Brief description of the experience")


class ResumeData(BaseModel):
    """Model for the extracted resume data."""

    name: str = Field(..., description="Full name of the candidate")
    email: str = Field(..., description="Email address of the candidate")
    phone: str = Field(..., description="Phone number of the candidate")
    soft_skills: list[str] = Field(..., description="List of soft skills mentioned in the resume")
    hard_skills: list[str] = Field(..., description="List of hard skills mentioned in the resume")
    education: list[Experience] = Field(..., description="List of educational qualifications")
    experiences: list[Experience] = Field(..., description="List of professional experiences")
    projects: list[str] = Field(..., description="List of projects undertaken by the candidate")
    publications: list[str] = Field(..., description="List of publications (papers, articles, etc.) by the candidate")
    languages: list[str] = Field(..., description="Languages known by the candidate")
    others: list[str] = Field(..., description="Other relevant information")


def pdf_to_base64(pdf_path: str) -> str:
    """Convert PDF file to base64 encoded string.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        str: Base64 encoded string of the PDF file.

    Raises:
        ValueError: If the PDF file cannot be read.
    """
    image = convert_from_path(pdf_path, first_page=1, last_page=1)
    if not image:
        msg = f"Could not convert PDF to image: {pdf_path}"
        raise ValueError(msg)

    buffered = BytesIO()
    image[0].save(buffered, format="JPEG", quality=90)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def resume_extractor(resume_file: str) -> dict:
    """Extract relevant information from a resume using a VLM.

    The return dict contains the following fields (ResumeData model):
    - name (str): Full name of the candidate.
    - email (str): Email address of the candidate.
    - phone (str): Phone number of the candidate.
    - soft_skills (list[str]): List of soft skills mentioned in the resume.
    - hard_skills (list[str]): List of hard skills mentioned in the resume.
    - education (list[Experience]): List of educational qualifications.
    - experiences (list[Experience]): List of professional experiences.
    - projects (list[str]): List of projects undertaken by the candidate.
    - publications (list[str]): List of publications (papers, articles, etc.) by the candidate.
    - languages (list[str]): Languages known by the candidate.
    - others (list[str]): Other relevant information.

    The Experience model is the following:
    - organization: str = Field(..., description="Name of the organization (company, institution, etc.)")
    - role (str): Role or position held.
    - start_date (str): Start date of the experience.
    - end_date (str): End date of the experience or 'Present' if ongoing.
    - description (str): Brief description of the experience.

    Args:
        resume_file (str): Path to the resume file (PDF format).

    Returns:
        dict: Extracted information from the resume in JSON format based on ResumeData model.
    """
    try:
        resume_base64 = pdf_to_base64(resume_file)
    except ValueError as e:
        return {"error": f"Failed to process resume file: {e}"}

    client = OpenAI(base_url="https://api.tokenfactory.nebius.com/v1", api_key=os.environ.get("NEBIUS_API_KEY"))

    system_prompt = f"""
    You are an expert resume analyzer.
    Extract only the relevant information from the resume image into a strict JSON format.
    Explications of the fields to extract:
    {json.dumps(ResumeData.model_json_schema(), indent=2)}

    Rules:
    1. Return ONLY the JSON object, without any additional text. No markdown, no intro text.
    2. If a field is missing, use null.
    3. Normalize dates to YYYY-MM format if possible.
    """

    try:
        response = client.chat.completions.parse(
            model="nvidia/Nemotron-Nano-V2-12b",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract resume data to JSON."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{resume_base64}"}},
                    ],
                },
            ],
            response_format=ResumeData,
            temperature=0.1,
        )

        data = response.choices[0].message.content
        resume_data = json.loads(data)

    except (json.JSONDecodeError, KeyError, IndexError, AttributeError, ValueError) as e:
        return {"error": f"VLM request failed: {e}"}
    else:
        return resume_data
