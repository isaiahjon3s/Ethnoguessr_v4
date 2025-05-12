import json
import requests
from bs4 import BeautifulSoup
import time

def get_description(url):
    try:
        # Add a small delay to be respectful to the server
        time.sleep(1)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the element containing 'Description'
            desc_elem = None
            for tag in soup.find_all(text=True):
                if tag and 'description' in tag.lower():
                    desc_elem = tag.parent
                    break
            if desc_elem:
                # Find the next element with non-empty text
                next_elem = desc_elem.find_next()
                while next_elem and (not next_elem.get_text(strip=True) or 'description' in next_elem.get_text(strip=True).lower()):
                    next_elem = next_elem.find_next()
                if next_elem:
                    # Extract the entire text block, ignoring HTML elements but keeping their text
                    text = next_elem.get_text(strip=True)
                    if text:
                        return text
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
    return ""

def update_phenotype_data():
    # Read the existing phenotype data
    with open('phenotype_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Update each phenotype with its description
    for phenotype in data:
        if not phenotype['description']:  # Only update if description is empty
            print(f"Scraping description for {phenotype['name']}...")
            description = get_description(phenotype['url'])
            phenotype['description'] = description
            if description:
                print(f"Found description: {description[:100]}...")  # Print first 100 chars
            else:
                print("No description found")
    
    # Save the updated data
    with open('phenotype_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("Finished updating phenotype descriptions!")

if __name__ == "__main__":
    update_phenotype_data() 