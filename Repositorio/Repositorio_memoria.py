# Archivo: rpg_manager_multinivel_flask/repositorio/repositorio_memoria.py (fragmento)


class RepositorioMemoria():
    def __init__(self):
        self._datos = {}          # id -> Personaje
        self._inventarios = {}    # id -> lista de Item
        self._siguiente_id = 1    # como AUTO_INCREMENT: nunca reutiliza un id

    def guardar(self, personaje):
        # Misma regla que el UNIQUE de MariaDB sobre el nombre
        for existente in self._datos.values():
            if existente.nombre == personaje.nombre:
                raise DatoDuplicadoException(personaje.nombre)
        personaje.id = self._siguiente_id
        self._siguiente_id += 1
        self._datos[personaje.id] = personaje
        self._inventarios[personaje.id] = []
        return personaje