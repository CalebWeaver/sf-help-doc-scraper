Here is the README in Markdown format:

Salesforce Documentation Web Scraper

The Salesforce Documentation Web Scraper (sf_docs_webscraper.py) is a Python script that uses BeautifulSoup and Selenium to automate the process of scraping, organizing, and transforming Salesforce help documentation into JSON and HTML formats. It retrieves structured data from Table of Contents (TOC) pages, processes and saves content into organized files, and generates minified JSON files suitable for further analysis or use in web applications.

Features

	•	Automated Web Scraping: Navigates through Salesforce documentation pages, extracts Table of Contents (TOC) URLs, and processes individual pages.
	•	HTML Processing: Cleans and saves HTML content for each document.
	•	JSON Structuring: Builds and saves a nested JSON structure representing each TOC, with options for minified JSON.
	•	Data Transformation: Converts HTML content into JSON-compatible text using html_to_json_minifier.
	•	Efficient Saving: Saves progress and structure at intervals to avoid re-scraping on subsequent runs.
	•	Concatenated HTML Export: Combines all scraped HTML files into a single concatenated HTML file for easy viewing.

Requirements

	•	Python 3.6+
	•	Selenium
	•	BeautifulSoup (bs4)
	•	Google Chrome and ChromeDriver

Install the required packages using pip:

pip install beautifulsoup4 selenium

Setup

	1.	Download ChromeDriver: Ensure ChromeDriver is in your PATH. It should match your Chrome version.
	2.	Configure Directories: The script will save files in organized directories under Help Doc Output/{title} Help Docs.

Usage

	1.	Run the Script: Execute the main script to start scraping:

python sf_docs_webscraper.py


	2.	Specify Groups in the Main Function: Define the list of groups (documentation sections) in the groups list within the main function. Each group requires a title and url.
	3.	Headless Mode: The script uses Chrome in headless mode by default. To disable headless mode, modify the setup_driver function:

def setup_driver(headless=True):
    chrome_options = Options()
    # Remove or comment out this line to disable headless mode
    chrome_options.add_argument('--headless')
    return webdriver.Chrome(options=chrome_options)



Key Functions

setup_driver(headless=True)

Sets up and returns the Selenium ChromeDriver with optional headless mode.

get_toc_from_url(driver, url)

Navigates to a TOC page, retrieves the main TOC element, and parses it with BeautifulSoup.

extract_urls_from_toc(driver, url)

Extracts all URLs from a TOC page and returns them as a list.

build_content_structure(help_doc_dir, ul_element)

Recursively builds a structured JSON representation of the TOC, including title, link, and children nodes.

process_toc_urls(driver, toc_content, output_dir, start_index=0, end_index=None)

Processes each URL in the TOC, loading page content, saving it to a structured JSON file, and updating content as it processes.

minify_toc_structure(toc_structure)

Recursively removes unnecessary fields (e.g., link) and converts HTML content into a compact JSON-friendly structure.

concatenate_html_files(group_title, input_dir, output_path)

Concatenates individual HTML files into a single file for each documentation group.

Example Directory Structure

Help Doc Output/
├── Service Cloud Help Docs/
│   ├── Help Doc Pages/
│   │   ├── Customize Support Settings.html
│   │   ├── Set Business Hours.html
│   ├── toc_structure.json
│   ├── toc_structure_strip.json
│   └── toc_structure_min.json

Configuration Options

	•	Headless Mode: Toggle in setup_driver.
	•	Output Directories: Modify in the main function as needed.
	•	Save Frequency: The script saves after processing every 5 URLs. Adjust in process_toc_urls as needed.

Additional Notes

	•	Error Handling: The script includes retry logic for loading pages. Modify time.sleep() values for faster retries.
	•	Minified JSON: For minimized file size, the script can create both indented and compact JSON files.
	•	Custom Transformation: The script uses html_to_json_minifier to strip and convert HTML content. Ensure this module is configured for your specific transformation needs.

Example Code for Executing the Script

The following command starts the script and processes all specified groups in headless mode:

python sf_docs_webscraper.py

This will generate both detailed and minified JSON files for each group, along with a concatenated HTML file, all saved under Help Doc Output.

License

This project is for educational purposes and internal use only, especially if scraping documentation from sites like Salesforce. Please review Salesforce’s Terms of Service and scraping policies before running this tool in production.

