from flask import Flask, jsonify, redirect, render_template, request, url_for
from Modelo.Personaje import Personaje
from Modelo.PersonajeDAO import PersonajeDAO

dao = PersonajeDAO()
app = Flask(__name__)

@app.route('/personajes', methods=['GET'])
def obtener_personajes():
    return render_template('index.html', personajes=dao.obtener_personajes())

@app.route('/personajes', methods=['POST'])
def agregar_personaje():
    nombre = request.form.get('nombre')
    clase = request.form.get('clase')
    nivel = request.form.get('nivel')
    vida = request.form.get('vida')
    dao.agregar_personaje(Personaje(nombre, clase, nivel, vida))
    return redirect(url_for('obtener_personajes'))

if __name__ == '__main__':
    app.run(debug=True)