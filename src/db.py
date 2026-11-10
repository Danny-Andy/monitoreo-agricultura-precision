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