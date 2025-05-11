import os
import time
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class PhenotypeScraper:
    def __init__(self):
        self.base_url = "http://humanphenotypes.net"
        self.basic_url = "http://humanphenotypes.net/basic"
        self.data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def get_phenotype_links(self):
        """Get all phenotype links from the basic directory."""
        print("Getting phenotype links...")
        response = self.session.get(self.basic_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        # Find all links that end with .html
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.endswith('.html'):
                # Join with basic directory
                full_url = urljoin(self.basic_url + '/', href)
                links.append(full_url)
        
        print(f"Found {len(links)} phenotype pages")
        return links

    def scrape_phenotype_page(self, url):
        """Scrape a single phenotype page."""
        try:
            print(f"Scraping: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract phenotype information
            phenotype_data = {
                'url': url,
                'name': '',
                'description': '',
                'images': []
            }
            
            # Extract name from the page title
            title = soup.find('title')
            if title:
                phenotype_data['name'] = title.text.strip().split(' - ')[0]
            
            # Extract description from the main content
            main_content = soup.find('div', class_='content') or soup.find('div', class_='main')
            if main_content:
                # Get all text paragraphs
                paragraphs = main_content.find_all('p')
                phenotype_data['description'] = ' '.join([p.text.strip() for p in paragraphs])
            
            # Extract images (only the first two person images, not maps)
            images = soup.find_all('img')
            person_images = []
            for img in images:
                if img.get('src'):
                    # Join with basic directory for image URLs
                    img_url = urljoin(self.basic_url + '/', img['src'])
                    # Skip map images (usually end with 's.jpg' or '.gif')
                    if not (img_url.endswith('s.jpg') or img_url.endswith('.gif')):
                        if img_url.endswith(('.jpg', '.jpeg', '.png')):
                            person_images.append(img_url)
                            if len(person_images) >= 2:  # Only take first two person images
                                break
            
            phenotype_data['images'] = person_images
            
            if phenotype_data['name'] and phenotype_data['images']:
                self.data.append(phenotype_data)
                print(f"Successfully scraped: {phenotype_data['name']}")
            else:
                print(f"No useful data found at {url}")
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")

    def save_data(self):
        """Save the scraped data and download images."""
        print("Saving scraped data...")
        # Save the scraped data
        with open('phenotype_data.json', 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        
        print("Downloading images...")
        # Create images directory if it doesn't exist
        os.makedirs('static/images', exist_ok=True)
        
        # Download images
        for phenotype in self.data:
            for img_url in phenotype['images']:
                try:
                    response = self.session.get(img_url)
                    if response.status_code == 200:
                        filename = os.path.basename(img_url)
                        with open(os.path.join('static/images', filename), 'wb') as f:
                            f.write(response.content)
                        print(f"Downloaded: {filename}")
                except Exception as e:
                    print(f"Error downloading {img_url}: {str(e)}")
                time.sleep(1)  # Be nice to the server

    def scrape_all(self):
        """Main method to scrape all phenotype pages."""
        links = self.get_phenotype_links()
        for link in links:
            self.scrape_phenotype_page(link)
            time.sleep(1)  # Be nice to the server
        self.save_data()

def scrape_veddid_only():
    scraper = PhenotypeScraper()
    veddid_url = 'http://humanphenotypes.net/basic/veddid.html'
    scraper.scrape_phenotype_page(veddid_url)
    # Save only the veddid data and images
    print("Saving scraped data for veddid...")
    with open('veddid_data.json', 'w', encoding='utf-8') as f:
        json.dump(scraper.data, f, ensure_ascii=False, indent=2)
    print("Downloading images for veddid...")
    os.makedirs('static/images', exist_ok=True)
    for phenotype in scraper.data:
        for img_url in phenotype['images']:
            try:
                response = scraper.session.get(img_url)
                if response.status_code == 200:
                    filename = os.path.basename(img_url)
                    with open(os.path.join('static/images', filename), 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {filename}")
            except Exception as e:
                print(f"Error downloading {img_url}: {str(e)}")
            time.sleep(1)

def main():
    scraper = PhenotypeScraper()
    scraper.scrape_all()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'veddid':
        scrape_veddid_only()
    else:
        main() 