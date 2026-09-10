import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request, session

# Load environment variables from .env file
load_dotenv()  

app = Flask(__name__)
API_KEY = os.getenv('OPENWEATHER_API_KEY')

# Set the secret key for session management
app.secret_key = os.getenv('SECRET_KEY')  

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather')
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

    if 'recent_searches' not in session: 
        session['recent_searches'] = []

    if city not in session['recent_searches']:
        session['recent_searches'].insert(0, city)
        
        # Keep only the last 5 searches
        session['recent_searches'] = session['recent_searches'][:5]  
        
        # Mark the session as modified to ensure it gets saved
        session.modified = True  

    return render_template('weather.html', city=city, temp=temp, feels_like=feels_like, condition=condition, humidity=humidity, icon=icon, recent_searches=session['recent_searches'], daily_forecast=daily_forecast, unit=unit)

@app.route('/weather/coords')
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

    if 'recent_searches' not in session:
        session['recent_searches'] = []

    return render_template('weather.html', city=city, temp=temp, feels_like=feels_like, condition=condition, humidity=humidity, icon=icon, recent_searches=session['recent_searches'], daily_forecast=daily_forecast, unit=unit)


if __name__ == '__main__':
    app.run(debug=False)