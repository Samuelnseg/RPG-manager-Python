"""Errores de datos que cualquier repositorio puede lanzar.

El repositorio NO escribe mensajes para el usuario: solo avisa qué pasó con los
datos. El Service decide qué mensaje mostrar.
"""


class DatoDuplicadoException(Exception):
    """Ya existe un registro con ese valor único (por ejemplo, el nombre)."""


class DatoEnUsoException(Exception):
    """El registro no se puede borrar porque otros datos lo referencian."""