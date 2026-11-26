"""Capa de negocio: las reglas del juego.

Recibe el repositorio por el constructor y solo conoce el contrato
PersonajeRepository: no sabe si detrás hay memoria, MariaDB o MongoDB.
"""
from decimal import Decimal, InvalidOperation

from Modelo.Personaje import CLASES_VALIDAS, crear_personaje
from Repositorio.excepciones import DatoDuplicadoException, DatoEnUsoException


class ValidacionException(Exception):
    """Un dato no cumple una regla del juego. El mensaje es para el usuario."""


class PersonajeNoEncontradoException(Exception):
    """No existe un personaje con ese id."""


class PersonajeService:

    def __init__(self, repositorio):
        self._repositorio = repositorio

    # ---------- consultas ----------

    def listar(self):
        return self._repositorio.listar_todos()


    def listar_por_clase(self, clase):
        self._validar_clase(clase)
        return self._repositorio.listar_por_clase(clase)

    def obtener(self, id):
        personaje = self._repositorio.buscar_por_id(id)
        if personaje is None:
            raise PersonajeNoEncontradoException(f"No existe el personaje {id}")
        return personaje

    def inventario(self, id):
        self.obtener(id)    # 404 si el personaje no existe
        return self._repositorio.listar_inventario(id)


    def catalogo(self):
        return self._repositorio.listar_catalogo()

    # ---------- inventario ----------

    def agregar_item(self, id, nombre_item, cantidad=1):
        self.obtener(id)
        cantidad = self._entero(cantidad, "cantidad")
        if not 1 <= cantidad <= 99:
            raise ValidacionException("La cantidad debe estar entre 1 y 99")
        nombres = []
        for item in self._repositorio.listar_catalogo():
            nombres.append(item.nombre)
        if nombre_item not in nombres:
            raise ValidacionException(f"No existe el ítem {nombre_item}")
        self._repositorio.agregar_item(id, nombre_item, cantidad)
        return self._repositorio.listar_inventario(id)


    def quitar_item(self, id, nombre_item):
        personaje = self.obtener(id)
        if not self._repositorio.quitar_item(id, nombre_item):
            raise ValidacionException(f"{personaje.nombre} no tiene {nombre_item} en su inventario")

    # ---------- cambios ----------

    def crear(self, nombre, clase, nivel=1, vida=100, ataque=10, oro="0"):
        nombre = (nombre or "").strip()
        if not nombre:
            raise ValidacionException("El nombre es obligatorio")
        if len(nombre) > 50:
            raise ValidacionException("El nombre admite máximo 50 caracteres")
        self._validar_clase(clase)
        nivel = self._entero(nivel, "nivel")
        vida = self._entero(vida, "vida")
        ataque = self._entero(ataque, "ataque")
        oro = self._dinero(oro)
        if not 1 <= nivel <= 100:
            raise ValidacionException("El nivel debe estar entre 1 y 100")
        if vida < 0:
            raise ValidacionException("La vida no puede ser negativa")
        if ataque < 0:
            raise ValidacionException("El ataque no puede ser negativo")
        if oro < 0:
            raise ValidacionException("El oro no puede ser negativo")

        personaje = crear_personaje(clase, nombre, nivel, vida, ataque, oro)
        try:
            return self._repositorio.guardar(personaje)
        except DatoDuplicadoException:
            raise ValidacionException(f"Ya existe un personaje llamado {nombre}")


    def actualizar_vida(self, id, vida):
        vida = self._entero(vida, "vida")
        if vida < 0:
            raise ValidacionException("La vida no puede ser negativa")
        personaje = self.obtener(id)
        personaje.vida = vida
        self._repositorio.actualizar(personaje)
        return personaje

    def eliminar(self, id):
        self.obtener(id)
        try:
            self._repositorio.eliminar(id)
        except DatoEnUsoException:
            raise ValidacionException(
                "No se puede eliminar: el personaje tiene combates registrados")

    # ---------- validaciones auxiliares ----------

    @staticmethod
    def _validar_clase(clase):
        if clase not in CLASES_VALIDAS:
            raise ValidacionException(f"Clase inválida: {clase}. Usa Guerrero, Mago o Arquero")

    @staticmethod
    def _entero(valor, campo):
        try:
            return int(valor)
        except (TypeError, ValueError):
            raise ValidacionException(f"El campo {campo} debe ser un número entero")

    @staticmethod
    def _dinero(valor):
        try:
            return Decimal(str(valor)).quantize(Decimal("0.01"))
        except InvalidOperation:
            raise ValidacionException("El oro debe ser un número")