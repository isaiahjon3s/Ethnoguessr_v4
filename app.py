from flask import Flask, render_template, request, jsonify
import json
import os
from math import radians, sin, cos, sqrt, atan2
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ethnoguessr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), unique=True, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'lat': self.latitude,
            'lng': self.longitude,
            'location': self.location_name,
            'description': self.description
        }

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    # Get a random image from the database
    image = Image.query.order_by(db.func.random()).first()
    if not image:
        return "No images available in the database", 404
    return render_template('game.html', image=image.to_dict())

@app.route('/check_guess', methods=['POST'])
def check_guess():
    data = request.get_json()
    image_id = data.get('image_id')
    guess_lat = float(data.get('lat'))
    guess_lng = float(data.get('lng'))

    image = Image.query.get_or_404(image_id)
    distance = calculate_distance(guess_lat, guess_lng, image.latitude, image.longitude)
    
    # Calculate score (max 5000 points, decreasing with distance)
    score = max(0, int(5000 * (1 - distance/20000)))  # 20000km is max distance

    return jsonify({
        'score': score,
        'actual_location': image.location_name,
        'distance': round(distance, 2)
    })

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/admin/add_image', methods=['POST'])
def add_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the image file
    filename = file.filename
    file.save(os.path.join('static/images', filename))

    # Create new image record
    new_image = Image(
        filename=filename,
        latitude=float(request.form['latitude']),
        longitude=float(request.form['longitude']),
        location_name=request.form['location_name'],
        description=request.form.get('description', '')
    )

    db.session.add(new_image)
    db.session.commit()

    return jsonify({'message': 'Image added successfully', 'image': new_image.to_dict()})

# Create the database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 