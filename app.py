from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
import random
from math import radians, sin, cos, sqrt, atan2
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ethnoguessr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/game')
def game():
    # Initialize game session if not exists
    if 'game_state' not in session:
        session['game_state'] = {
            'round': 1,
            'total_score': 0,
            'scores': []
        }
    
    # Check if game is complete
    if session['game_state']['round'] > 10:
        return redirect(url_for('game_complete'))
    
    # Get random phenotype
    phenotypes = load_phenotype_data()
    phenotype = random.choice(phenotypes)
    
    # Store phenotype in session for later verification
    session['current_phenotype'] = {
        'name': phenotype['name'],
        'latitude': phenotype['latitude'],
        'longitude': phenotype['longitude']
    }
    
    return render_template('game_play.html', 
                         phenotype_name=phenotype['name'],
                         description=phenotype['description'],
                         male_image=phenotype['images'][0],
                         female_image=phenotype['images'][1],
                         current_round=session['game_state']['round'],
                         total_rounds=10)

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
    points = max(0, int(5000 * (1 - distance/20000)))  # 20000km is max distance
    
    # Update game state
    game_state = session['game_state']
    game_state['total_score'] += points
    game_state['scores'].append(points)
    
    # Check if this was the last round
    if game_state['round'] == 10:
        game_state['round'] += 1
        session['game_state'] = game_state
        return jsonify({
            'points': points,
            'distance': round(distance, 2),
            'actual_location': {
                'latitude': actual_lat,
                'longitude': actual_lon,
                'name': phenotype['name']
            },
            'current_round': 10,
            'total_rounds': 10,
            'total_score': game_state['total_score'],
            'game_complete': True
        })
    
    game_state['round'] += 1
    session['game_state'] = game_state
    
    return jsonify({
        'points': points,
        'distance': round(distance, 2),
        'actual_location': {
            'latitude': actual_lat,
            'longitude': actual_lon,
            'name': phenotype['name']
        },
        'current_round': game_state['round'],
        'total_rounds': 10,
        'total_score': game_state['total_score'],
        'game_complete': False
    })

@app.route('/game_complete')
def game_complete():
    if 'game_state' not in session:
        return redirect(url_for('index'))
    
    game_state = session['game_state']
    average_score = game_state['total_score'] / 10
    
    return render_template('game_complete.html',
                         total_score=game_state['total_score'],
                         average_score=round(average_score, 2),
                         scores=game_state['scores'])

@app.route('/reset_game')
def reset_game():
    session.pop('game_state', None)
    return redirect(url_for('game'))

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points on Earth using the Haversine formula."""
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return distance

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 