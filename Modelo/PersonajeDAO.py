class PersonajeDAO:
    def __init__(self):
        self.personajes = []

    def agregar_personaje(self, personaje):
        self.personajes.append(personaje)

    def obtener_personajes(self):
        return self.personajes