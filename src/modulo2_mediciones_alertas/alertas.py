from flask import Blueprint, render_template, redirect, url_for
from datetime import datetime
from db import obtener_conexion

alertas_bp = Blueprint("alertas", __name__, url_prefix="/alertas")

def evaluar_medicion(id_parcela, tipo_medida, valor):
    # Esta línea de abajo debe tener exactamente 4 espacios:
    with obtener_conexion() as conexion:
        umbral = conexion.execute(
            "SELECT * FROM umbrales WHERE id_parcela = ? AND tipo_medida = ? AND activo = 1",
            (id_parcela, tipo_medida)
        ).fetchone()

        if umbral:
            if valor < umbral["valor_minimo"] or valor > umbral["valor_maximo"]:
                mensaje = f"Alerta: El valor {valor} de {tipo_medida} está fuera del rango ({umbral['valor_minimo']} - {umbral['valor_maximo']})"
                nivel = "Crítico"
                fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Esta línea debe tener 8 espacios:
                conexion.execute(
                    "INSERT INTO alertas (id_umbral, mensaje, nivel, fecha_hora) VALUES (?, ?, ?, ?)",
                    (umbral["id"], mensaje, nivel, fecha_hora)
                )

@alertas_bp.route("/")
def listar():
    with obtener_conexion() as conexion:
        alertas = conexion.execute("SELECT * FROM alertas ORDER BY fecha_hora DESC").fetchall()
    return render_template("alertas/lista.html", alertas=alertas)

@alertas_bp.route("/leer/<int:id>")
def marcar_leida(id):
    with obtener_conexion() as conexion:
        conexion.execute("UPDATE alertas SET leida = 1 WHERE id = ?", (id,))
    return redirect(url_for("alertas.listar"))