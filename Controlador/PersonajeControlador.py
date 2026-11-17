from Servicio.PersonajeServicio import PersonajeServicio

class PersonajeControlador:
    def __init__(self):
        self.servicio = PersonajeServicio()

    def agregar_personaje(self, nombre, clase, nivel, vida):
        if self.servicio.agregarPersonaje(nombre, clase, nivel, vida):
            return "Personaje agregado exitosamente."
        else:
            return "Error al agregar el personaje. Verifica los datos ingresados."

    def obtener_personajes(self):
        return self.servicio.obtenerPersonajes()