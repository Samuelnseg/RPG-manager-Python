from Modelo.Personaje import Personaje
class PersonajeDAO:
    def __init__(self):
        self.personajes = [Personaje("Maguin", "Mago", 0, 100), Personaje("Efrain", "Guerrero", 0, 150)]

    def obtener_todos(self):
        Personajes_dict = [personaje.to_dict() for personaje in self.personajes]
        return Personajes_dict

    def agregar_personaje(self, personaje):
        self.personajes.append(personaje)