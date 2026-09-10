import os
import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

# Load environment variables from .env file
load_dotenv()  

app = Flask(__name__)
API_KEY = os.getenv('OPENWEATHER_API_KEY')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather')
def weather():
    city = request.args.get('city')

    if not city:
        return render_template('error.html', message="Please enter a valid city name.")
    
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url) # actually makes the API call
    data = response.json()


    if response.status_code != 200:
        return render_template('error.html', message=f"Could not find weather for '{city}'. Check the spelling.")

    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    condition = data['weather'][0]['description']
    humidity = data['main']['humidity']

    return render_template('weather.html', city=city, temp=temp, feels_like=feels_like, condition=condition, humidity=humidity)


if __name__ == '__main__':
    app.run(debug=True)