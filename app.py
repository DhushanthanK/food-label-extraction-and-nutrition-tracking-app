from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
import os
import logging
from sqlalchemy.exc import SQLAlchemyError
from flask_migrate import Migrate
from dotenv import load_dotenv
from ocr import extract_nutrition_info  # Import the OCR function

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="http://localhost:5173") 
load_dotenv()

# Database configuration
username = os.getenv('DATABASE_USER', 'default_user')
password = os.getenv('DATABASE_PASSWORD', 'default_password')
host = os.getenv('DATABASE_HOST', 'localhost')
database = os.getenv('DATABASE_NAME', 'default_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{host}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# Logging configuration
logging.basicConfig(level=logging.DEBUG)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

class Nutrition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    servings_size = db.Column(db.String(100))
    servings_per_container = db.Column(db.String(100))
    calories_per_serving = db.Column(db.String(100))
    total_fat_amount = db.Column(db.String(100))
    total_fat_dv = db.Column(db.String(100))
    saturated_fat_amount = db.Column(db.String(100))
    saturated_fat_dv = db.Column(db.String(100))
    trans_fat_amount = db.Column(db.String(100))
    trans_fat_dv = db.Column(db.String(100))
    cholesterol_amount = db.Column(db.String(100))
    cholesterol_dv = db.Column(db.String(100))
    sodium_amount = db.Column(db.String(100))
    sodium_dv = db.Column(db.String(100))
    total_carbohydrates_amount = db.Column(db.String(100))
    total_carbohydrates_dv = db.Column(db.String(100))
    dietary_fiber_amount = db.Column(db.String(100))
    dietary_fiber_dv = db.Column(db.String(100))
    total_sugars_amount = db.Column(db.String(100))
    total_sugars_dv = db.Column(db.String(100))
    added_sugars_amount = db.Column(db.String(100))
    added_sugars_dv = db.Column(db.String(100))
    protein_amount = db.Column(db.String(100))
    protein_dv = db.Column(db.String(100))
    vitamin_d_amount = db.Column(db.String(100))
    vitamin_d_dv = db.Column(db.String(100))
    calcium_amount = db.Column(db.String(100))
    calcium_dv = db.Column(db.String(100))
    iron_amount = db.Column(db.String(100))
    iron_dv = db.Column(db.String(100))
    potassium_amount = db.Column(db.String(100))
    potassium_dv = db.Column(db.String(100))

    def __repr__(self):
        return f"<Nutrition {self.id}>"

# Helper function
def safe_get(data, key):
    return data.get(key) or ""

# API Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    # Check for existing user
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Hash the password
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Create user
    new_user = User(email=email, password_hash=password_hash)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if user and bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid email or password"}), 400

@app.route('/api/food_labels_db', methods=['GET'])
def get_food_labels_from_db():
    try:
        food_labels = Nutrition.query.all()
        result = [{
            'id': label.id,
            'servings_size': label.servings_size,
            'servings_per_container': label.servings_per_container,
            'calories_per_serving': label.calories_per_serving,
        } for label in food_labels]
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"message": "An error occurred"}), 500

@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"message": "No image file provided"}), 400
    
    image = request.files['image']
    image_path = os.path.join("uploads", image.filename)

    # Save the image
    image.save(image_path)

    # Extract nutrition info using OCR
    nutrition_data = extract_nutrition_info(image_path)

    if not nutrition_data:
        return jsonify({"message": "Failed to extract nutrition information"}), 500

    # Store nutrition data in the database
    new_nutrition = Nutrition(
        servings_size=nutrition_data.get('Serving Size'),
        servings_per_container=nutrition_data.get('Servings per container'),
        calories_per_serving=nutrition_data.get('Calories'),
        total_fat_amount=nutrition_data.get('Total Fat (Amount)'),
        total_fat_dv=nutrition_data.get('Total Fat (Daily Value)'),
        saturated_fat_amount=nutrition_data.get('Saturated Fat (Amount)'),
        saturated_fat_dv=nutrition_data.get('Saturated Fat (Daily Value)'),
        trans_fat_amount=nutrition_data.get('Trans Fat (Amount)'),
        trans_fat_dv=nutrition_data.get('Trans Fat (Daily Value)'),
        cholesterol_amount=nutrition_data.get('Cholesterol (Amount)'),
        cholesterol_dv=nutrition_data.get('Cholesterol (Daily Value)'),
        sodium_amount=nutrition_data.get('Sodium (Amount)'),
        sodium_dv=nutrition_data.get('Sodium (Daily Value)'),
        total_carbohydrates_amount=nutrition_data.get('Total Carbohydrates (Amount)'),
        total_carbohydrates_dv=nutrition_data.get('Total Carbohydrates (Daily Value)'),
        dietary_fiber_amount=nutrition_data.get('Dietary Fiber (Amount)'),
        dietary_fiber_dv=nutrition_data.get('Dietary Fiber (Daily Value)'),
        total_sugars_amount=nutrition_data.get('Total Sugars (Amount)'),
        total_sugars_dv=nutrition_data.get('Total Sugars (Daily Value)'),
        added_sugars_amount=nutrition_data.get('Added Sugars (Amount)'),
        added_sugars_dv=nutrition_data.get('Added Sugars (Daily Value)'),
        protein_amount=nutrition_data.get('Protein (Amount)'),
        protein_dv=nutrition_data.get('Protein (Daily Value)'),
        vitamin_d_amount=nutrition_data.get('Vitamin D (Amount)'),
        vitamin_d_dv=nutrition_data.get('Vitamin D (Daily Value)'),
        calcium_amount=nutrition_data.get('Calcium (Amount)'),
        calcium_dv=nutrition_data.get('Calcium (Daily Value)'),
        iron_amount=nutrition_data.get('Iron (Amount)'),
        iron_dv=nutrition_data.get('Iron (Daily Value)'),
        potassium_amount=nutrition_data.get('Potassium (Amount)'),
        potassium_dv=nutrition_data.get('Potassium (Daily Value)')
    )

    db.session.add(new_nutrition)
    db.session.commit()

    return jsonify({"message": "Nutrition information successfully uploaded and stored"}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)