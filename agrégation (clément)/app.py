# -------------------- IMPORTS -------------------- #
from flask import Flask, request, jsonify
from flasgger import Swagger
import requests
# ------------------------------------------------- #

app = Flask(__name__)
swagger = Swagger(app)

# -------------------- METHODES GET -------------------- #

@app.route("/fullinfo", methods=["GET"])
def get_fullinfo():
    '''
    Récupère la météo et une blague pour une ville donnée
    ---
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: Ville dont on veut la météo
        example: Rodez
    responses:
      200:
        description: Données combinées de météo et blague
        examples:
          application/json:
            {
              "city": "Rodez",
              "weather": {
                "temperature": 21.2,
                "condition": "nuageux"
              },
              "joke": "Où est caché le canard ? Dans le coin."
            }
      400:
        description: Paramètre manquant
      502:
        description: Erreur d’un des services
    '''
    city = request.args.get("city")
    if not city:
        return jsonify({"error": "Paramètre 'city' manquant"}), 400

    try:
        weather_resp = requests.get(f"http://weather:5000/weather?city={city}", timeout=5)
        weather_data = weather_resp.json()
    except Exception as e:
        return jsonify({"error": f"Service météo indisponible : {str(e)}"}), 502

    try:
        joke_resp = requests.get("http://jokes:5000/joke", timeout=5)
        joke_data = joke_resp.json()
    except Exception as e:
        return jsonify({"error": f"Service blague indisponible : {str(e)}"}), 502

    return jsonify({
        "city": city,
        "weather": weather_data,
        "joke": joke_data.get("joke")
    }), 200

@app.route("/weather", methods=["GET"])
def proxy_weather():
    '''
    Proxy vers le service météo
    ---
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: Ville pour la météo
        example: Rodez
    responses:
      200:
        description: Réponse brute du service météo
      400:
        description: Ville inconnue
      502:
        description: Service météo indisponible
    '''
    city = request.args.get("city")
    try:
        r = requests.get(f"http://weather:5000/weather?city={city}", timeout=5)
        return r.content, r.status_code, r.headers.items()
    except Exception:
        return jsonify({"error": "Service météo indisponible"}), 502

@app.route("/joke", methods=["GET"])
def proxy_joke():
    '''
    Proxy vers le service de blagues
    ---
    responses:
      200:
        description: Une blague aléatoire
        examples:
          application/json:
            {
              "joke": "Quel est le jeu préféré des canards ? La coinche."
            }
      502:
        description: Service blague indisponible
    '''
    try:
        r = requests.get("http://jokes:5000/joke", timeout=5)
        return r.content, r.status_code, r.headers.items()
    except Exception:
        return jsonify({"error": "Service blague indisponible"}), 502
    
# ------------------------------------------------- #

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
