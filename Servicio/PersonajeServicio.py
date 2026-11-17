from Modelo.Personaje import Personaje
from Modelo.PersonajeDAO import PersonajeDAO

class PersonajeServicio:
    def __init__(self):
        self.dao = PersonajeDAO()

    def agregarPersonaje(self, nombre, clase, nivel, vida):
        if nombre.strip() != "" and clase.strip() != "" and vida > 0 and 1 <= nivel <= 100:
            if clase in ["Guerrero", "Mago", "Arquero"]:
                personaje = Personaje(nombre, clase, nivel, vida)
                self.dao.agregar_personaje(personaje)
                return True
        return False

    def obtenerPersonajes(self):
        return self.dao.obtener_personajes()