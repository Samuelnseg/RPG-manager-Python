from flask import Flask, jsonify, redirect, request, render_template
import Modelo.PersonajeDAO as personaje_dao
from Modelo.Personaje import Personaje

app = Flask(__name__)
personaje_dao = personaje_dao.PersonajeDAO()

@app.route('/personajes', methods=['GET'])
def obtener_personajes():
    personajes = personaje_dao.obtener_todos()
    return render_template('personaje.html', personajes=personajes)

@app.route('/crear-personaje', methods=['POST'])
def crear_personaje():
    nombre = request.form.get('nombre')
    clase = request.form.get('clase')

    nuevo_personaje = Personaje(nombre, clase, nivel=1, vida=100)
    
    personaje_dao.agregar_personaje(nuevo_personaje)

    return redirect('/personajes')

if __name__ == '__main__':
    app.run(port=5000, debug=True)