import json
import random
import math
from flask import Flask, render_template, request, jsonify, session
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key

# Load phenotype data
def load_phenotype_data():
    with open('phenotype_locations.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    phenotypes = []
    current_phenotype = {}
    
    for line in content.split('\n'):
        if line.startswith('=== '):
            if current_phenotype:
                phenotypes.append(current_phenotype)
            current_phenotype = {'name': line.strip('= ')}
        elif line.startswith('Coordinates: '):
            coords = line.replace('Coordinates: ', '').split(',')
            current_phenotype['latitude'] = float(coords[0])
            current_phenotype['longitude'] = float(coords[1])
        elif line.startswith('Description: '):
            current_phenotype['description'] = line.replace('Description: ', '')
        elif line.startswith('- static/images/'):
            if 'images' not in current_phenotype:
                current_phenotype['images'] = []
            current_phenotype['images'].append(line.strip('- '))
    
    if current_phenotype:
        phenotypes.append(current_phenotype)
    
    return phenotypes

# Calculate distance between two points using Haversine formula
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = R * c
    
    return distance

# Calculate points based on distance
def calculate_points(distance):
    # Maximum points: 5000
    # Points decrease linearly with distance
    # No points after 5000 km
    max_distance = 5000  # km
    points = max(0, int(5000 * (1 - distance/max_distance)))
    return points

@app.route('/')
def index():
    # Get random phenotype
    phenotypes = load_phenotype_data()
    phenotype = random.choice(phenotypes)
    
    # Store phenotype in session for later verification
    session['current_phenotype'] = {
        'name': phenotype['name'],
        'latitude': phenotype['latitude'],
        'longitude': phenotype['longitude']
    }
    
    return render_template('game.html', 
                         phenotype=phenotype,
                         male_image=phenotype['images'][0],
                         female_image=phenotype['images'][1])

@app.route('/submit_guess', methods=['POST'])
def submit_guess():
    data = request.get_json()
    guess_lat = float(data['latitude'])
    guess_lon = float(data['longitude'])
    
    # Get actual coordinates from session
    phenotype = session.get('current_phenotype')
    if not phenotype:
        return jsonify({'error': 'No active game'}), 400
    
    actual_lat = phenotype['latitude']
    actual_lon = phenotype['longitude']
    
    # Calculate distance and points
    distance = calculate_distance(guess_lat, guess_lon, actual_lat, actual_lon)
    points = calculate_points(distance)
    
    return jsonify({
        'points': points,
        'distance': round(distance, 2),
        'actual_location': {
            'latitude': actual_lat,
            'longitude': actual_lon,
            'name': phenotype['name']
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002) 