"""France Chômage MCP server file for deployement on Blaxel platform."""

import os

from mcp.server.fastmcp import FastMCP
from tools import job_search_tool as job_search_mcp_tool
from tools.resume_extractor import resume_extractor as resume_extractor_mcp_tool

mcp = FastMCP(
    "France Chômage MCP Server",
    stateless_http=True,
    host=os.getenv("BL_SERVER_HOST", "0.0.0.0"),  # noqa: S104
    port=os.getenv(
        "BL_SERVER_PORT",
        "80",
    ),
)


@mcp.tool()
def job_search_tool(
    site_name: list | str,
    search_term: str,
    google_search_term: str,
    location: str,
    distance: int,
    job_type: list,
    is_remote: bool,
    results_wanted: int,
    hours_old: int,
    linkedin_fetch_description: bool,
) -> dict:
    """Search for jobs using the scraper from JobSpy.

    Args:
        site_name (list | str): List of job sites to scrape from.
        search_term (str): The job title or keywords to search for.
        google_search_term (str): Search term for Google job search.
        location (str): The location to search for jobs in.
        distance (int): The search radius in kilometers.
        job_type (str): The type of job.
        is_remote (bool): Whether to include remote jobs.
        results_wanted (int): The number of job listings to retrieve for each site.
        hours_old (int): The maximum age of job listings in hours (ZipRecruiter and Glassdoor round up to next days).
        linkedin_fetch_description (bool): Whether to fetch full description and direct job url for LinkedIn.

    Returns:
        dict: A dict containing of the retrieved job informations.
    """
    return job_search_mcp_tool(
        site_name,
        search_term,
        google_search_term,
        location,
        distance,
        job_type,
        is_remote,
        results_wanted,
        hours_old,
        linkedin_fetch_description,
    )


@mcp.tool()
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
    return resume_extractor_mcp_tool(resume_file)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
