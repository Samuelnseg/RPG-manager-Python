from flask import Flask, jsonify, request
from Modelo.Personaje import Personaje
from Modelo.PersonajeDAO import PersonajeDAO

dao = PersonajeDAO()
app = Flask(__name__)

@app.route('/personajes', methods=['GET'])
def obtener_personajes():
    return jsonify(dao.obtener_personajes())

@app.route('/personajes', methods=['POST'])
def agregar_personaje():
    data = request.get_json()
    nombre = data.get('nombre')
    clase = data.get('clase')
    nivel = data.get('nivel')
    vida = data.get('vida')
    dao.agregar_personaje(Personaje(nombre, clase, nivel, vida))
    return jsonify({"message": "Personaje agregado correctamente"})

if __name__ == '__main__':
    app.run(debug=True) 