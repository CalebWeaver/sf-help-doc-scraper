Here's a basic README file that you can use for your project. It covers the key aspects of your script, including its purpose, how to set it up, and how to run it.

---

# Salesforce Documentation Web Scraper

This project is a Python-based web scraper designed to extract and save content from Salesforce documentation pages. It uses Selenium for web page interaction and BeautifulSoup for HTML parsing. The scraper fetches URLs from the table of contents of a specified Salesforce documentation page, processes them, and saves the relevant content to HTML files.

## Features

- **URL Extraction:** Extracts URLs from the Table of Contents (TOC) of a Salesforce documentation page.
- **Content Extraction:** Fetches the content from each URL and extracts the main content (`div` with `id="content"`).
- **File Saving:** Saves the extracted content as individual HTML files, using the `<h1>` tag of the content as the filename.
- **Incremental Processing:** Processes and saves each page's content immediately, improving memory efficiency and providing real-time progress.

## Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`
- `pandas`
- `selenium`
- Chrome WebDriver (matching your installed version of Chrome)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/sf-docs-webscraper.git
   cd sf-docs-webscraper
   ```

2. **Install dependencies:**

   You can install the required Python packages using `pip`:

   ```bash
   pip install requests beautifulsoup4 pandas selenium
   ```

3. **Set up ChromeDriver:**

   Make sure you have [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/downloads) installed and that it matches your version of Chrome. Add the `chromedriver` executable to your system's PATH.

## Usage

1. **Run the Script:**

   To scrape a Salesforce documentation page, navigate to the project directory and run the following command:

   ```bash
   python sf-docs-webscraper.py
   ```

   By default, the script starts processing the URLs found on the Salesforce documentation page specified in the code.

2. **Customizing the URL Range:**

   You can customize the range of URLs processed by modifying the `start_index` and `end_index` parameters in the `main()` function call within the script:

   ```python
   process_urls(driver, url_list, output_dir, start_index=2, end_index=350)
   ```

3. **Output:**

   - The extracted content will be saved as HTML files in the `output-soups` directory.
   - The filenames are derived from the `<h1>` tag in the content. If no `<h1>` tag is found, a fallback filename is used.

4. **Saving URLs:**

   The script saves all the URLs it processes to a file named `urls.txt`. If the file exists, the script will load the URLs from this file instead of fetching them again.

## Troubleshooting

- **ChromeDriver Issues:** Ensure that ChromeDriver is installed and correctly added to your PATH. The version of ChromeDriver must match the version of Chrome installed on your machine.
- **Missing Content:** If the script fails to find the content (`div` with `id="content"`), ensure that the Salesforce documentation page structure has not changed.
- **File Overwrites:** The script sanitizes filenames to avoid illegal characters. However, if multiple pages have the same `<h1>` content, files may be overwritten. Consider manually checking for unique filenames if this occurs.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any bugs or suggestions.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

---

Feel free to customize this README to better fit your project's needs, especially the sections about installation, usage, and contributing.
