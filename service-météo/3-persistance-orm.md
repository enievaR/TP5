---
titre: Architecture micro-service
sous-titre: TP 5 - Premiers micro-services - La météo, ça coûte cher en bande passante !
auteur: Philippe \textsc{Roussille}
theme: Warsaw
lang: fr-FR
section-titles: false
fontsize: 10pt
couleur-type-1: true
rendu-type: papier
rendu-logo: 3il
---

# État des lieux

## Présentation du cadre

> *"C'est quoi ce flood sur open-meteo ?!" - Ginette*
> *"Désolé, j'ai fait une boucle infinie pour voir s'il faisait toujours beau à Rodez... et puis mon cactus a éternué, et donc je vais devoir m'absenter du bureau, je vous laisse gérer." - Philibert Roquart, stagiaire à temps partiel "efficace"*

Après plusieurs jours d'utilisation, certains ont remarqué que le microservice météo était interrogé **en boucle** par des scripts naïfs. Résultat : des appels redondants, une saturation du service externe... et une menace de ban de la part d'Open-Meteo.

## Le problème

Le service météo actuel interroge *systématiquement* l'API distante à chaque requête, sans rien retenir. Pas malin, surtout pour Rodez, dont le climat change peu. Il est temps d'ajouter une **forme de persistance** : retenir les dernières infos pour ne pas toujours les redemander.

## Ben c'est simple, on part sur des fichiers !

On pourrait, bien sûr, stocker les réponses dans un fichier JSON. Mais cela pose vite des problèmes :

* Fichiers à ouvrir/fermer proprement
* Accès concurrents risqués
* Difficile de filtrer ou d'organiser les données efficacement

Or, vous avez déjà vu un **outil bien plus adapté** : une **base de données**.

## Deux outils outils : MySQL + SQLAlchemy

Grâce à la dockerisation du TP précédent, on peut maintenant facilement ajouter une **base MySQL via docker-compose**. Et pour éviter de manipuler des requêtes SQL à la main, on utilisera un **ORM** : un outil qui permet de manipuler les objets Python comme des enregistrements de base de données.

Ce n'est pas toujours nécessaire (ici, c'est même très artificiel) mais c'est **un passage obligé** pour comprendre les architectures modernes.

# Le matériel de base pour flanquer une BD

## Fichier `docker-compose.yml` + `.env`

Plutôt que de coder en dur les identifiants dans le `docker-compose.yml`, nous allons utiliser un fichier `.env` pour centraliser la configuration.

### Contenu de `.env`

```
DB_HOST=db
DB_PORT=3306
DB_USER=weather
DB_PASSWORD=weatherpass
DB_NAME=weather_db
MYSQL_ROOT_PASSWORD=rootpass
```

### Fichier `docker-compose.yml`

```yaml
version: '3.8'

services:
  weather:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - db

  db:
    image: mysql:8.0
    restart: always
    env_file:
      - .env
    environment:
      MYSQL_DATABASE: ${DB_NAME}
      MYSQL_USER: ${DB_USER}
      MYSQL_PASSWORD: ${DB_PASSWORD}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
    volumes:
      - dbdata:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  dbdata:
```

(cela doit ressembler à votre production du dernier TP)

# Questions de réflexion

Avant de coder, prenez le temps de réfléchir à ces questions. Elles vous aideront à comprendre le **pourquoi** avant de voir le **comment**.

## Sur la base de données

1. Pourquoi ajouter une base de données à un service météo aussi simple ? Est-ce justifié ?  

        Pour éviter de surcharger l'API externe et pour stocker les données de manière persistante.
2. Est-ce que chaque microservice devrait avoir sa propre base, ou peut-on les partager ?  

        Chaque microservice devrait idéalement avoir sa propre base pour éviter les dépendances et faciliter la scalabilité. Cependant, dans certains cas, il peut être judicieux de partager une base si les services sont étroitement liés.
3. Que gagne-t-on (et que perd-on) en utilisant une base relationnelle plutôt qu'un fichier ou un dictionnaire Python ?  

        On gagne en robustesse, en scalabilité et en capacité de requête. On perd en simplicité et en performance pour des opérations très simples.
4. Que permet une base comme MySQL que ne permet pas un fichier JSON ?

        MySQL permet des requêtes complexes, des transactions, une gestion des accès concurrents, et une intégrité des données. Un fichier JSON est limité à la sérialisation/désérialisation et ne gère pas les accès concurrents.
5. Si on voulait partager cette météo avec d'autres services, la base est-elle une bonne interface ?  
        Oui, une base de données permet de structurer les données de manière standardisée et d'offrir des interfaces de requête (SQL) qui peuvent être utilisées par d'autres services. Cela facilite l'intégration et la réutilisation des données.
6. Peut-on facilement sauvegarder/exporter les données ? Et les restaurer ?  

        Oui, MySQL permet de faire des sauvegardes via des outils comme `mysqldump` ou des commandes SQL pour exporter les données. La restauration est également simple avec les mêmes outils. De plus, Docker facilite la gestion des volumes pour conserver les données entre les redémarrages du conteneur.

## Sur les performances et la scalabilité

7. Est-ce que l'ajout d'une BDD rend le service plus rapide ? Plus lent ?  

        L'ajout d'une base de données peut rendre le service plus lent pour les requêtes individuelles, car il y a une latence liée à la connexion et aux opérations de lecture/écriture. Cependant, cela permet de réduire la charge sur l'API externe en évitant les appels redondants, ce qui peut améliorer les performances globales du système.
8. Que se passe-t-il si plusieurs clients envoient des requêtes simultanément ?  

        Si plusieurs clients envoient des requêtes simultanément, la base de données gère les accès concurrents. Cependant, il peut y avoir des problèmes de contention ou de verrouillage si les requêtes modifient les mêmes données. Il est important de gérer les transactions et les verrous pour éviter les conflits.
9. Peut-on mettre à jour une donnée météo sans recontacter l'API externe ?  

        Oui, on peut mettre à jour une donnée météo en modifiant l'enregistrement dans la base de données sans recontacter l'API externe. Cela permet de conserver les données locales et de réduire le nombre d'appels à l'API.
10. Est-ce qu'on peut interroger la météo d'hier ou de demain avec cette architecture ?

        Oui, on peut interroger la météo d'hier ou de demain en stockant les données avec un timestamp. On peut ensuite utiliser des requêtes SQL pour filtrer les données en fonction de la date souhaitée.

# Le vif du sujet : comprendre et utiliser SQLAlchemy (ORM)

## Qu’est-ce qu’un ORM ?

Un **ORM** (Object-Relational Mapper) est une bibliothèque qui permet de manipuler une **base de données relationnelle** à l’aide d’objets Python, **sans écrire de SQL directement**.

* Vous écrivez des **classes Python** → il crée des **tables SQL**
* Vous instanciez des objets Python → il insère des **lignes en base**
* Vous modifiez des attributs → il exécute des **requêtes UPDATE**

L’ORM que nous utilisons ici est **SQLAlchemy**, avec son intégration Flask.

## Installer SQLAlchemy

Une petite ligne de commande et hop : `pip install flask flask_sqlalchemy pymysql`

## Déclarer le modèle

Dans `models.py`, on définit une classe qui hérite de `db.Model` :

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float)
    windspeed = db.Column(db.Float)
    condition = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime)
```

Cela crée une table `weather_data` avec les colonnes suivantes : `id`, `city`, `temperature`, `windspeed`, `condition`, `timestamp`.

## Initialiser SQLAlchemy dans `app.py`

```python
from flask import Flask
from models import db
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
```

Pensez à installer le driver `pymysql` si besoin :

```bash
pip install pymysql
```

## Créer et récupérer des données

### Ajouter une entrée

```python
from models import WeatherData
from datetime import datetime

entry = WeatherData(
    city="Rodez",
    temperature=22.5,
    windspeed=10.4,
    condition="nuageux",
    timestamp=datetime.utcnow()
)
db.session.add(entry)
db.session.commit()
```

### Chercher une donnée en BDD

```python
result = WeatherData.query.filter_by(city="Rodez").first()
```

On peut ensuite comparer le `timestamp` pour décider si la donnée est "fraîche" ou non.


# Réparer le service pour éviter la magouille de Philibert (et tous les autres)

> *"Mais moi je m'en fiche, j'avais fait un code simple qui retient la météo et qui l'affiche. Je veux que ça marche !"* - Philibert Roquart, toujours pas convaincu

Avant même de penser à quoi que ce soit (trop fatiguant), Philibert a écrit un petit script personnel. C'est moche, ça spamme, mais... ça *marche*. Voici un exemple (à **ne pas reproduire tel quel**, sauf pour le corriger !) :

```python
# philibert.py
import requests
import time

while True:
    try:
        r = requests.get("http://localhost:5000/weather?city=Rodez")
        print(r.json())
    except Exception as e:
        print("Erreur:", e)
    time.sleep(1)
```

Ce script :

* interroge le microservice météo **chaque seconde**, sans jamais mémoriser la réponse,
* utilise `print()` pour tout afficher,
* n'a aucune tolérance aux erreurs réseau,
* fonctionne en local uniquement.

Votre mission, si vous l'acceptez :

* Éviter que ce genre de script n'explose les quotas de l'API ou ne fasse tourner le serveur dans le vide.
* Ajouter une couche de cache ou de persistance.
* Bonus : aider Philibert à améliorer son script pour qu'il interroge **intelligemment** le service météo.

# Questions de réflexion

1. Pourquoi voudrait-on éviter d'écrire directement des requêtes SQL à la main ?

        Pour éviter les erreurs de syntaxe, améliorer la lisibilité du code, faciliter la maintenance et permettre une abstraction des détails de la base de données.
2. Que gagne-t-on en utilisant un ORM comme SQLAlchemy ?

        On gagne en lisibilité et en abstraction, on écrit du python au lieu de SQL, on peut facilement manipuler des objets et gérer les relations entre eux. Cela permet aussi de changer de base de données sans modifier le code applicatif.
3. Est-ce que l’ORM vous empêche complètement d’accéder au SQL si besoin ?

        Pas du tout, on peux toujours utiliser des requête SQL en dur 
4. Est-ce que le code Python devient plus clair ou plus opaque avec un ORM ?

        Beaucoup p^lus clair, car on  a pas au milieu du code en python des requêtes SQL. Un ORM permet de manipuler les données de manière orientée objet beaucoup plus effucace et lisible.
5. À quel moment l’ORM peut devenir un inconvénient ? (performances, complexité, etc.)

        L'ORM peut devenir un inconvénient si les requêtes deviennent très complexes, car il peut générer du SQL inefficace. De plus, pour des opérations très simples ou des scripts légers, l'ORM peut ajouter une couche de complexité inutile.

## Quelques pistes pour vous aider...

* Un ORM est très pratique pour prototyper vite, mais **introduit une abstraction** : il faut comprendre ce qu’il génère en SQL !
* SQLAlchemy est un ORM très complet, mais aussi complexe. Ici, on reste dans un usage basique.
* Pensez à gérer les erreurs de connexion ou d’intégrité (`try/except`).

