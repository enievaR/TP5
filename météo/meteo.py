from flask import Flask, request, jsonify
from flasgger import Swagger

app = Flask(__name__)
swagger = Swagger(app)

known_cities = {
    "Rodez": (44.35, 2.57),
    "Honolulu": (21.30, -157.85),
    "Tombouctou": (16.77, -3.01)
}

@app.route('/weather')
def get_weather():
    """
    Obtenir la météo actuelle d'une ville
    ---
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: Nom de la ville (Rodez, Honolulu, Tombouctou)
    responses:
      200:
        description: Météo de la ville
        schema:
          type: object
          properties:
            city:
              type: string
            temperature:
              type: number
            windspeed:
              type: number
            condition:
              type: string
      404:
        description: Ville inconnue
        schema:
          type: object
          properties:
            error:
              type: string
    """
    city = request.json.get('city')
    print(city, flush=True)
    if city not in known_cities:
        return jsonify({"error": "Ville inconnue"}), 404

    lat, lon = known_cities[city]
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    resp = request.get(url)
    if resp.status_code != 200:
        return jsonify({"error": "Erreur lors de l'appel à open-meteo"}), 502

    data = resp.json()
    weather = data.get("current_weather", {})
    # Pour simplifier, on ne traduit pas la condition météo ici
    return jsonify({
        "city": city,
        "temperature": weather.get("temperature"),
        "windspeed": weather.get("windspeed"),
        "condition": weather.get("weathercode", "inconnu")
    })

@app.route('/cities')
def get_cities():
    """
    Liste des villes supportées
    ---
    responses:
      200:
        description: Liste des villes
        schema:
          type: object
          properties:
            available_cities:
              type: array
              items:
                type: string
    """
    return jsonify({"available_cities": list(known_cities.keys())})

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)
