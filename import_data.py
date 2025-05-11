import json
from app import app, db, Image

def import_data():
    # Read the scraped data
    with open('phenotype_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Import each phenotype
        for phenotype in data:
            # Skip if no images
            if not phenotype['images']:
                continue
                
            # Use the first image as the main image
            image_filename = phenotype['images'][0].split('/')[-1]
            
            # Extract location coordinates from description or location
            # This is a placeholder - you'll need to implement proper coordinate extraction
            # based on the actual data format
            lat = 0.0  # Replace with actual latitude
            lng = 0.0  # Replace with actual longitude
            
            # Create new image record
            new_image = Image(
                filename=image_filename,
                latitude=lat,
                longitude=lng,
                location_name=phenotype['location'] or phenotype['name'],
                description=phenotype['description']
            )
            
            try:
                db.session.add(new_image)
                db.session.commit()
                print(f"Imported: {image_filename}")
            except Exception as e:
                print(f"Error importing {image_filename}: {str(e)}")
                db.session.rollback()

if __name__ == "__main__":
    import_data() 