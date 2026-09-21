from flask import Flask, jsonify
import Modelo.PersonajeDAO as personaje_dao

app = Flask(__name__)
personaje_dao = personaje_dao.PersonajeDAO()

@app.route('/personajes', methods=['GET'])
def obtener_personajes():
    personajes = personaje_dao.obtener_todos()
    return jsonify(personajes)

if __name__ == '__main__':
    app.run(port=5000, debug=True)