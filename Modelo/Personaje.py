"""Modelo del RPG Manager: Personaje y sus subclases, e Item del inventario.

El modelo no sabe nada de bases de datos: solo describe los objetos del juego.
"""
from decimal import Decimal

CLASES_VALIDAS = ("Guerrero", "Mago", "Arquero")

MANA_POR_DEFECTO = 100       # Mago sin mana guardado (por ejemplo, filas antiguas en MariaDB)
PRECISION_POR_DEFECTO = 70   # Arquero sin precision guardada


class Personaje:
    """Datos comunes a todos los personajes."""

    clase = "Personaje"

    def __init__(self, nombre, nivel=1, vida=100, ataque=10, oro=Decimal("0"), id=None):
        self.id = id
        self.nombre = nombre
        self.nivel = nivel
        self.vida = vida
        self.ataque = ataque
        self.oro = Decimal(str(oro))


    def a_dict(self):
        """Representación simple para la API JSON y las plantillas."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "clase": self.clase,
            "nivel": self.nivel,
            "vida": self.vida,
            "ataque": self.ataque,
            "oro": str(self.oro),
        }

    def __repr__(self):
        return f"{self.clase}(id={self.id}, nombre={self.nombre!r}, nivel={self.nivel}, vida={self.vida})"


class Guerrero(Personaje):
    clase = "Guerrero"


class Mago(Personaje):
    clase = "Mago"

    def __init__(self, nombre, nivel=1, vida=100, ataque=10, oro=Decimal("0"), id=None,
                mana=MANA_POR_DEFECTO):
        super().__init__(nombre, nivel, vida, ataque, oro, id)
        self.mana = mana

    def a_dict(self):
        datos = super().a_dict()
        datos["mana"] = self.mana
        return datos



class Arquero(Personaje):
    clase = "Arquero"

    def __init__(self, nombre, nivel=1, vida=100, ataque=10, oro=Decimal("0"), id=None,
                precision=PRECISION_POR_DEFECTO):
        super().__init__(nombre, nivel, vida, ataque, oro, id)
        self.precision = precision

    def a_dict(self):
        datos = super().a_dict()
        datos["precision"] = self.precision
        return datos


def crear_personaje(clase, nombre, nivel=1, vida=100, ataque=10, oro=Decimal("0"), id=None,
                    mana=None, precision=None):
    """Reconstruye la subclase correcta a partir del texto de la clase.

    La usan los tres repositorios: una fila de MariaDB, un documento de MongoDB
    o un formulario dicen "Mago", y aquí se decide qué objeto crear.
    """
    if clase == "Guerrero":
        return Guerrero(nombre, nivel, vida, ataque, oro, id)
    if clase == "Mago":
        return Mago(nombre, nivel, vida, ataque, oro, id,
                    mana if mana is not None else MANA_POR_DEFECTO)
    if clase == "Arquero":
        return Arquero(nombre, nivel, vida, ataque, oro, id,
                        precision if precision is not None else PRECISION_POR_DEFECTO)
    raise ValueError(f"Clase desconocida: {clase}")



class Item:
    """Un ítem dentro del inventario de un personaje."""

    def __init__(self, nombre, tipo, valor, cantidad=1):
        self.nombre = nombre
        self.tipo = tipo
        self.valor = valor
        self.cantidad = cantidad


    def a_dict(self):
        return {"nombre": self.nombre, "tipo": self.tipo, "valor": self.valor, "cantidad": self.cantidad}

    def __repr__(self):
        return f"Item({self.nombre!r} x{self.cantidad})"