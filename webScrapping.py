!pip install gspread beautifulsoup4 requests

from google.colab import drive
drive.mount('/content/drive')

from bs4 import BeautifulSoup
import requests
import sys
from google.auth import default

# Mount Google Drive to access files
from google.colab import auth
auth.authenticate_user()

import gspread
from google.auth import default
creds, _ = default()
gc = gspread.authorize(creds)
# Function to scrape data from LinkedIn
import re


def scrape_linkedin_jobs(start_index):
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?trk=guest_homepage-basic_guest_nav_menu_jobs&start={start_index}"

    response = requests.get(url)
    if response.status_code != 200:
        print("jobs finished. Exiting program.")
        sys.exit()



    soup = BeautifulSoup(response.text, "html.parser")



    locations = [loc.text.strip() for loc in soup.find_all(class_="job-search-card__location")]
    links = [tag.get('href') for tag in soup.find_all(class_="hidden-nested-link")]   #-> To get next 25 job desc
    descriptions = [tag.text.strip() for tag in soup.find_all(class_="hidden-nested-link")] # New array for text inside hidden-nested-link -> name of the company
    sr_only_tags = [tag.text.strip() for tag in soup.find_all(class_="sr-only")]

    for i in reversed(range(len(locations))):
        if re.search(r"(United States|united states|US)", locations[i]):
            del locations[i]
            del links[i]
            del descriptions[i] # Remove corresponding element from descriptions array
            del sr_only_tags[i]
        elif not re.search(r"(WFH|remote)", sr_only_tags[i], re.IGNORECASE):
            del locations[i]
            del links[i]
            del descriptions[i] # Remove corresponding element from descriptions array
            del sr_only_tags[i]

    return locations, links, descriptions, sr_only_tags



# Function to write data to Google Spreadsheet
def write_to_google_sheet(spreadsheet_key, locations, links,descriptions, sr_only_tags):
    gc = gspread.authorize(creds)
    sh = gc.open_by_key(spreadsheet_key)
    worksheet = sh.sheet1  # Assuming data is written to the first worksheet

    for loc, link, tag, desc in zip(locations, links, descriptions, sr_only_tags):
        worksheet.append_row([loc, link, desc ,tag])


# Iterate over API with start indices 0, 25, 800, ...

for start_index in range(0, 800, 25):
    locations, links, descriptions ,sr_only_tags = scrape_linkedin_jobs(start_index)
    spreadsheet_key = "1tcNqwY7zGH_CQM3p4hl6J2QJtO2F-9hgxcvg_RCGJl0"
    write_to_google_sheet(spreadsheet_key, locations, links,descriptions,sr_only_tags)