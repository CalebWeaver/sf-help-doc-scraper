import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Set up the Selenium WebDriver with options
def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    return webdriver.Chrome(options=chrome_options)

# Function to fetch a page using Selenium and return its content
def fetch_page(driver, url):
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    return driver.page_source

# Function to parse the page content and extract the Table of Contents URLs
def extract_urls_from_toc(page_content):
    soup = BeautifulSoup(page_content, 'html.parser')
    toc = soup.find('div', class_='table-of-content')
    if toc:
        urls = [a['href'] for a in toc.find_all('a', href=True)]
        print(f"Found {len(urls)} URLs in Table of Contents.")
        return urls
    else:
        print("Table of Contents not found.")
        return []

def clean_urls(url_list):
    cleaned_urls = []
    base_url = "https://help.salesforce.com"

    for url in url_list:
        # Only keep URLs that contain "articleView"
        if "articleView" in url:
            # Prepend the base URL if it's not already present
            if not url.startswith("http"):
                url = base_url + url
            cleaned_urls.append(url)

    print(f"Cleaned URLs: {len(cleaned_urls)} valid URLs found.")
    return cleaned_urls

def extract_and_append_content(driver, url, soup_list):
    soup = fetch_page(driver, url)
    content_div = soup.find('div', id='content')
    if content_div:
        soup_list.append(content_div)
        print("Content div found and saved.")
    else:
        print("Content div not found.")

def sanitize_filename(name):
    # Remove or replace characters that are not allowed in filenames
    return re.sub(r'[\/:*?"<>|]', '_', name)

# Function to save the parsed soup to files
def save_soups(soup_list, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for i, soup in enumerate(soup_list):
        # Extract the h1 tag content
        h1_tag = soup.find('h1')
        if h1_tag and h1_tag.text.strip():
            title = h1_tag.text.strip()
        else:
            title = f'soup_{i + 1}'  # Fallback if no h1 is found

        # Sanitize the title to make it a valid filename
        filename = sanitize_filename(title) + '.html'

        # Save the file
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(str(soup))
        print(f'Saved: {filepath}')

def save_urls(url_list, output_file='urls.txt'):
    with open(output_file, 'w', encoding='utf-8') as file:
        for url in url_list:
            file.write(url + '\n')
    print(f"URLs have been saved to {output_file}")

def load_urls_from_file(file_name='urls.txt'):
    url_list = []
    with open(file_name, 'r', encoding='utf-8') as file:
        url_list = [line.strip() for line in file.readlines()]
    print(f"Loaded {len(url_list)} URLs from {file_name}")
    return url_list

def check_for_url_file(file_name='urls.txt'):
    return os.path.exists('urls.txt')

def process_urls(driver, url_list, soup_list, start_index=0, end_index=None):
    # Adjust the end_index if it's not provided or out of bounds
    if end_index is None or end_index > len(url_list):
        end_index = len(url_list)

    # Loop through the specified range of URLs
    for i in range(start_index, end_index):
        url = url_list[i]
        print(f"Processing URL {i + 1}/{end_index} of {len(url_list)} total: {url}")
        # Call your function here, e.g., fetch_page or any other processing function
        extract_and_append_content(driver, url, soup_list)

# Main function to control the flow of the script
def main(url, output_dir='output-soups'):
    driver = setup_driver()
    pages = []
    soup_list = []
    url_list = []

    try:
        if (not check_for_url_file()):
          # Fetch the page and process it
          page_content = fetch_page(driver, url)
          pages.append(page_content)

          # Parse the page and extract URLs
          soup = BeautifulSoup(page_content, 'html.parser')
          soup_list.append(soup)
          urls = extract_urls_from_toc(page_content)
          urls = clean_urls(urls)
          url_list.extend(urls)
        else:
          url_list = load_urls_from_file()

        process_urls(driver, url_list, soup_list, 0, 1)

        # Save the soups to files
        save_urls(url_list)
        save_soups(soup_list, output_dir)

    finally:
        driver.quit()  # Ensure the driver is closed properly

    return url_list

# Run the script
if __name__ == "__main__":
    url = 'https://help.salesforce.com/s/articleView?id=sf.psc_admin_concept_psc_welcom.htm'
    main(url)