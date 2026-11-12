import sqlite3
from contextlib import contextmanager
from pathlib import Path

RUTA_BD = Path(__file__).parent / "agricultura.db"


@contextmanager
def obtener_conexion():
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    try:
        yield conexion
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        conexion.close()


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
            CREATE TABLE IF NOT EXISTS mediciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parcela_id INTEGER NOT NULL,
                sensor TEXT NOT NULL,
                valor REAL NOT NULL,
                unidad TEXT NOT NULL,
                fecha_medicion TEXT NOT NULL,
                observacion TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (parcela_id) REFERENCES parcelas(id) ON DELETE CASCADE
            )
            """
        )
        conexion.execute(
            "CREATE INDEX IF NOT EXISTS idx_mediciones_fecha "
            "ON mediciones(fecha_medicion DESC, id DESC)"
        )
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS umbrales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_parcela INTEGER NOT NULL,
                tipo_medida TEXT NOT NULL,
                valor_minimo REAL NOT NULL,
                valor_maximo REAL NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (id_parcela) REFERENCES parcelas(id) ON DELETE CASCADE
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_umbral INTEGER NOT NULL,
                mensaje TEXT NOT NULL,
                nivel TEXT NOT NULL,
                fecha_hora TEXT NOT NULL,
                leida INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (id_umbral) REFERENCES umbrales(id) ON DELETE CASCADE
            )
            """
        )
