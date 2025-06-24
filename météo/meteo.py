from flask import Flask, request, jsonify
from flasgger import Swagger
import requests

app = Flask(__name__)
swagger = Swagger(app)

known_cities = {
  "Rodez": (44.35, 2.57),
  "Honolulu": (21.30, -157.85),
  "Tombouctou": (16.77, -3.01)
}

@app.route('/weather')
def get_weather():
  city = request.args.get('city')
  print(city, flush=True)
  if city not in known_cities:
    return jsonify({"error": "Ville inconnue"}), 404

  lat, lon = known_cities[city]
  url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
  try:
    response = requests.get(url)
    if response.status_code != 200:
      return jsonify({"error": "Erreur lors de l'appel à open-meteo"}), 502
    data = response.json()
  except Exception as e:
    return jsonify({"error": "Erreur lors de l'appel à open-meteo"}), 502

  weather = data.get("current_weather", {})
  return jsonify({
    "city": city,
    "temperature": weather.get("temperature"),
    "windspeed": weather.get("windspeed"),
    "condition": weather.get("weathercode", "inconnu")
  })

@app.route('/cities')
def get_cities():
  return jsonify({"available_cities": list(known_cities.keys())})

if __name__ == '__main__':
  app.run(debug=True, host='0.0.0.0', port=5000)
