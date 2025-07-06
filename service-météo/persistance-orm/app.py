from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import requests

from models import db, WeatherData

app = Flask(__name__)

# Config DB via .env
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Démarrage : créer les tables si nécessaires
with app.app_context():
    db.create_all()

# URL de ton service météo existant
WEATHER_SERVICE_URL = 'http://weather:5000/weather'

@app.route('/weather')
def cached_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "Paramètre 'city' manquant"}), 400

    # Vérifie cache
    data = WeatherData.query.filter_by(city=city).order_by(WeatherData.timestamp.desc()).first()
    if data and (datetime.utcnow() - data.timestamp) < timedelta(minutes=10):
        return jsonify({
            "city": data.city,
            "temperature": data.temperature,
            "windspeed": data.windspeed,
            "condition": data.condition,
            "source": "cache"
        })

    try:
        r = requests.get(WEATHER_SERVICE_URL, params={"city": city})
        r.raise_for_status()
        w = r.json()
    except Exception as e:
        return jsonify({"error": f"Erreur appel service météo : {e}"}), 502

    # Sauvegarde en DB
    new = WeatherData(
        city=w.get("city"),
        temperature=w.get("temperature"),
        windspeed=w.get("windspeed"),
        condition=w.get("condition"),
        timestamp=datetime.utcnow()
    )
    db.session.add(new)
    db.session.commit()

    return jsonify({**w, "source": "service"})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
            