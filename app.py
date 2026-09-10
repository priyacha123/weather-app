import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables from .env file
load_dotenv()  

app = Flask(__name__)
API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Set the secret key for session management
app.secret_key = os.getenv('SECRET_KEY')  

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to check the weather.'

class User(UserMixin, db.Model):
    id = db. Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        existing_user = User. query.filter((User.username == username) | (User.email == email)).first()

        if existing_user:
            flash('Username or email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')

        login_user(new_user)  # Log in the user immediately after registration
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/weather')
@login_required
def weather():
    city = request.args.get('city')
    unit = request.args.get('unit', 'metric')

    if not city:
        return render_template('error.html', message="Please enter a valid city name.")
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
    response = requests.get(url) # actually makes the API call
    data = response.json()


    if response.status_code != 200:
        return render_template('error.html', message=f"Could not find weather for '{city}'. Check the spelling.")

    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    condition = data['weather'][0]['description']
    humidity = data['main']['humidity']
    icon = data['weather'][0]['icon']

    # Fetch forecast data
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"
    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()

    daily_forecast = []
    for entry in forecast_data['list']:
        if '12:00:00' in entry['dt_txt']:
            daily_forecast.append({
                'date': entry['dt_txt'].split(' ')[0],
                'temp': entry['main']['temp'],
                'condition': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon']
            })

    # if 'recent_searches' not in session: 
    #     session['recent_searches'] = []

    # if city not in session['recent_searches']:
    #     session['recent_searches'].insert(0, city)
        
    #     # Keep only the last 5 searches
    #     session['recent_searches'] = session['recent_searches'][:5]  
        
    #     # Mark the session as modified to ensure it gets saved
    #     session.modified = True
    # 
    new_search = Search(city=city, user_id=current_user.id)
    db.session.add(new_search)
    db.session.commit()

    recent_searches = Search.query.filter_by(user_id=current_user.id).order_by(Search.timestamp.desc()).limit(5).all()
    recent_searches = [s.city for s in recent_searches]  

    return render_template('weather.html', city=city, temp=temp, feels_like=feels_like, condition=condition, humidity=humidity, icon=icon, recent_searches=recent_searches, daily_forecast=daily_forecast, unit=unit)

@app.route('/weather/coords')
@login_required
def weather_by_coords():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    unit = request.args.get('unit', 'metric')

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units={unit}"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return render_template('error.html', message="Could not detect weather for your location.")

    city = data['name']
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    condition = data['weather'][0]['description']
    humidity = data['main']['humidity']
    icon = data['weather'][0]['icon']

    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units={unit}"
    forecast_response = requests.get(forecast_url)
    forecast_data = forecast_response.json()

    daily_forecast = []
    for entry in forecast_data['list']:
        if '12:00:00' in entry['dt_txt']:
            daily_forecast.append({
                'date': entry['dt_txt'].split(' ')[0],
                'temp': entry['main']['temp'],
                'condition': entry['weather'][0]['description'],
                'icon': entry['weather'][0]['icon']
            })

    new_search = Search(city=city, user_id=current_user.id)
    db.session.add(new_search)
    db.session.commit()

    recent_searches = Search.query.filter_by(user_id=current_user.id).order_by(Search.timestamp.desc()).limit(5).all()
    recent_searches = [s.city for s in recent_searches]

    return render_template('weather.html', city=city, temp=temp, feels_like=feels_like, condition=condition, humidity=humidity, icon=icon, recent_searches=recent_searches, daily_forecast=daily_forecast, unit=unit)

if __name__ == '__main__':
    app.run(debug=False)