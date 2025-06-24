from flasgger import Swagger
from flask import Flask
import random
from flask import request, jsonify


app = Flask(__name__)
swagger = Swagger(app)


jokes=[
{ "joke": "Pourquoi un canard est toujours à l'heure ? Parce qu'il est dans l'étang." },
{ "joke": "Quel est le jeu de cartes préféré des canards ? La coin-che." },
{ "joke": "Qu'est-ce qui fait Nioc nioc? Un canard qui parle en verlan." },
{ "joke": "Comment appelle-t-on un canard qui fait du DevOps ? Un DuckOps." }
]


@app.route('/')
def index():
    """
    Welcome to the Duck Jokes API
    ---
    responses:
      200:
        description: A welcome message
        examples:
          text: "Welcome to the Duck Jokes API!"
    """
    return "Welcome to the Duck Jokes API!"




@app.route('/joke', methods=['GET'])
def get_joke():
    """
    Get a random joke
    ---
    responses:
      200:
        description: A random joke
        schema:
          type: object
          properties:
            joke:
              type: string
              example: "Pourquoi un canard est toujours à l'heure ? Parce qu'il est dans l'étang."
    """
    return {"joke": random.choice(jokes)["joke"]}


@app.route('/joke',methods=['POST'])
def add_joke():
    """
    Add a new joke
    ---
    parameters:
      - name: joke
        in: body
        required: true
        schema:
          type: object
          properties:
            joke:
              type: string
              example: "Quel est le jeu de cartes préféré des canards ? La coin-che."
    response:
      201:
        description: Joke added successfully
        schema:
          type: object
          properties:
            message:
                type: string
                example: "Joke added successfully"
    """
    print(request.json)
    new_joke = request.json.get('joke')
    if new_joke:
        jokes.append({"joke": new_joke})
        return {"message": "Joke added successfully"}, 201
    else:
        return {"message": "Joke content is required"}, 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)





