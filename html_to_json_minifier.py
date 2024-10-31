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
    if soup.find(nav_tag):
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