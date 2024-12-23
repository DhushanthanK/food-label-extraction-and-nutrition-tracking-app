from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt 
import os
import logging
from flask_migrate import Migrate
from dotenv import load_dotenv
import ocr  
import label_detection

app = Flask(__name__)
CORS(app)  

load_dotenv()

username = os.getenv('DATABASE_USER', 'default_user')
password = os.getenv('DATABASE_PASSWORD', 'default_password')
host = os.getenv('DATABASE_HOST', 'localhost')
database = os.getenv('DATABASE_NAME', 'default_db')

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{username}:{password}@{host}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.DEBUG)

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

def safe_get(data, key):
    return data.get(key) or ""

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

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
            'total_fat_amount': label.total_fat_amount,
            'total_fat_dv': label.total_fat_dv,
            'saturated_fat_amount': label.saturated_fat_amount,
            'saturated_fat_dv': label.saturated_fat_dv,
            'trans_fat_amount': label.trans_fat_amount,
            'trans_fat_dv': label.trans_fat_dv,
            'cholesterol_amount': label.cholesterol_amount,
            'cholesterol_dv': label.cholesterol_dv,
            'sodium_amount': label.sodium_amount,
            'sodium_dv': label.sodium_dv,
            'total_carbohydrates_amount': label.total_carbohydrates_amount,
            'total_carbohydrates_dv': label.total_carbohydrates_dv,
            'dietary_fiber_amount': label.dietary_fiber_amount,
            'dietary_fiber_dv': label.dietary_fiber_dv,
            'total_sugars_amount': label.total_sugars_amount,
            'total_sugars_dv': label.total_sugars_dv,
            'added_sugars_amount': label.added_sugars_amount,
            'added_sugars_dv': label.added_sugars_dv,
            'protein_amount': label.protein_amount,
            'protein_dv': label.protein_dv,
            'vitamin_d_amount': label.vitamin_d_amount,
            'vitamin_d_dv': label.vitamin_d_dv,
            'calcium_amount': label.calcium_amount,
            'calcium_dv': label.calcium_dv,
            'iron_amount': label.iron_amount,
            'iron_dv': label.iron_dv,
            'potassium_amount': label.potassium_amount,
            'potassium_dv': label.potassium_dv
        } for label in food_labels]
        return jsonify(result), 200
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"message": "An error occurred"}), 500

@app.route('/api/food_labels_db', methods=['POST'])
def upload_food_label():
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files['file']

    file_path = f"uploads/{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)

    cropped_image_path = f"cropped_image/{file.filename}"
    os.makedirs("cropped_image", exist_ok=True)

    try:
        cropped_image = label_detection.crop_label(file_path)
        cropped_image.save(cropped_image_path)
        
        if cropped_image:
            nutrition_data = ocr.extract_nutrition_info(cropped_image)
        else:
            print("No cropped image available.")

        servings_size=nutrition_data.get("Serving Size")
        servings_per_container=nutrition_data.get("Servings per Container")
        calories_per_serving=nutrition_data.get("Calories")
        total_fat_amount=nutrition_data.get("Total Fat (Amount)")
        total_fat_dv=nutrition_data.get("Total Fat (Daily Value)")
        saturated_fat_amount=nutrition_data.get("Saturated Fat (Amount)")
        saturated_fat_dv=nutrition_data.get("Saturated Fat (Daily Value)")
        trans_fat_amount=nutrition_data.get("Trans Fat (Amount)")
        trans_fat_dv=nutrition_data.get("Trans Fat (Daily Value)")
        cholesterol_amount=nutrition_data.get("Cholesterol (Amount)")
        cholesterol_dv=nutrition_data.get("Cholesterol (Daily Value)")
        sodium_amount=nutrition_data.get("Sodium (Amount)")
        sodium_dv=nutrition_data.get("Sodium (Daily Value)")
        total_carbohydrates_amount=nutrition_data.get("Total Carbohydrates (Amount)")
        total_carbohydrates_dv=nutrition_data.get("Total Carbohydrates (Daily Value)")
        dietary_fiber_amount=nutrition_data.get("Dietary Fiber (Amount)")
        dietary_fiber_dv=nutrition_data.get("Dietary Fiber (Daily Value)")
        total_sugars_amount=nutrition_data.get("Total Sugars (Amount)")
        total_sugars_dv=nutrition_data.get("Total Sugars (Daily Value)")
        added_sugars_amount=nutrition_data.get("Added Sugars (Amount)")
        added_sugars_dv=nutrition_data.get("Added Sugars (Daily Value)")
        protein_amount=nutrition_data.get("Protein (Amount)")
        protein_dv=nutrition_data.get("Protein (Daily Value)")
        vitamin_d_amount=nutrition_data.get("Vitamin D (Amount)")
        vitamin_d_dv=nutrition_data.get("Vitamin D (Daily Value)")
        calcium_amount=nutrition_data.get("Calcium (Amount)")
        calcium_dv=nutrition_data.get("Calcium (Daily Value)")
        iron_amount=nutrition_data.get("Iron (Amount)")
        iron_dv=nutrition_data.get("Iron (Daily Value)")
        potassium_amount=nutrition_data.get("Potasium (Amount)")
        potassium_dv=nutrition_data.get("Potasium (Daily Value)")

        new_entry = Nutrition(
            servings_size=servings_size,
            servings_per_container=servings_per_container,
            calories_per_serving=calories_per_serving,
            total_fat_amount=total_fat_amount,
            total_fat_dv=total_fat_dv,
            saturated_fat_amount=saturated_fat_amount,
            saturated_fat_dv=saturated_fat_dv,
            trans_fat_amount=trans_fat_amount,
            trans_fat_dv=trans_fat_dv,
            cholesterol_amount=cholesterol_amount,
            cholesterol_dv=cholesterol_dv,
            sodium_amount=sodium_amount,
            sodium_dv=sodium_dv,
            total_carbohydrates_amount=total_carbohydrates_amount,
            total_carbohydrates_dv=total_carbohydrates_dv,
            dietary_fiber_amount=dietary_fiber_amount,
            dietary_fiber_dv=dietary_fiber_dv,
            total_sugars_amount=total_sugars_amount,
            total_sugars_dv=total_sugars_dv,
            added_sugars_amount=added_sugars_amount,
            added_sugars_dv=added_sugars_dv,
            protein_amount=protein_amount,
            protein_dv=protein_dv,
            vitamin_d_amount=vitamin_d_amount,
            vitamin_d_dv=vitamin_d_dv,
            calcium_amount=calcium_amount,
            calcium_dv=calcium_dv,
            iron_amount=iron_amount,
            iron_dv=iron_dv,
            potassium_amount=potassium_amount,
            potassium_dv=potassium_dv
        )
        db.session.add(new_entry)
        db.session.commit()

        return jsonify({"message": "File processed and data saved successfully"}), 200
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return jsonify({"message": "Failed to process the file"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)

