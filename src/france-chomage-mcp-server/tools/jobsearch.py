"""MCP Tool for Job Search Assistance using JobSpy."""

from jobspy import scrape_jobs


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
    # country_indeed: str,
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
    distance_miles = int(distance * 0.621371)

    jobs_df = scrape_jobs(
        site_name=site_name,
        search_term=search_term,
        google_search_term=google_search_term,
        location=location,
        distance=distance_miles,
        job_type=job_type,
        is_remote=is_remote,
        results_wanted=results_wanted,
        hours_old=hours_old,
        verbose=2,  # Set verbosity to 2 for detailed output
        linkedin_fetch_description=linkedin_fetch_description,
    )

    jobs = jobs_df.to_dict(orient="records")

    return jobs
