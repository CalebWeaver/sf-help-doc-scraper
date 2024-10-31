from bs4 import BeautifulSoup
import time
import os
import re
import shutil
import random
import json
import html_to_json_minifier
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# TODO: Make this work for developer docs too like this https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/salesforce_industries_dev_guide.htm

# Set up the Selenium WebDriver with options
def setup_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    return webdriver.Chrome(options=chrome_options)

def get_toc_from_url(driver, url):
    return load_page_with_retry(driver, url, 'ul', 'class', 'tree')

# Function to recursively build the JSON structure as indicated by the table of contents
def build_content_structure(help_doc_dir, ul_element):
    toc_structure = []
    print(f"toc ul_element: {ul_element}")
    for li in ul_element.find_all('li', recursive=False):
        title = li.get('title')

        # Find the <a> tag to extract the link
        a_tag = li.find('a')
        link = clean_url(a_tag['href']) if a_tag else None

        children_ul = li.find('ul')

        # Recursively get the children structure
        children = build_content_structure(help_doc_dir, children_ul) if children_ul else []

        toc_structure.append({
            "title": title,
            "link": link,
            "content": None,
            "children": children
        })

    return toc_structure

def clean_url(url):
    cleaned_url = None
    base_url = "https://help.salesforce.com"

    # Only keep URLs that contain "articleView"
    if "articleView" in url:
        # Prepend the base URL if it's not already present
        if not url.startswith("http"):
            cleaned_url = base_url + url
        else:
            cleaned_url = url

    return cleaned_url

def clean_urls(url_list):
    cleaned_urls = []

    for url in url_list:
        cleaned_url = clean_url(url)
        if cleaned_url:
            cleaned_urls.append(url)

    print(f"Cleaned URLs: {len(cleaned_urls)} valid URLs found.")
    return cleaned_urls

def check_for_element(driver, element_type='div', by='class', value=None):
    # Searches for an element of a specified type with a given attribute.
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    search_kwargs = {by: value}
    element = soup.find(element_type, **search_kwargs)
    return element

def load_page_with_retry(driver, url, element, by, value):
    driver.get(url)
    time.sleep(5)
    checkCount = 0
    content_div = None
    while True:
        content_div = check_for_element(driver, element, by, value)

        if content_div:
            print(f"{element} with {by} '{value}' found.")
            return content_div
        elif not content_div and checkCount <= 4:
            checkCount += 1
            print(f"{element} with {by} '{value}' not found. Attempt {checkCount} of 5.")
            time.sleep(1)
        else:
            print(f"{element} with {by} '{value}' not found. Abandoned.")
            return

def sanitize_filename(name):
    # Remove or replace characters that are not allowed in filenames
    return re.sub(r'[\/:*?"<>|]', '_', name)

# Function to save the parsed soup to files
def save_soup(soup, output_dir, title):
    os.makedirs(output_dir, exist_ok=True)

    # Sanitize the title to make it a valid filename
    filename = sanitize_filename(title) + '.html'

    # Save the file
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(str(soup))
    print(f'Saved: {filepath}')

def process_toc_urls(driver, toc_content, output_dir, start_index=0, end_index=None):

    url_list = flatten_toc_content(toc_content)
    # Adjust the end_index if it's not provided or out of bounds
    if end_index is None or end_index > len(url_list):
        end_index = len(url_list)

    # Loop through the specified range of URLs
    for i in range(start_index, end_index):
        toc_node = url_list[i]  # Get the current TOC node with title, link, etc.

        if (toc_node['content']):
            continue

        url = toc_node['link']
        title = toc_node['title']
        print(f"Processing URL {i + 1}/{end_index} of {len(url_list)} total: {url}")

        contentSoup = load_page_with_retry(driver, url, 'div', 'id', 'content')

        if contentSoup:
            # Save the soup content to file
            save_soup(contentSoup, os.path.join(output_dir, "Help Doc Pages"), title)

            # Convert the soup content to text or HTML and update the toc_node
            toc_node['content'] = str(contentSoup)

            # Save after every `save_frequency` iterations
            if (i + 1) % 5 == 0:
                save_json_to_file(toc_content, output_dir, "toc_structure.json")

        print()

    # Final save after processing all URLs
    save_json_to_file(toc_content, output_dir, "toc_structure.json")

    return toc_content

def flatten_toc_content(toc_content):
    # Recursively flatten the toc_content JSON structure to extract references to nodes.
    url_list = []

    for node in toc_content:
        if 'link' in node and node['link']:  # Ensure the node has a valid link
            url_list.append(node)  # Append the original node to maintain the reference

        # Recursively process children
        if 'children' in node and node['children']:
            url_list.extend(flatten_toc_content(node['children']))  # Extend with child nodes

    return url_list

def concatenate_html_files(group_title, input_dir, output_path):
    output_file = os.path.join(output_path, group_title + " Concat.html")

    os.makedirs(output_path, exist_ok=True)

    # Empty the output file if it exists
    with open(output_file, 'w', encoding='utf-8') as outfile:
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

def save_json_to_min_file(content, output_dir, file_name):
    print(f"Saving to {output_dir}/{file_name}")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, file_name)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(content, outfile, separators=(',', ':'))

def save_json_to_file(content, output_dir, file_name):
    print(f"Saving to {output_dir}/{file_name}")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, file_name)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(content, outfile, indent=2)

def minify_toc_structure(toc_structure):
    """
    Recursively transforms the toc_structure by removing the 'link' field 
    and converting the 'content' field using html_to_json.strip_and_convert_html.
    """
    new_structure = []

    for node in toc_structure:
        # Copy the fields we want to keep
        transformed_node = {
            't': node['title'],
            'c': html_to_json_minifier.strip_and_convert_html_content(node['content']) if 'content' in node else None,
            'ch': minify_toc_structure(node['children']) if 'children' in node else []
        }
        if transformed_node['c'] or transformed_node['ch']:
            # Append the transformed node to the new structure
            new_structure.append(transformed_node)

    return new_structure

def format_title(title_string):
    title_string = title_string.lower().replace(" ", "_")
    return title_string

# Main function to control the flow of the script
def main(output_dir='output-soups'):
    driver = setup_driver()

    groups = [
        # {"title": "Sales Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.sales_core.htm&type=5"},
        # {"title": "Service Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.service_cloud.htm&type=5"},
        {"title": "PSS", "url": "https://help.salesforce.com/s/articleView?id=sf.psc_admin_concept_psc_welcom.htm&type=5"},
        {"title": "Experience Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.networks_overview.htm&type=5"},
        {"title": "Identity and Access", "url": "https://help.salesforce.com/s/articleView?id=sf.identity_overview.htm&type=5"},
        {"title": "Extend with Clicks", "url": "https://help.salesforce.com/s/articleView?id=sf.extend_click_intro.htm&type=5"},
        {"title": "Industries Common Components", "url": "https://help.salesforce.com/s/articleView?id=sf.industries_common_features.htm&type=5"},
        {"title": "Data Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.c360_a_data_cloud.htm&type=5"},
        {"title": "Winter 25", "url": "https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=216&type=5"},
        # {"title": "Omnistudio", "url": "https://help.salesforce.com/s/articleView?id=sf.os_omnistudio_standard.htm&type=5"},
    ]

    try:
        for group in groups:

            help_doc_dir = os.path.join("Help Doc Output", f"{group['title']} Help Docs")

            title = group['title']
            url = group['url']
            toc_file_path = os.path.join(help_doc_dir, "toc_structure.json")

            print(f"Processing {title}...")

            # Clear output-soups directory before processing
            # clear_output_files(output_dir='output-soups')

            # Check if the toc_structure file exists
            if os.path.exists(toc_file_path):
                print(f"Loading existing TOC structure from {toc_file_path}...")
                with open(toc_file_path, 'r', encoding='utf-8') as toc_file:
                    toc_structure = json.load(toc_file)
            else:
                print(f"Building TOC Structure from {url}...")
                # Fetch the base page and get all urls from toc
                toc_element = get_toc_from_url(driver, url)
                toc_structure = build_content_structure(help_doc_dir, toc_element)
                save_json_to_file(toc_structure, help_doc_dir, "toc_structure.json")

            process_toc_urls(driver, toc_structure, help_doc_dir)

            strip_toc_structure = minify_toc_structure(toc_structure)
            save_json_to_file(strip_toc_structure, help_doc_dir, "toc_structure_strip.json")
            save_json_to_min_file(strip_toc_structure, help_doc_dir, format_title(group['title']) + "_toc_structure_min.json")

            # Concatenate the HTML files
            concatenate_html_files(title, os.path.join(help_doc_dir, "Help Doc Pages"), help_doc_dir)
            # print(f"Completed processing for {title}\n")

    finally:
        driver.quit()  # Ensure the driver is closed properly

# Run the script
if __name__ == "__main__":
    main()

