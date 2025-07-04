# philibert.py
import requests
import time
import os
from flask import Flask, request, jsonify
from models import db, WeatherData
from datetime import datetime, timedelta

# Flask configuration
app = Flask(__name__)

# database environment variables
DB_USER = os.getenv('DB_USER', 'weather')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'weatherpass')
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'weather_db')


# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# database initialization
db.init_app(app)

# table creation
with app.app_context():
    db.create_all()

# interval configuration to avoid spamming
CACHE_DURATION_MINUTES = 10  
NORMAL_INTERVAL = 600 
ERROR_INTERVAL = 60 


#get date in DB
def get_cached_weather(city):
    with app.app_context():
        # get the most recent data for this city
        result = WeatherData.query.filter_by(city=city).order_by(WeatherData.timestamp.desc()).first()
        
        if result:
            # Check if the cached data is still valid
            time_diff = datetime.utcnow() - result.timestamp
            if time_diff < timedelta(minutes=CACHE_DURATION_MINUTES):
                print(f"Utilisation du cache pour {city}")
                print(f"Récupérées il y a {time_diff.total_seconds():.0f} secondes")
                return result
        
        return None

# call API
def fetch_fresh_weather(city):
    try:
        print("🌐 Appel API pour {city}...")
        
        # API call to get weather data (weather service)

        try:
            r = requests.get("http://localhost:5000/weather?city="+city)
            if r.status_code != 200:
                return jsonify({"error": "Erreur lors de l'appel à meteo"}), 502
            data= r.json()
        except requests.RequestException as e:
            return jsonify({"error": "Erreur lors de l'appel à open-meteo"}), 502
        
        weather = data.get("current_weather", {})
        weather_data = {
            "city": city,
            "temperature": weather.get("temperature"),
            "windspeed": weather.get("windspeed"),
            "condition":weather.get("weathercode", "inconnu")
        }
        
        print(f"Nouvelles données reçues: {weather_data}")
        
        # Stock in database
        with app.app_context():
            entry = WeatherData(
                city=weather_data["city"],
                temperature=weather_data["temperature"],
                windspeed=weather_data["windspeed"],
                condition=weather_data["condition"],
                timestamp=datetime.utcnow()
            )
            
            db.session.add(entry)
            db.session.commit()
            
            print(f"Données sauvegardées en BDD pour {city}")
            return entry
            
    except Exception as e:
        print(f"Erreur lors de l'appel API: {e}")
        return None

def get_weather_intelligently(city):
    
    # Try with cache data
    cached_data = get_cached_weather(city)
    if cached_data:
        return cached_data, False
    
    #Call API
    print(f"Cache expiré ou inexistant pour {city}")
    fresh_data = fetch_fresh_weather(city)
    
    if fresh_data:
        return fresh_data, True
    else:
        # In case of error, try to take the last informations about the city
        print(f"Tentative de récupération de la dernière donnée connue pour {city}")
        with app.app_context():
            last_known = WeatherData.query.filter_by(city=city).order_by(WeatherData.timestamp.desc()).first()
            if last_known:
                print(f"Utilisation des dernières données connues (âge: {datetime.utcnow() - last_known.timestamp})")
                return last_known, True
        
        return None, True
    

if __name__ == "__main__":
    city = "Rodez"
    print(f"Démarrage du client météo intelligent pour {city}")
    print(f"Configuration: Cache {CACHE_DURATION_MINUTES}min, Intervalle {NORMAL_INTERVAL//60}min")
    
    while True:
        try:
            print(f"\n{datetime.now().strftime('%H:%M:%S')} - Vérification météo...")
            
            # Récupération intelligente des données
            weather_data, needs_long_wait = get_weather_intelligently(city)
            
            if weather_data:
                print(f"Météo actuelle à {weather_data.city}:")
                print(f"   • Température: {weather_data.temperature}°C")
                print(f"   • Conditions: {weather_data.condition}")
                print(f"   • Vent: {weather_data.windspeed} km/h")
                print(f"   • Dernière mise à jour: {weather_data.timestamp}")
                
                
                # Attente intelligente selon qu'on ait utilisé l'API ou le cache
                wait_time = NORMAL_INTERVAL if needs_long_wait else ERROR_INTERVAL
                
            else:
                print("Impossible de récupérer les données météo")
                wait_time = ERROR_INTERVAL
            
            print(f"⏳ Prochaine vérification dans {wait_time//60} minutes...")
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\nArrêt demandé par l'utilisateur")
            break
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            print(f"Nouvelle tentative dans {ERROR_INTERVAL//60} minute(s)...")
            time.sleep(ERROR_INTERVAL)