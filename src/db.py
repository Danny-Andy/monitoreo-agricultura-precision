import sqlite3
from pathlib import Path

RUTA_BD = Path(__file__).parent / "agricultura.db"


def obtener_conexion():
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    return conexion


def crear_tablas():
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS parcelas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                ubicacion TEXT NOT NULL,
                area_hectareas REAL NOT NULL,
                cultivo TEXT NOT NULL
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS sensores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL,
                unidad TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1,
                id_parcela INTEGER NOT NULL,
                FOREIGN KEY (id_parcela) REFERENCES parcelas(id)
            )
            """
        )