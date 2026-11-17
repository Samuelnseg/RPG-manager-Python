from flask import Flask, jsonify, redirect, render_template, request, url_for
from Controlador.PersonajeControlador import PersonajeControlador
from Modelo.Personaje import Personaje

pc = PersonajeControlador()
app = Flask(__name__)

@app.route('/personajes', methods=['GET'])
def obtener_personajes():
    return render_template('index.html', personajes=pc.obtener_personajes())

@app.route('/personajes', methods=['POST'])
def agregar_personaje():
    nombre = request.form.get('nombre')
    clase = request.form.get('clase')
    nivel = int(request.form.get('nivel'))
    vida = int(request.form.get('vida'))    
    mensaje = pc.agregar_personaje(nombre, clase, nivel, vida)
    return redirect(url_for('agregar_personaje'))

if __name__ == '__main__':
    app.run(debug=True)