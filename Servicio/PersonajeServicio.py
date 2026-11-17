from Modelo.Personaje import Personaje
from Modelo.PersonajeDAO import PersonajeDAO

class PersonajeServicio:
    def __init__(self):
        self.dao = PersonajeDAO()

    def agregarPersonaje(self, nombre, clase, nivel, vida):
        if nombre.strip() == "":
            return False
        
        if clase.strip() == "":
            return False
        
        if vida < 0:
            return False
        
        if not (1 <= nivel <= 100):
            return False

        if clase not in ["Guerrero", "Mago", "Arquero"]:
            return False
        
        personaje = Personaje(nombre, clase, nivel, vida)
        self.dao.agregar_personaje(personaje)
        return True

    def obtenerPersonajes(self):
        return self.dao.obtener_personajes()