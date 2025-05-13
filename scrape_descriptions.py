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
            # Find the <h3> tag with 'Description' in its text
            desc_h3 = None
            for h3 in soup.find_all('h3'):
                if 'description' in h3.get_text(strip=True).lower():
                    desc_h3 = h3
                    break
            if desc_h3:
                description_parts = []
                # Go through siblings after the <h3>Description</h3> until the next <h3>
                for sib in desc_h3.next_siblings:
                    if getattr(sib, 'name', None) == 'h3':
                        break
                    if isinstance(sib, str):
                        text = sib.strip()
                        if text:
                            description_parts.append(text)
                    elif hasattr(sib, 'get_text'):
                        text = sib.get_text(separator=' ', strip=True)
                        if text:
                            description_parts.append(text)
                if description_parts:
                    return ' '.join(description_parts)
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