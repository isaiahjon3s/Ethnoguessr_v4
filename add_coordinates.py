import json
import os

# Dictionary mapping phenotype names to their approximate coordinates
# Format: (latitude, longitude)
PHENOTYPE_COORDINATES = {
    "Ainuid": (42.5, 141.5),  # Hokkaido, Japan
    "Alpinid": (46.0, 7.0),   # Swiss Alps
    "Amazonid": (-3.0, -60.0), # Amazon Basin
    "Andid": (-13.0, -72.0),  # Andes Mountains
    "Armenoid": (40.0, 44.0), # Armenia
    "Australid": (-25.0, 133.0), # Australia
    "Bambutid": (1.0, 29.0),  # Congo Basin
    "Bantuid": (-2.0, 23.0),  # Central Africa
    "Centralid": (35.0, 105.0), # Central China
    "Congolid": (-1.0, 15.0), # Congo
    "Dinarid": (44.0, 17.0),  # Balkans
    "East Europid": (55.0, 35.0), # Eastern Europe
    "Eskimid": (70.0, -100.0), # Arctic
    "Ethiopid": (9.0, 38.0),  # Ethiopia
    "Indid": (20.0, 77.0),    # India
    "Indo Melanid": (7.0, 80.0), # Sri Lanka
    "Khoid": (-22.0, 17.0),   # Namibia
    "Lagid": (15.0, 18.0),    # Chad
    "Lappid": (69.0, 27.0),   # Lapland
    "Margid": (25.0, 55.0),   # Arabian Peninsula
    "Mediterranid": (38.0, 15.0), # Mediterranean
    "Melanesid": (-6.0, 155.0), # Melanesia
    "Negritid": (7.0, 125.0), # Philippines
    "Nilotid": (4.0, 32.0),   # South Sudan
    "Nordid": (60.0, 15.0),   # Scandinavia
    "Orientalid": (35.0, 105.0), # East Asia
    "Pacifid": (-13.0, -172.0), # Pacific Islands
    "Patagonid": (-50.0, -70.0), # Patagonia
    "Polynesid": (-17.0, -149.0), # Polynesia
    "Sanid": (-22.0, 20.0),   # Kalahari
    "Sibirid": (60.0, 100.0), # Siberia
    "Silvid": (55.0, 105.0),  # Eastern Siberia
    "Sinid": (35.0, 105.0),   # China
    "South Mongolid": (45.0, 105.0), # Mongolia
    "Sudanid": (15.0, 30.0),  # Sudan
    "Tungid": (50.0, 120.0),  # Eastern Siberia
    "Turanid": (45.0, 60.0),  # Central Asia
    "Veddid": (10.0, 77.0),   # South India
}

def process_data():
    # Read the phenotype data
    with open('phenotype_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create output file
    with open('phenotype_locations.txt', 'w', encoding='utf-8') as f:
        for phenotype in data:
            name = phenotype['name']
            # Get coordinates
            coords = PHENOTYPE_COORDINATES.get(name, (0.0, 0.0))
            
            # Write header
            f.write(f"=== {name} ===\n")
            f.write(f"Coordinates: {coords[0]}, {coords[1]}\n")
            f.write(f"Description: {phenotype['description']}\n")
            f.write("Images:\n")
            
            # Write image paths
            for img_url in phenotype['images']:
                filename = os.path.basename(img_url)
                base_name = filename[:-5]  # Remove 'm.jpg' or 'f.jpg'
                f.write(f"- static/images/{base_name}/{filename}\n")
            
            f.write("\n")  # Add blank line between entries

if __name__ == "__main__":
    process_data()
    print("Created phenotype_locations.txt with coordinates and image paths") 