"""
Plant Disease Detection System
Base Flask Application (Existing System Reconstruction)

This represents the existing system before the AI Plant Care upgrade.
It provides:
- User registration and login
- Leaf image upload
- CNN-based disease classification
- Prediction history
- Reviews/feedback
"""

import os
import uuid
from datetime import datetime
from functools import wraps

from dotenv import load_dotenv
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, send_from_directory
)
from werkzeug.utils import secure_filename
import bcrypt
from pymongo import MongoClient
import numpy as np
from PIL import Image

load_dotenv()

# ---------------------------------------------------------------------------
# App Configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))

UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
MODEL_PATH = os.getenv('MODEL_PATH', 'models/plant_disease_model.h5')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IMG_SIZE = 224  # Model expects 224x224

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs('models', exist_ok=True)

# ---------------------------------------------------------------------------
# Database Connection
# ---------------------------------------------------------------------------
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'plant_disease_db')

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Collections
users_col = db['users']
predictions_col = db['predictions']
reviews_col = db['reviews']

# ---------------------------------------------------------------------------
# Class Labels — matches the trained model output order
# These are the classes the current model supports (PlantVillage subset)
# ---------------------------------------------------------------------------
CLASS_LABELS = [
    'Pepper__bell___Bacterial_spot',
    'Pepper__bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
]

# Human-readable names
CLASS_DISPLAY_NAMES = {
    'Pepper__bell___Bacterial_spot': 'Pepper Bell - Bacterial Spot',
    'Pepper__bell___healthy': 'Pepper Bell - Healthy',
    'Potato___Early_blight': 'Potato - Early Blight',
    'Potato___Late_blight': 'Potato - Late Blight',
    'Potato___healthy': 'Potato - Healthy',
}

# Basic disease information (existing system's static data)
DISEASE_INFO = {
    'Pepper__bell___Bacterial_spot': {
        'disease': 'Bacterial Spot',
        'crop': 'Pepper Bell',
        'description': 'Bacterial spot is caused by Xanthomonas campestris pv. vesicatoria. '
                       'It causes lesions on leaves, stems, and fruit.',
        'symptoms': [
            'Small, dark, water-soaked spots on leaves',
            'Spots may have yellow halos',
            'Leaves may drop prematurely',
            'Fruit spots are raised and scab-like',
        ],
        'treatment': [
            'Remove and destroy infected plant parts',
            'Apply copper-based bactericides',
            'Use disease-free seeds and transplants',
            'Practice crop rotation',
            'Avoid overhead irrigation',
        ],
    },
    'Pepper__bell___healthy': {
        'disease': 'Healthy',
        'crop': 'Pepper Bell',
        'description': 'The plant appears healthy with no visible signs of disease.',
        'symptoms': [],
        'treatment': [
            'Continue regular care and monitoring',
            'Maintain proper watering schedule',
            'Ensure adequate nutrition',
        ],
    },
    'Potato___Early_blight': {
        'disease': 'Early Blight',
        'crop': 'Potato',
        'description': 'Early blight is caused by the fungus Alternaria solani. '
                       'It is one of the most common potato diseases.',
        'symptoms': [
            'Dark brown to black concentric rings (target-like spots) on older leaves',
            'Yellowing around the spots',
            'Lower leaves affected first',
            'Premature leaf drop',
        ],
        'treatment': [
            'Remove infected leaves immediately',
            'Apply fungicides containing chlorothalonil or mancozeb',
            'Practice crop rotation (2-3 year cycle)',
            'Ensure adequate plant spacing for air circulation',
            'Avoid overhead watering',
            'Use certified disease-free seed potatoes',
        ],
    },
    'Potato___Late_blight': {
        'disease': 'Late Blight',
        'crop': 'Potato',
        'description': 'Late blight is caused by the oomycete Phytophthora infestans. '
                       'It is one of the most destructive potato diseases worldwide.',
        'symptoms': [
            'Water-soaked, pale green to dark brown lesions on leaves',
            'White fuzzy growth (sporangia) on the underside of leaves in humid conditions',
            'Rapid browning and death of foliage',
            'Firm, dark brown rot on tubers',
        ],
        'treatment': [
            'Destroy all infected plant material',
            'Apply fungicides preventatively (metalaxyl, mancozeb)',
            'Plant resistant varieties when available',
            'Avoid planting near previous potato or tomato fields',
            'Monitor weather for cool, wet conditions that favor the disease',
            'Consult local agricultural extension for current recommendations',
        ],
    },
    'Potato___healthy': {
        'disease': 'Healthy',
        'crop': 'Potato',
        'description': 'The plant appears healthy with no visible signs of disease.',
        'symptoms': [],
        'treatment': [
            'Continue regular care and monitoring',
            'Maintain proper watering schedule',
            'Hill soil around plants as they grow',
            'Monitor for signs of pests or disease',
        ],
    },
}

# ---------------------------------------------------------------------------
# Model Loading
# ---------------------------------------------------------------------------
model = None


def load_model():
    """Load the trained CNN model."""
    global model
    if model is not None:
        return model
    try:
        from tensorflow.keras.models import load_model as keras_load
        if os.path.exists(MODEL_PATH):
            model = keras_load(MODEL_PATH)
            print(f"[INFO] Model loaded from {MODEL_PATH}")
        else:
            print(f"[WARNING] Model file not found at {MODEL_PATH}. "
                  f"Predictions will use demo mode.")
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
    return model


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------
def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def preprocess_image(image_path):
    """
    Preprocess image for CNN inference.
    - Resize to 224x224
    - Normalize pixel values to [0, 1]
    """
    img = Image.open(image_path).convert('RGB')
    img = img.resize((IMG_SIZE, IMG_SIZE))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array


def predict_disease(image_path):
    """
    Run CNN inference on a preprocessed leaf image.
    Returns (predicted_class, confidence, all_predictions).
    """
    loaded_model = load_model()

    img_array = preprocess_image(image_path)

    if loaded_model is None:
        # Demo mode: return a random prediction for development
        import random
        idx = random.randint(0, len(CLASS_LABELS) - 1)
        confidence = round(random.uniform(0.70, 0.99), 4)
        return CLASS_LABELS[idx], confidence, {CLASS_LABELS[i]: round(random.uniform(0.01, 0.1), 4) for i in range(len(CLASS_LABELS))}

    predictions = loaded_model.predict(img_array)
    predicted_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][predicted_idx])
    predicted_class = CLASS_LABELS[predicted_idx]

    all_preds = {CLASS_LABELS[i]: float(predictions[0][i]) for i in range(len(CLASS_LABELS))}

    return predicted_class, confidence, all_preds


def login_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ---------------------------------------------------------------------------
# Routes — Authentication
# ---------------------------------------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        # Check if user exists
        if users_col.find_one({'email': email}):
            flash('Email already registered.', 'error')
            return render_template('register.html')

        # Hash password and save
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = {
            'name': name,
            'email': email,
            'password': hashed,
            'role': 'farmer',
            'created_at': datetime.utcnow(),
        }
        result = users_col.insert_one(user)

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        user = users_col.find_one({'email': email})
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_role'] = user.get('role', 'farmer')
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


# ---------------------------------------------------------------------------
# Routes — Pages
# ---------------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session['user_id']
    recent_predictions = list(
        predictions_col.find({'user_id': user_id})
        .sort('created_at', -1)
        .limit(5)
    )
    total_predictions = predictions_col.count_documents({'user_id': user_id})
    return render_template(
        'dashboard.html',
        predictions=recent_predictions,
        total_predictions=total_predictions,
    )


@app.route('/detect', methods=['GET', 'POST'])
@login_required
def detect():
    if request.method == 'POST':
        if 'leaf_image' not in request.files:
            flash('No image file selected.', 'error')
            return render_template('detect.html')

        file = request.files['leaf_image']
        if file.filename == '':
            flash('No image file selected.', 'error')
            return render_template('detect.html')

        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload a PNG or JPG image.', 'error')
            return render_template('detect.html')

        # Save uploaded file with unique name
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        file.save(filepath)

        try:
            # Validate it's actually an image
            img = Image.open(filepath)
            img.verify()
        except Exception:
            os.remove(filepath)
            flash('The uploaded file is not a valid image.', 'error')
            return render_template('detect.html')

        # Run prediction
        try:
            predicted_class, confidence, all_predictions = predict_disease(filepath)
        except Exception as e:
            flash(f'Prediction failed: {str(e)}', 'error')
            return render_template('detect.html')

        # Get disease info
        disease_info = DISEASE_INFO.get(predicted_class, {})
        display_name = CLASS_DISPLAY_NAMES.get(predicted_class, predicted_class)

        # Store prediction in database
        prediction_record = {
            'user_id': session['user_id'],
            'image_filename': filename,
            'predicted_class': predicted_class,
            'display_name': display_name,
            'confidence': confidence,
            'all_predictions': all_predictions,
            'disease_info': disease_info,
            'created_at': datetime.utcnow(),
        }
        result = predictions_col.insert_one(prediction_record)
        prediction_id = str(result.inserted_id)

        return redirect(url_for('result', prediction_id=prediction_id))

    return render_template('detect.html')


@app.route('/result/<prediction_id>')
@login_required
def result(prediction_id):
    from bson.objectid import ObjectId
    try:
        prediction = predictions_col.find_one({
            '_id': ObjectId(prediction_id),
            'user_id': session['user_id'],
        })
    except Exception:
        flash('Invalid prediction ID.', 'error')
        return redirect(url_for('history'))

    if not prediction:
        flash('Prediction not found.', 'error')
        return redirect(url_for('history'))

    return render_template('result.html', prediction=prediction)


@app.route('/history')
@login_required
def history():
    user_id = session['user_id']
    page = request.args.get('page', 1, type=int)
    per_page = 10

    total = predictions_col.count_documents({'user_id': user_id})
    predictions = list(
        predictions_col.find({'user_id': user_id})
        .sort('created_at', -1)
        .skip((page - 1) * per_page)
        .limit(per_page)
    )
    total_pages = (total + per_page - 1) // per_page

    return render_template(
        'history.html',
        predictions=predictions,
        page=page,
        total_pages=total_pages,
        total=total,
    )


@app.route('/reviews', methods=['GET', 'POST'])
@login_required
def reviews():
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment', '').strip()

        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5.', 'error')
        else:
            review = {
                'user_id': session['user_id'],
                'user_name': session['user_name'],
                'rating': rating,
                'comment': comment,
                'created_at': datetime.utcnow(),
            }
            reviews_col.insert_one(review)
            flash('Thank you for your review!', 'success')

    all_reviews = list(reviews_col.find().sort('created_at', -1).limit(20))
    return render_template('reviews.html', reviews=all_reviews)


# ---------------------------------------------------------------------------
# Routes — Static Files / Uploads
# ---------------------------------------------------------------------------
@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(UPLOAD_DIR, filename)


# ---------------------------------------------------------------------------
# Error Handlers
# ---------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 10MB.', 'error')
    return redirect(url_for('detect'))


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    load_model()
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    app.run(debug=debug, host='0.0.0.0', port=5000)
