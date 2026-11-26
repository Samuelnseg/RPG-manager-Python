"""Implementación con MongoDB: la colección personajes cargada con el seed de la nivelación.

Cada documento es un dict. El inventario viene embebido dentro del personaje.

Decisión sobre el id: los documentos del seed solo tienen _id (ObjectId) y el
Service trabaja con ids numéricos. Este repositorio agrega a cada documento un
campo numérico id_personaje, tomado de un contador en la colección
"contadores" (el equivalente al AUTO_INCREMENT). El Service nunca se entera.
"""
import certifi
from pymongo import ASCENDING, MongoClient, ReturnDocument

from decimal import Decimal

from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.errors import DuplicateKeyError

from Modelo.Personaje import Item, crear_personaje
from Repositorio.excepciones import DatoDuplicadoException
from Repositorio.personaje_repository import PersonajeRepository


class RepositorioMongo(PersonajeRepository):

    def __init__(self, uri, base, cliente=None):
        # "cliente" permite inyectar un cliente de pruebas; en la app se crea con la uri
        self._cliente = (
            cliente
            if cliente is not None
            else MongoClient(uri, tlsCAFile=certifi.where())
        )
        db = self._cliente[base]
        self._personajes = db["personajes"]
        self._contadores = db["contadores"]
        self._items = db["items"]          # catálogo: lo crea db/mongo_persistencia.js
        self._preparar_ids()

    def _preparar_ids(self):
        """Da un id_personaje numérico a los documentos que aún no lo tienen."""
        if self._contadores.find_one({"_id": "personajes"}) is None:
            mayor = self._personajes.find_one({"id_personaje": {"$exists": True}},
                                              sort=[("id_personaje", -1)])
            inicio = mayor["id_personaje"] if mayor else 0
            self._contadores.insert_one({"_id": "personajes", "seq": inicio})
        # Orden de inserción (_id) para que los ids sigan el orden del seed.
        # Primero se juntan los _id en una lista y luego se actualizan:
        # nunca se modifica la colección mientras se recorre el cursor
        sin_id = []
        for doc in self._personajes.find({"id_personaje": {"$exists": False}}).sort("_id", ASCENDING):
            sin_id.append(doc["_id"])
        for id_mongo in sin_id:
            self._personajes.update_one({"_id": id_mongo},
                                        {"$set": {"id_personaje": self._siguiente_id()}})
        self._personajes.create_index("id_personaje", unique=True)
        self._personajes.create_index("nombre", unique=True)   # misma regla que el UNIQUE de MariaDB

    def _siguiente_id(self):
        contador = self._contadores.find_one_and_update(
            {"_id": "personajes"}, {"$inc": {"seq": 1}},
            upsert=True, return_document=ReturnDocument.AFTER)
        return contador["seq"]

    @staticmethod
    def _entero(valor):
        # Según cómo se cargó el seed (mongosh, Compass, Atlas) un número puede
        # llegar como int o como float (12.0): se normaliza a int
        return int(valor) if valor is not None else None

    @classmethod
    def _documento_a_personaje(cls, doc):
        # .get(): un Guerrero no tiene "mana" y un Mago no tiene "precision"
        return crear_personaje(
            doc["clase"], doc["nombre"], cls._entero(doc.get("nivel", 1)),
            cls._entero(doc.get("vida", 100)), cls._entero(doc.get("ataque", 10)),
            Decimal(str(doc.get("oro", 0))).quantize(Decimal("0.01")),
            id=cls._entero(doc["id_personaje"]),
            mana=cls._entero(doc.get("mana")), precision=cls._entero(doc.get("precision")))

    @staticmethod
    def _campos_de(personaje):
        campos = {
            "nombre": personaje.nombre,
            "clase": personaje.clase,
            "nivel": personaje.nivel,
            "vida": personaje.vida,
            "ataque": personaje.ataque,
            "oro": float(personaje.oro),   # el seed guarda oro como número
        }
        if hasattr(personaje, "mana"):
            campos["mana"] = personaje.mana
        if hasattr(personaje, "precision"):
            campos["precision"] = personaje.precision
        return campos

    def _consultar(self, filtro):
        resultado = []
        for doc in self._personajes.find(filtro).sort("id_personaje", ASCENDING):
            resultado.append(self._documento_a_personaje(doc))
        return resultado

    def guardar(self, personaje):
        documento = self._campos_de(personaje)
        documento["inventario"] = []
        documento["misiones"] = []
        if self._personajes.find_one({"nombre": personaje.nombre}) is not None:
            raise DatoDuplicadoException(personaje.nombre)
        documento["id_personaje"] = self._siguiente_id()
        try:
            self._personajes.insert_one(documento)
        except DuplicateKeyError as error:
            raise DatoDuplicadoException(personaje.nombre) from error
        personaje.id = documento["id_personaje"]
        return personaje


    def buscar_por_id(self, id):
        doc = self._personajes.find_one({"id_personaje": id})
        return self._documento_a_personaje(doc) if doc else None

    def listar_todos(self):
        return self._consultar({})

    def listar_por_clase(self, clase):
        return self._consultar({"clase": clase})

    def actualizar(self, personaje):
        # $set cambia solo esos campos: el inventario y las misiones embebidas se conservan
        try:
            resultado = self._personajes.update_one({"id_personaje": personaje.id},
                                                    {"$set": self._campos_de(personaje)})
        except DuplicateKeyError as error:
            raise DatoDuplicadoException(personaje.nombre) from error
        return resultado.matched_count > 0

    def eliminar(self, id):
        # MongoDB no tiene llaves foráneas: no revisa si el personaje aparece en combates
        return self._personajes.delete_one({"id_personaje": id}).deleted_count > 0

    def listar_inventario(self, id_personaje):
        doc = self._personajes.find_one({"id_personaje": id_personaje}, {"inventario": 1})
        items = []
        if doc is None:
            return items
        for elemento in doc.get("inventario", []):
            items.append(Item(elemento.get("item"), elemento.get("tipo", "sin tipo"),
                              self._entero(elemento.get("valor", 0)),
                              self._entero(elemento.get("cantidad", 1))))
        return items

    def listar_catalogo(self):
        items = []
        for doc in self._items.find().sort([("tipo", ASCENDING), ("nombre", ASCENDING)]):
            items.append(Item(doc["nombre"], doc["tipo"], self._entero(doc["valor"])))
        return items

    def agregar_item(self, id_personaje, nombre_item, cantidad):
        resultado = self._personajes.update_one(
            {"id_personaje": id_personaje, "inventario.item": nombre_item},
            {"$inc": {"inventario.$.cantidad": cantidad}})
        if resultado.matched_count > 0:
            return True
        # 2. Si no lo tiene: se copia del catálogo y se agrega al arreglo con $push
        del_catalogo = self._items.find_one({"nombre": nombre_item})
        if del_catalogo is None:
            return False
        nuevo = {"item": del_catalogo["nombre"], "tipo": del_catalogo["tipo"],
                 "valor": del_catalogo["valor"], "cantidad": cantidad}
        resultado = self._personajes.update_one({"id_personaje": id_personaje},
                                                {"$push": {"inventario": nuevo}})
        return resultado.matched_count > 0


    def quitar_item(self, id_personaje, nombre_item):
        # $pull saca del arreglo los elementos que cumplan la condición
        resultado = self._personajes.update_one({"id_personaje": id_personaje},
                                                {"$pull": {"inventario": {"item": nombre_item}}})
        return resultado.modified_count > 0