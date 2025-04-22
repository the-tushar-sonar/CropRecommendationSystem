from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import warnings
import pickle
import numpy as np
import pandas as pd

warnings.simplefilter(action='ignore', category=UserWarning)

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models after defining the app
from models import User, SoilData, Recommendation, db  

# Initialize SQLAlchemy with the app
db.init_app(app)  

# Flask-Login Setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Load ML Model & Scaler
with open('crop_recommendation_model.pkl', 'rb') as model_file:
    model = pickle.load(model_file)

with open('crop_recommendation_scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

# Function to validate input range
def validate_input(value, min_val, max_val):
    return min_val <= value <= max_val

# 🏠 Home Route
@app.route('/')
def home():
    return render_template('welcome.html')  # Ensure 'welcome.html' exists

# 📝 Form Page (GET & POST)
@app.route('/form', methods=['GET', 'POST'])
@login_required
def form():
    if request.method == 'POST':
        try:
            # Extract & Validate Input
            N = float(request.form['N'])
            P = float(request.form['P'])
            K = float(request.form['K'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])

            # Validate input ranges
            if not (validate_input(N, 0, 140) and validate_input(P, 5, 145) and 
                    validate_input(K, 5, 205) and validate_input(temperature, 8, 44) and
                    validate_input(humidity, 14, 100) and validate_input(ph, 3.5, 10) and 
                    validate_input(rainfall, 20, 300)):
                flash("Invalid input values. Please enter values within the allowed range.", "danger")
                return redirect(url_for('form'))

            # Preprocess Input for Model
            input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
            input_df = pd.DataFrame(input_data, columns=['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall'])
            scaled_input = scaler.transform(input_df)

            # Predict Crop Recommendation
            prediction = model.predict(scaled_input)
            recommended_crop = prediction[0]

            return render_template('result.html', crop=recommended_crop)

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('form'))

    return render_template('form.html')

# 🌱 Prediction Route
@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        # Extract Form Data
        N = float(request.form['N'])
        P = float(request.form['P'])
        K = float(request.form['K'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        # Validate Inputs
        if not (validate_input(N, 0, 140) and validate_input(P, 5, 145) and 
                validate_input(K, 5, 205) and validate_input(temperature, 8, 44) and
                validate_input(humidity, 14, 100) and validate_input(ph, 3.5, 10) and 
                validate_input(rainfall, 20, 300)):
            flash("Invalid input values. Please enter values within the allowed range.", "danger")
            return redirect(url_for('form'))

        # Preprocess Input
        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        scaled_input = scaler.transform(input_data)

        # Predict Crop Recommendation
        prediction = model.predict(scaled_input)
        recommended_crop = prediction[0]
        confidence_score = 1.0  # Placeholder confidence score

        # Store Data in Database
        soil_data = SoilData(
            user_id=current_user.id, nitrogen=N, phosphorus=P, potassium=K,
            temperature=temperature, humidity=humidity, ph=ph, rainfall=rainfall
        )
        db.session.add(soil_data)
        db.session.commit()

        recommendation = Recommendation(
            user_id=current_user.id, soil_data_id=soil_data.id,
            recommended_crop=recommended_crop, confidence_score=confidence_score
        )
        db.session.add(recommendation)
        db.session.commit()

        image_filename = f"images/crops/{recommended_crop.lower()}.jpg"

        return render_template("result.html", crop=recommended_crop, confidence=confidence_score, image_filename=image_filename)

    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect(url_for('form'))

# 🔐 User Authentication Routes

# 🚀 Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('form'))
        else:
            flash("Invalid email or password. Try again.", "danger")
    
    return render_template('login.html')

# 🚪 Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# 🆕 Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists. Please login.", "warning")
            return redirect(url_for('login'))

        # Add new user to database
        new_user = User(name=name, email=email, password=password)  
        db.session.add(new_user)
        db.session.commit()
        
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# 📊 Create Database Tables Before Running the App
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Ensures all tables exist
    app.run(debug=True, port=5007)
