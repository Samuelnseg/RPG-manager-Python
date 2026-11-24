"""Implementación con MariaDB: SQL escrito a mano sobre las tablas de la nivelación.

Tablas que usa: personaje, clase, inventario, item.
Requiere haber ejecutado db/alter_persistencia.sql (columnas mana y precision_tiro).
"""
import pymysql
from pymysql.cursors import DictCursor

from Modelo.Personaje import Item, crear_personaje
from Repositorio.excepciones import DatoDuplicadoException, DatoEnUsoException
from Repositorio.personaje_repository import PersonajeRepository

ERROR_DUPLICADO = 1062      # violación de UNIQUE
ERROR_FK_EN_USO = 1451      # una llave foránea de otra tabla apunta a esta fila

# La clase NO está como texto en personaje: se trae de la tabla clase con un JOIN
SELECT_PERSONAJE = """
    SELECT p.id_personaje, p.nombre, c.nombre AS clase, p.nivel, p.vida,
           p.ataque, p.oro, p.mana, p.precision_tiro
    FROM personaje p
    JOIN clase c ON p.id_clase = c.id_clase
"""


class RepositorioMariaDB(PersonajeRepository):

    def __init__(self, host, puerto, base, usuario, clave):
        self._parametros = dict(host=host, port=int(puerto), database=base, user=usuario,
                                password=clave, charset="utf8mb4", cursorclass=DictCursor)
        # Mapa nombre de clase -> id_clase, cargado una sola vez al arrancar
        self._id_clase = {}
        with self._conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT id_clase, nombre FROM clase")
            for fila in cursor.fetchall():
                self._id_clase[fila["nombre"]] = fila["id_clase"]

    def _conectar(self):
        return pymysql.connect(**self._parametros)

    @staticmethod
    def _fila_a_personaje(fila):
        # Con DictCursor cada fila es un dict: se lee por nombre de columna
        return crear_personaje(
            fila["clase"], fila["nombre"], fila["nivel"], fila["vida"], fila["ataque"],
            fila["oro"], id=fila["id_personaje"],
            mana=fila["mana"], precision=fila["precision_tiro"])

    # Archivo: rpg_manager_multinivel_flask/repositorio/repositorio_mariadb.py (fragmento)

    def _consultar_personajes(self, sql, parametros=()):
        resultado = []
        with self._conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(sql, parametros)
            for fila in cursor.fetchall():
                resultado.append(self._fila_a_personaje(fila))
        return resultado

    def buscar_por_id(self, id):
        encontrados = self._consultar_personajes(SELECT_PERSONAJE + " WHERE p.id_personaje = %s", (id,))
        return encontrados[0] if encontrados else None
        

    def guardar(self, personaje):
        sql = """INSERT INTO personaje
                     (nombre, id_clase, nivel, vida, ataque, oro, mana, precision_tiro)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        valores = (personaje.nombre, self._id_clase[personaje.clase], personaje.nivel,
                   personaje.vida, personaje.ataque, personaje.oro,
                   getattr(personaje, "mana", None), getattr(personaje, "precision", None))
        # >>> SALA 2.4 · MariaDB: guardar con INSERT
        # Arma este bloque en el Edificio de la Persistencia (pestaña Python),
        # pulsa «Copiar bloque» y pégalo entre estas dos marcas.
        # <<< FIN SALA 2.4

    def buscar_por_id(self, id):
        encontrados = self._consultar_personajes(SELECT_PERSONAJE + " WHERE p.id_personaje = %s", (id,))
        return encontrados[0] if encontrados else None

    def listar_todos(self):
        return self._consultar_personajes(SELECT_PERSONAJE + " ORDER BY p.id_personaje")

    def listar_por_clase(self, clase):
        return self._consultar_personajes(
            SELECT_PERSONAJE + " WHERE c.nombre = %s ORDER BY p.id_personaje", (clase,))

    def actualizar(self, personaje):
        sql = """UPDATE personaje
                 SET nombre = %s, id_clase = %s, nivel = %s, vida = %s, ataque = %s,
                     oro = %s, mana = %s, precision_tiro = %s
                 WHERE id_personaje = %s"""
        valores = (personaje.nombre, self._id_clase[personaje.clase], personaje.nivel,
                   personaje.vida, personaje.ataque, personaje.oro,
                   getattr(personaje, "mana", None), getattr(personaje, "precision", None),
                   personaje.id)
        with self._conectar() as conexion:
            try:
                with conexion.cursor() as cursor:
                    filas = cursor.execute(sql, valores)
                conexion.commit()
            except pymysql.err.IntegrityError as error:
                conexion.rollback()
                if error.args[0] == ERROR_DUPLICADO:
                    raise DatoDuplicadoException(personaje.nombre) from error
                raise
        # MariaDB cuenta 0 filas si el UPDATE no cambió nada; por eso se confirma que exista
        return filas > 0 or self.buscar_por_id(personaje.id) is not None

    def eliminar(self, id):
        # >>> SALA 2.5 · MariaDB: eliminar y el error 1451
        # Arma este bloque en el Edificio de la Persistencia (pestaña Python),
        # pulsa «Copiar bloque» y pégalo entre estas dos marcas.
        # <<< FIN SALA 2.5

    def listar_inventario(self, id_personaje):
        sql = """SELECT i.nombre, i.tipo, i.valor, inv.cantidad
                 FROM inventario inv
                 JOIN item i ON inv.id_item = i.id_item
                 WHERE inv.id_personaje = %s
                 ORDER BY i.nombre"""
        items = []
        with self._conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute(sql, (id_personaje,))
            for fila in cursor.fetchall():
                items.append(Item(fila["nombre"], fila["tipo"], fila["valor"], fila["cantidad"]))
        return items

    def listar_catalogo(self):
        items = []
        with self._conectar() as conexion, conexion.cursor() as cursor:
            cursor.execute("SELECT nombre, tipo, valor FROM item ORDER BY tipo, nombre")
            for fila in cursor.fetchall():
                items.append(Item(fila["nombre"], fila["tipo"], fila["valor"]))
        return items

    def agregar_item(self, id_personaje, nombre_item, cantidad):
        # El id_item sale de la tabla item por su nombre. Si el personaje ya tenía
        # el ítem, la llave primaria (id_personaje, id_item) se repite y
        # ON DUPLICATE KEY UPDATE suma la cantidad en vez de fallar.
        sql = """INSERT INTO inventario (id_personaje, id_item, cantidad)
                 SELECT %s, id_item, %s FROM item WHERE nombre = %s
                 ON DUPLICATE KEY UPDATE cantidad = inventario.cantidad + VALUES(cantidad)"""
        with self._conectar() as conexion:
            with conexion.cursor() as cursor:
                filas = cursor.execute(sql, (id_personaje, cantidad, nombre_item))
            conexion.commit()
        return filas > 0        # 0 filas: el ítem no existe en la tabla item

    def quitar_item(self, id_personaje, nombre_item):
        sql = """DELETE inv FROM inventario inv
                 JOIN item i ON inv.id_item = i.id_item
                 WHERE inv.id_personaje = %s AND i.nombre = %s"""
        with self._conectar() as conexion:
            with conexion.cursor() as cursor:
                filas = cursor.execute(sql, (id_personaje, nombre_item))
            conexion.commit()
        return filas > 0