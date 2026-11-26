"""Punto de arranque del RPG Manager (Flask).

1. Lee config.ini (copia config.example.ini y pon tus datos).
2. La fábrica crea el repositorio que diga [app] repositorio.
3. El Service recibe ese repositorio por el constructor.
4. El controlador recibe el Service.
"""
import configparser
import os
import sys

from flask import Flask

from Controlador.PersonajeControlador import crear_controlador
from Repositorio.repository_factory import crear_repositorio
from Servicio.PersonajeService import PersonajeService

CARPETA = os.path.dirname(os.path.abspath(__file__))


def leer_configuracion(ruta=None):
    ruta = ruta or os.path.join(CARPETA, "config.ini")
    if not os.path.exists(ruta):
        sys.exit("No existe config.ini. Copia config.example.ini como config.ini y pon tus datos.")
    cfg = configparser.ConfigParser()
    cfg.read(ruta, encoding="utf-8")
    return cfg


def crear_app(cfg=None, repositorio=None):
    cfg = cfg or leer_configuracion()
    repositorio = repositorio or crear_repositorio(cfg)   # aquí se elige el motor
    service = PersonajeService(repositorio)                # inyección por constructor

    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.register_blueprint(crear_controlador(service, cfg.get("app", "repositorio")))
    return app



if __name__ == "__main__":
    aplicacion = crear_app()
    aplicacion.run(port=5000, debug=False)