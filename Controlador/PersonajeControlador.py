"""Controlador: recibe la petición, llama al Service y elige la vista.

Aquí no hay SQL ni llamadas a MongoDB: si aparecen en una ruta, se rompió una capa.
"""
from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from Modelo.Personaje import CLASES_VALIDAS
from Servicio.PersonajeService import PersonajeNoEncontradoException, ValidacionException


def crear_controlador(service, motor):
    bp = Blueprint("personajes", __name__)

    @bp.app_context_processor
    def datos_comunes():
        return {"motor": motor, "clases": CLASES_VALIDAS}

    # ---------- vistas HTML ----------

    @bp.get("/")
    def inicio():
        return redirect(url_for("personajes.listar"))

    @bp.get("/personajes")
    def listar():
        clase = request.args.get("clase", "")
        error = None
        try:
            personajes = service.listar_por_clase(clase) if clase else service.listar()
        except ValidacionException as e:
            personajes, error = service.listar(), str(e)
        return render_template("personajes.html", personajes=personajes,
                               clase_filtro=clase, error=error)

    @bp.get("/personajes/nuevo")
    def formulario():
        return render_template("nuevo.html", datos={}, error=None)

    @bp.post("/personajes")
    def crear():
        datos = request.form
        try:
            service.crear(datos.get("nombre"), datos.get("clase"), datos.get("nivel", 1),
                          datos.get("vida", 100), datos.get("ataque", 10), datos.get("oro", 0))
        except ValidacionException as e:
            return render_template("nuevo.html", datos=datos, error=str(e)), 400
        return redirect(url_for("personajes.listar"))


    @bp.get("/personajes/<int:id>")
    def detalle(id):
        try:
            personaje = service.obtener(id)
            inventario = service.inventario(id)
        except PersonajeNoEncontradoException as e:
            return render_template("error.html", mensaje=str(e)), 404
        return render_template("detalle.html", p=personaje, inventario=inventario,
                               catalogo=service.catalogo(), error=request.args.get("error"))

    @bp.post("/personajes/<int:id>/inventario")
    def agregar_item(id):
        try:
            service.agregar_item(id, request.form.get("item"), request.form.get("cantidad", 1))
        except PersonajeNoEncontradoException as e:
            return render_template("error.html", mensaje=str(e)), 404
        except ValidacionException as e:
            return redirect(url_for("personajes.detalle", id=id, error=str(e)))
        return redirect(url_for("personajes.detalle", id=id))


    @bp.post("/personajes/<int:id>/inventario/quitar")
    def quitar_item(id):
        try:
            service.quitar_item(id, request.form.get("item"))
        except PersonajeNoEncontradoException as e:
            return render_template("error.html", mensaje=str(e)), 404
        except ValidacionException as e:
            return redirect(url_for("personajes.detalle", id=id, error=str(e)))
        return redirect(url_for("personajes.detalle", id=id))

    @bp.post("/personajes/<int:id>/vida")
    def actualizar_vida(id):
        try:
            service.actualizar_vida(id, request.form.get("vida"))
        except PersonajeNoEncontradoException as e:
            return render_template("error.html", mensaje=str(e)), 404
        except ValidacionException as e:
            return redirect(url_for("personajes.detalle", id=id, error=str(e)))
        return redirect(url_for("personajes.detalle", id=id))

    @bp.post("/personajes/<int:id>/eliminar")
    def eliminar(id):
        try:
            service.eliminar(id)
        except PersonajeNoEncontradoException as e:
            return render_template("error.html", mensaje=str(e)), 404
        except ValidacionException as e:
            return redirect(url_for("personajes.detalle", id=id, error=str(e)))
        return redirect(url_for("personajes.listar"))

    # ---------- API JSON ----------

    @bp.get("/api/personajes")
    def api_listar():
        clase = request.args.get("clase")
        try:
            personajes = service.listar_por_clase(clase) if clase else service.listar()
        except ValidacionException as e:
            return jsonify({"error": str(e)}), 400
        return jsonify([p.a_dict() for p in personajes])

    @bp.get("/api/personajes/<int:id>")
    def api_obtener(id):
        try:
            return jsonify(service.obtener(id).a_dict())
        except PersonajeNoEncontradoException as e:
            return jsonify({"error": str(e)}), 404

    @bp.get("/api/personajes/<int:id>/inventario")
    def api_inventario(id):
        try:
            return jsonify([item.a_dict() for item in service.inventario(id)])
        except PersonajeNoEncontradoException as e:
            return jsonify({"error": str(e)}), 404

    @bp.post("/api/personajes")
    def api_crear():
        datos = request.get_json(silent=True) or {}
        try:
            p = service.crear(datos.get("nombre"), datos.get("clase"), datos.get("nivel", 1),
                              datos.get("vida", 100), datos.get("ataque", 10), datos.get("oro", 0))
        except ValidacionException as e:
            return jsonify({"error": str(e)}), 400
        return jsonify(p.a_dict()), 201

    return bp