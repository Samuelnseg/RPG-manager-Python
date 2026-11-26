"""Selector: lee la configuración y crea la implementación del contrato.

Es el único lugar del proyecto que sabe qué motor hay detrás.
"""
from Repositorio.RepositorioMariaDB import RepositorioMariaDB
from Repositorio.Repositorio_memoria import RepositorioMemoria
from Repositorio.repositorio_mongo import RepositorioMongo


def crear_repositorio(cfg):
    tipo = cfg.get("app", "repositorio", fallback="").strip().lower()
    if tipo == "memoria":
        return RepositorioMemoria()
    elif tipo == "mariadb":
        return RepositorioMariaDB(
            host=cfg.get("mariadb", "host"),
            puerto=cfg.get("mariadb", "puerto"),
            base=cfg.get("mariadb", "base"),
            usuario=cfg.get("mariadb", "usuario"),
            clave=cfg.get("mariadb", "clave"))
    elif tipo == "mongo":
        return RepositorioMongo(uri=cfg.get("mongo", "uri"), base=cfg.get("mongo", "base"))
    # Mejor que la app no arranque a que falle en la primera petición
    raise ValueError(f"Repositorio desconocido: '{tipo}'. Usa memoria, mariadb o mongo.")
