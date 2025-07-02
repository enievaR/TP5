from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    windspeed = db.Column(db.Float)
    condition = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)