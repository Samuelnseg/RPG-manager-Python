"""Reto 6: el mismo recorrido con cualquier motor.

Uso:
    python recorrido.py            -> usa el motor de config.ini
    python recorrido.py mariadb    -> sobrescribe [app] repositorio solo para esta ejecución

Copia la salida a salida_persistencia.txt.
"""
import sys

from app import leer_configuracion
from Repositorio.repository_factory import crear_repositorio
from Servicio.PersonajeService import PersonajeService, ValidacionException

NOMBRE_PRUEBA = "Kaelen"


def imprimir_lista(titulo, personajes):
    print(f"\n{titulo} ({len(personajes)})")
    for p in personajes:
        print(f"  {p.id:>3}  {p.nombre:<12} {p.clase:<9} nivel {p.nivel:>3}  vida {p.vida:>4}  oro {p.oro}")


def main():
    cfg = leer_configuracion()
    if len(sys.argv) > 1:
        cfg.set("app", "repositorio", sys.argv[1])
    motor = cfg.get("app", "repositorio")
    service = PersonajeService(crear_repositorio(cfg))
    print(f"=== RPG Manager · recorrido de persistencia · Python · motor: {motor} ===")

    imprimir_lista("1. Todos los personajes", service.listar())
    imprimir_lista("2. Solo los Magos", service.listar_por_clase("Mago"))

    todos = service.listar()
    if todos:
        primero = todos[0]
        print(f"\n3. Inventario de {primero.nombre}")
        inventario = service.inventario(primero.id)
        for item in inventario:
            print(f"  {item.nombre:<18} {item.tipo:<9} valor {item.valor:>4}  x{item.cantidad}")
        if not inventario:
            print("  (vacío)")

    try:
        nuevo = service.crear(NOMBRE_PRUEBA, "Arquero", nivel=3, vida=90, ataque=18, oro="12.50")
    except ValidacionException as e:
        print(f"\n4. No se pudo crear: {e}")
        return
    print(f"\n4. Creado: {nuevo.nombre} con id {nuevo.id}")

    actualizado = service.actualizar_vida(nuevo.id, 55)
    print(f"5. Vida de {actualizado.nombre} actualizada a {service.obtener(nuevo.id).vida}")

    service.eliminar(nuevo.id)
    print(f"6. {NOMBRE_PRUEBA} eliminado")

    imprimir_lista("7. Todos los personajes otra vez", service.listar())


    print("\n8. Validaciones del Service")
    for intento in ({"nombre": "", "clase": "Mago"},
                    {"nombre": "Zed", "clase": "Paladin"},
                    {"nombre": "Zed", "clase": "Mago", "vida": -5}):
        try:
            service.crear(**intento)
        except ValidacionException as e:
            print(f"  rechazado: {e}")


if __name__ == "__main__":
    main()