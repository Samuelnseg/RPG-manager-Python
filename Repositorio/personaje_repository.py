# Archivo: rpg_manager_multinivel_flask/repositorio/personaje_repository.py (clase abstracta)

"""Contrato de la capa de persistencia.

Dice QUÉ operaciones debe ofrecer cualquier repositorio, no CÓMO se hacen.
Python no deja crear un objeto de una clase que no implemente todos los
métodos abstractos (lanza TypeError).
"""
from abc import ABC, abstractmethod


class PersonajeRepository(ABC):

    @abstractmethod
    def guardar(self, personaje):
        """Guarda un personaje nuevo, le asigna su id y lo devuelve."""

    @abstractmethod
    def buscar_por_id(self, id):
        """Devuelve el personaje con ese id, o None si no existe."""

    @abstractmethod
    def listar_todos(self):
        """Devuelve una lista NUEVA con todos los personajes."""

    @abstractmethod
    def listar_por_clase(self, clase):
        """Devuelve una lista nueva con los personajes de esa clase."""

    @abstractmethod
    def actualizar(self, personaje):
        """Guarda los cambios de un personaje existente. True si existía."""

    @abstractmethod
    def eliminar(self, id):
        """Borra el personaje. True si existía."""

    @abstractmethod
    def listar_inventario(self, id_personaje):
        """Devuelve la lista de ítems del personaje (vacía si no tiene)."""

    @abstractmethod
    def listar_catalogo(self):
        """Devuelve todos los ítems que existen en el juego (la tabla item)."""

    @abstractmethod
    def agregar_item(self, id_personaje, nombre_item, cantidad):
        """Suma esa cantidad del ítem al inventario. Si ya lo tenía, se acumula.
        False si el ítem no existe en el catálogo."""

    @abstractmethod
    def quitar_item(self, id_personaje, nombre_item):
        """Saca el ítem completo del inventario. True si lo tenía."""
