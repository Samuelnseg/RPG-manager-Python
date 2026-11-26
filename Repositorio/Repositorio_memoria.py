"""Implementación en memoria: un dict cuya clave es el id.

Sirve para probar sin base de datos. Al reiniciar el servidor, todo se pierde.
"""
from Modelo.Personaje import Item
from Repositorio.excepciones import DatoDuplicadoException
from Repositorio.personaje_repository import PersonajeRepository

# Catálogo fijo: los mismos 9 ítems de la tabla item de MariaDB
CATALOGO = [
    Item("Espada larga", "arma", 120),
    Item("Hacha de guerra", "arma", 200),
    Item("Báculo arcano", "arma", 250),
    Item("Arco élfico", "arma", 180),
    Item("Cota de malla", "armadura", 300),
    Item("Túnica encantada", "armadura", 220),
    Item("Poción de vida", "pocion", 25),
    Item("Elixir de maná", "pocion", 40),
    Item("Amuleto del dragón", "reliquia", 1000),
]


class RepositorioMemoria(PersonajeRepository):

    def __init__(self):
        self._datos = {}          # id -> Personaje
        self._inventarios = {}    # id -> lista de Item
        self._siguiente_id = 1    # como AUTO_INCREMENT: nunca reutiliza un id

    def guardar(self, personaje):
        for existente in self._datos.values():
            if existente.nombre == personaje.nombre:
                raise DatoDuplicadoException(personaje.nombre)
        personaje.id = self._siguiente_id
        self._siguiente_id += 1
        self._datos[personaje.id] = personaje
        self._inventarios[personaje.id] = []
        return personaje


    def buscar_por_id(self, id):
        return self._datos.get(id)          # None si no existe (dict[id] lanzaría KeyError)

    def listar_todos(self):
        return list(self._datos.values())   # copia: quien la reciba no puede dañar el dict

    def listar_por_clase(self, clase):
        resultado = []
        for personaje in self._datos.values():
            if personaje.clase == clase:
                resultado.append(personaje)
        return resultado

    def actualizar(self, personaje):
        if personaje.id not in self._datos:
            return False
        self._datos[personaje.id] = personaje
        return True

    def eliminar(self, id):
        if id not in self._datos:
            return False
        del self._datos[id]
        self._inventarios.pop(id, None)
        return True

    def listar_inventario(self, id_personaje):
        return list(self._inventarios.get(id_personaje, []))

    def listar_catalogo(self):
        return list(CATALOGO)

    def agregar_item(self, id_personaje, nombre_item, cantidad):
        del_catalogo = None
        for item in CATALOGO:
            if item.nombre == nombre_item:
                del_catalogo = item
        if del_catalogo is None:
            return False
        inventario = self._inventarios.setdefault(id_personaje, [])
        for item in inventario:
            if item.nombre == nombre_item:      # ya lo tiene: se acumula
                item.cantidad += cantidad
                return True
        inventario.append(Item(del_catalogo.nombre, del_catalogo.tipo, del_catalogo.valor, cantidad))
        return True

    def quitar_item(self, id_personaje, nombre_item):
        inventario = self._inventarios.get(id_personaje, [])
        for i in range(len(inventario)):
            if inventario[i].nombre == nombre_item:
                del inventario[i]               # se borra por posición y se sale del ciclo
                return True
        return False