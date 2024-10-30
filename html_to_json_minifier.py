from bs4 import BeautifulSoup
import json
import html_to_json

# Function to remove all attributes from each tag
def clear_excess_attributes(soup):
    for tag in soup.find_all(True):  # True finds all tags
        # Preserve only 'src' and 'alt' attributes, if they exist
        preserved_attributes = {key: tag.attrs[key] for key in ('src', 'alt') if key in tag.attrs}
        tag.attrs = preserved_attributes
    return soup

# Function to remove specified tags but keep their content
def remove_visual_tags(soup):
    visual_tags = ['div', 'span', 'b', 'i', 'u', 'font', 'center', 'strike', 'strong', 'br']
    for tag in soup.find_all(visual_tags):
        tag.unwrap()  # Unwrap removes the tag but keeps its content
    return soup

def remove_nav_menu(soup):
    nav_tag = 'nav'
    soup.find(nav_tag).decompose()
    return soup

def strip_and_convert_html_content(html_content):
    if (html_content is None):
        return None

    soup = BeautifulSoup(html_content, 'lxml')
    soup = clear_excess_attributes(soup)
    soup = remove_visual_tags(soup)
    soup = remove_nav_menu(soup)

    json_data = html_to_json.convert(str(soup))
    return json_data

def main():
    items = [
        # {"title": "Sales Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.sales_core.htm&type=5"},
        # {"title": "Service Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.service_cloud.htm&type=5"},
        # {"title": "PSS", "url": "https://help.salesforce.com/s/articleView?id=sf.psc_admin_concept_psc_welcom.htm&type=5"},
        # {"title": "Experience Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.networks_overview.htm&type=5"},
        # {"title": "Identity and Access", "url": "https://help.salesforce.com/s/articleView?id=sf.identity_overview.htm&type=5"},
        # {"title": "Extend with Clicks", "url": "https://help.salesforce.com/s/articleView?id=sf.extend_click_intro.htm&type=5"},
        # {"title": "Industries Common Components", "url": "https://help.salesforce.com/s/articleView?id=sf.industries_common_features.htm&type=5"},
        # {"title": "Data Cloud", "url": "https://help.salesforce.com/s/articleView?id=sf.c360_a_data_cloud.htm&type=5"},
        # {"title": "Winter 25", "url": "https://help.salesforce.com/s/articleView?id=release-notes.salesforce_release_notes.htm&release=216&type=5"},
        # {"title": "Omnistudio", "url": "https://help.salesforce.com/s/articleView?id=sf.os_omnistudio_standard.htm&type=5"},
        {"title": "Industries Developer Guide", "url": "https://developer.salesforce.com/docs/atlas.en-us.industries_reference.meta/industries_reference/salesforce_industries_dev_guide.htm"},
    ]
    # Read your HTML files and convert them
    html_file_path = 'Help Doc Output/Omnistudio Help Docs.html'
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    json_data = strip_and_convert_html_content(html_content)

    # Save to a JSON file
    json_file_path = 'output.json'
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(json_data, json_file, separators=(',', ':'))

# Run the script
if __name__ == "__main__":
    main()