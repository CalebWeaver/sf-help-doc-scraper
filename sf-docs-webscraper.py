import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re
import shutil
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Set up the Selenium WebDriver with options
def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    return webdriver.Chrome(options=chrome_options)

# Function to parse the page content and extract the Table of Contents URLs
def extract_urls_from_toc(driver, url):
    toc = load_page_with_retry(driver, url, 'class', 'table-of-content')
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

def check_for_element(driver, by, value):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    search_kwargs = {by: value}
    div = soup.find('div', **search_kwargs)
    return div

def load_page_with_retry(driver, url, by, value):
    driver.get(url)
    time.sleep(2)
    checkCount = 0
    content_div = None
    while True:
        content_div = check_for_element(driver, by, value)

        if content_div:
            print(f"Div with {by} '{value}' found.")
            return content_div
        elif not content_div and checkCount <= 4:
            checkCount += 1
            print(f"Div with {by} '{value}' not found. Attempt {checkCount} of 5.")
            time.sleep(1)
        else:
            print(f"Div with {by} '{value}' not found. Abandoned.")
            return

def sanitize_filename(name):
    # Remove or replace characters that are not allowed in filenames
    return re.sub(r'[\/:*?"<>|]', '_', name)

# Function to save the parsed soup to files
def save_soup(soup, output_dir, index):
    os.makedirs(output_dir, exist_ok=True)

    # Extract the h1 tag content
    h1_tag = soup.find('h1')
    if h1_tag and h1_tag.text.strip():
        title = h1_tag.text.strip()
    else:
        title = f'soup_{index}'  # Fallback if no h1 is found

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

def process_urls(driver, url_list, output_dir, start_index=0, end_index=None):
    # Adjust the end_index if it's not provided or out of bounds
    if end_index is None or end_index > len(url_list):
        end_index = len(url_list)

    # Loop through the specified range of URLs
    for i in range(start_index, end_index):
        url = url_list[i]
        print(f"Processing URL {i + 1}/{end_index} of {len(url_list)} total: {url}")

        contentSoup = load_page_with_retry(driver, url, 'id', 'content')

        if contentSoup:
            save_soup(contentSoup, output_dir, i)

        print()

def concatenate_html_files(input_dir='output-soups', output_file='combined.html'):
    # Define the path to the output file in the project root
    project_root = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(project_root, output_file)

    # Empty the output file if it exists
    with open(output_path, 'w', encoding='utf-8') as outfile:
        # Loop through all HTML files in the input directory
        for file_name in os.listdir(input_dir):
            if file_name.endswith('.html'):
                file_path = os.path.join(input_dir, file_name)
                # Read the content of the current HTML file
                with open(file_path, 'r', encoding='utf-8') as infile:
                    outfile.write(infile.read())
                    # Append three new lines after each file's content
                    outfile.write('\n\n\n')

    print(f"All files have been concatenated into {output_path}")

def clear_output_files(url_file='urls.txt', output_dir='output-soups'):
    # Delete the URL file if it exists
    if os.path.exists(url_file):
        os.remove(url_file)
        print(f"Deleted {url_file}")
    else:
        print(f"{url_file} does not exist.")

    # Clear out the output-soups directory
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        os.makedirs(output_dir)  # Recreate the empty directory
        print(f"Cleared all files in {output_dir}")
    else:
        print(f"{output_dir} directory does not exist.")

def process_title_and_urls(driver, title, urls):
    output_dir = os.path.join('output-soups', sanitize_filename(title))
    os.makedirs(output_dir, exist_ok=True)

    # Process the URLs
    process_urls(driver, urls, output_dir, 292)

    # Concatenate the HTML files
    concatenate_html_files(output_dir, output_file=f"{title}.html")

    # Move the concatenated file to the title's directory
    # shutil.move(f"{title} Help Docs Concat.html", output_dir)

# Main function to control the flow of the script
def main(output_dir='output-soups'):
    driver = setup_driver()

    items = [
        # {"title": "Experience Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.networks_overview.htm&type=5"},
        # {"title": "Identity and Access", "url": "https://help.salesforce.com/s/articleView?id=sf.identity_overview.htm&type=5"},
        # {"title": "Extend with Clicks", "url": "https://help.salesforce.com/s/articleView?id=sf.extend_click_intro.htm&type=5"},
        # {"title": "Industries Common Components", "url": "https://help.salesforce.com/s/articleView?id=sf.industries_common_features.htm&type=5"},
        {"title": "Data Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.c360_a_data_cloud.htm&type=5"},
    ]

    try:
        for item in items:
            title = item['title']
            url = item['url']
            print(f"Processing {title}...")

            # Clear output-soups directory before processing
            # clear_output_files(output_dir='output-soups')

            # Fetch the base page and get all urls from toc
            # urls = extract_urls_from_toc(driver, url)
            # urls = clean_urls(urls)
            # save_urls(urls)
            urls = load_urls_from_file()

            # Process the title and URLs
            process_title_and_urls(driver, title, urls)
            print(f"Completed processing for {title}\n")

    finally:
        driver.quit()  # Ensure the driver is closed properly

# Run the script
if __name__ == "__main__":
    main()