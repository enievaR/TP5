from flask import Flask
from models import db
from models import WeatherData
from datetime import datetime

app = Flask(__name__)

# Config depuis les variables d'environnement
app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialisation
db.init_app(app)

# Création des tables (à faire une fois)
with app.app_context():
    db.create_all()

    entry = WeatherData(
    city="Rodez",
    temperature=22.5,
    windspeed=10.4,
    condition="nuageux",
    timestamp=datetime.utcnow()
    )
    db.session.add(entry)
    db.session.commit()

    result = WeatherData.query.filter_by(city="Rodez").first()
    print(f"Weather in {result.city}: {result.temperature}°C, {result.windspeed} km/h, {result.condition}")
