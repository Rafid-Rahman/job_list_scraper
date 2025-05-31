import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

def scrape_weworkremotely():
    url = "https://weworkremotely.com/categories/remote-full-stack-programming-jobs"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    jobs = []
    
    for job_section in soup.find_all("section", class_="jobs"):
        for job in job_section.find_all("li", class_="feature"):  # Job listings
            
            title_tag = job.find("h4", class_="new-listing__header__title")
            company_tag = job.find("p", class_="new-listing__company-name")
            link_tags = job.find_all("a", href=True)  # Extract all <a> tags
            
            if title_tag and company_tag and link_tags:
                title = title_tag.text.strip()
                company = company_tag.text.strip()
                
                
                job_link = link_tags[0]['href'] if len(link_tags) == 1 else link_tags[1]['href']
                
                # Ensure it's a full URL
                if not job_link.startswith("http"):
                    job_link = "https://weworkremotely.com" + job_link

                # Fetch additional details from job page
                job_details = scrape_job_details(job_link)
                
                jobs.append({
                    "Job Title": title,
                    "Company": company,
                    "Job Link": job_link,
                    **job_details
                })
    
    return jobs


def scrape_job_details(job_url):
    response = requests.get(job_url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve job page: {job_url}")
        return {
            "Posted On": "N/A",
            "Apply Before": "N/A",
            "Job Type": "N/A",
            "Region": "N/A"
        }
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all list items related to job details
    job_details_tags = soup.find_all("li", class_="lis-container__job__sidebar__job-about__list__item")

    # Extract "Posted On" and "Apply Before" from the first two matching <li> tags
    posted_on = job_details_tags[0].find("span").text.strip() if len(job_details_tags) > 0 and job_details_tags[0].find("span") else "N/A"
    apply_before = job_details_tags[1].find("span").text.strip() if len(job_details_tags) > 1 and job_details_tags[1].find("span") else "N/A"

    # Fixing "Job Type"
    job_type_tag = soup.find("span", class_="box box--jobType")
    job_type = job_type_tag.text.strip() if job_type_tag else "N/A"

    # Fixing "Region"
    region_tag = soup.find("li", class_="lis-container__job__sidebar__job-about__list__item--full")
    region = " | ".join([r.text.strip() for r in region_tag.find_all("span", class_="box--region")]) if region_tag else "N/A"

    return {
        "Posted On": posted_on,
        "Apply Before": apply_before,
        "Job Type": job_type,
        "Region": region
    }


def save_to_excel(jobs):
    if not jobs:
        print("No job listings found.")
        return
    
    df = pd.DataFrame(jobs)
    save_path = "F:\\Upwork\\Portfolio Projects\\Projects\\Job_Listings.xlsx"
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df.to_excel(save_path, index=False)
    print(f"Job listings saved to {save_path}")

if __name__ == "__main__":
    job_data = scrape_weworkremotely()
    save_to_excel(job_data)
