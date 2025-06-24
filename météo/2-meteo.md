---
titre: Architecture micro-service
sous-titre: TP 5 - Premiers micro-services - Météo
auteur: Philippe \textsc{Roussille}
theme: Warsaw
lang: fr-FR
section-titles: false
fontsize: 10pt
couleur-type-1: true
rendu-type: papier
rendu-logo: 3il
---

# Présentation du cadre

> *"Ginette, tu crois qu’il fera beau à Tombouctou ?"*
> *"Aucune idée Roger... mais on va devoir le savoir, maintenant qu’on ouvre une succursale là-bas !"*

Après avoir construit un microservice autonome pour les blagues, CanaDuck ouvre deux nouvelles succursales : l'une à **Honolulu**, l'autre à **Tombouctou**. Impossible de gérer correctement les horaires et les conditions d'expédition sans savoir s'il fait beau ou non.

CanaDuck se penche donc sur un **service météo**, capable de répondre aux demandes internes sur les conditions climatiques à différents endroits du monde.. Mais cette fois, pas question de tout coder à la main : on va **interroger un service externe déjà existant** pour récupérer les prévisions !

La météo sera récupérée depuis l'API publique de [https://open-meteo.com](https://open-meteo.com), et restituée de manière simple depuis un microservice Flask.

# Fonctionnalités attendues

Le microservice doit :

1. Exposer une route :

  ```
  GET /weather?city=Rodez
  ```

- Utiliser un dictionnaire interne pour convertir le nom de la ville en coordonnées (lat, lon)
- Interroger l'API `https://api.open-meteo.com/v1/forecast?latitude=...&longitude=...&current_weather=true`
- Retourner un JSON simplifié avec :

```json
{
  "city": "Rodez",
  "temperature": 21.3,
  "windspeed": 15.2,
  "condition": "partiellement nuageux"
}
```

Si la ville n'est pas supportée :

```json
{
  "error": "Ville inconnue"
}
```

2. Exposer une deuxième route :

  ```
  GET /cities
  ```

  qui renvoie la liste des villes disponibles, par exemple :

  ```json
  {
    "available_cities": ["Rodez", "Honolulu", "Tombouctou"]
  }
  ```

## Données des villes supportées

Créez un petit dictionnaire Python :

```python
known_cities = {
    "Rodez": (44.35, 2.57),
    "Honolulu": (21.30, -157.85),
    "Tombouctou": (16.77, -3.01)
}
```

# Ça peut vous être utile ?

Héhé, vous avez déjà vu tout le code utile à cette partie... regardez donc les TPs précédents ! ;)

# Quelques questions de fond

1. Pourquoi ne pas appeler directement open-meteo depuis le navigateur ?  
On va pas passer par un navigateur à chaque fois qu'on veut connaître la météo, surtout pour une application interne. On utilise un microservice pour centraliser les appels et éviter de surcharger le service externe avec des requêtes directes depuis le client.
2. Quel est l'avantage de passer par un microservice intermédiaire ?  
On peut centraliser la logique métier, gérer les erreurs, et simplifier l'interface pour les autres services ou applications qui consomment cette API. Cela permet aussi de changer facilement le service météo sous-jacent sans impacter les consommateurs.
3. Si le format de réponse de `open-meteo` change, que se passe-t-il ?  
Si le format de réponse de `open-meteo` change, le microservice devra être mis à jour pour s'adapter à ce nouveau format. Cela peut nécessiter des modifications dans la logique de traitement des données et potentiellement dans la structure du JSON retourné aux consommateurs.
4. Que pourrait-on ajouter pour rendre ce service plus complet ou plus robuste ?  
On pourrait ajouter des fonctionnalités comme la gestion des erreurs plus détaillée, la mise en cache des résultats pour éviter les appels répétés au service externe, ou encore une documentation automatique de l'API. On pourrait aussi envisager d'ajouter des tests unitaires pour garantir le bon fonctionnement du service.

# Dockerisation obligatoire

Pour que ce service soit déployable facilement par l’équipe (et notamment par Paul et Patrice qui refusent d’installer Flask à la main), vous devez le dockeriser.

Pour cela, inspirez vous de ce qui a été fait dans le TP sur le générateur de blagues.

Pour rappel :

```bash
docker build -t canaduck/weather-service .
docker run -p 5000:5000 canaduck/weather-service
```

Le service doit être accessible à :

* `http://localhost:5000/weather?city=Rodez`


# Bonus : documentation automatique avec Flasgger

Si vous avez terminé les fonctionnalités principales, ajoutez une documentation interactive avec **Flasgger**, comme dans le TP précédent. Vérifiez alors et accédez à la documentation Swagger sur :

```
http://localhost:5000/apidocs
```

> *"Je t'avais dit qu'on pouvait prédire le vent avec Python."* — Roger

