import requests
import time
from datetime import datetime, timedelta

SERVICE_URL = "http://localhost:5001/weather"
CITY = "Rodez"
CACHE_DURATION = timedelta(minutes=10)

last_result = None
last_fetched = None

while True:
    try:
        now = datetime.utcnow()

        # Fait un nouvel appel seulement si plus vieux que CACHE_DURATION
        if not last_fetched or (now - last_fetched > CACHE_DURATION):
            response = requests.get(SERVICE_URL, params={"city": CITY})
            response.raise_for_status()
            last_result = response.json()
            last_fetched = now
            print(f"[{now}] ➜ Données reçues ({last_result.get('source')})")
        else:
            print(f"[{now}] ➜ Données en cache local (évite appel HTTP)")

        print(f"{CITY}: {last_result['temperature']}°C, "
              f"{last_result['windspeed']} km/h, "
              f"condition: {last_result['condition']}")
    except Exception as e:
        print(f"Erreur lors de la récupération des données : {e}")

    time.sleep(5)