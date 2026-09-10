# 🌤️ Flask Weather App

A simple weather lookup app built with Flask, using the OpenWeatherMap API to show current conditions and a 5-day forecast for any city — or your current location.

**Live demo:** _add your Render URL here_

## Features

- Search weather by city name
- Current temperature, "feels like", condition, and humidity
- 5-day forecast strip with icons
- °C / °F unit toggle
- "Use my location" button (browser geolocation)
- Recent searches list (stored in session)
- Error handling for invalid cities and empty input

## Tech Stack

- **Backend:** Flask (Python)
- **Templating:** Jinja2
- **Styling:** Bootstrap 5
- **API:** OpenWeatherMap (current weather + 5-day forecast endpoints)
- **Deployment:** Render, with Gunicorn as the production server

## Project Structure

```
flask-weather-app/
├── app.py
├── requirements.txt
├── Procfile
├── .env                
├── .gitignore
└── templates/
    ├── base.html
    ├── index.html
    ├── weather.html
    └── error.html
```

## Running Locally

1. Clone the repo and move into it:
   ```
   git clone https://github.com/your-username/flask-weather-app.git
   cd flask-weather-app
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```
   OPENWEATHER_API_KEY=your_key_here
   SECRET_KEY=any_random_string
   ```
   Get a free API key at [openweathermap.org](https://openweathermap.org/).

5. Run the app:
   ```
   python app.py
   ```
   Visit `http://127.0.0.1:5000`.
