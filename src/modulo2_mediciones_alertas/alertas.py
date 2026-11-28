from flask import Blueprint, render_template, redirect, url_for, request, flash
from datetime import datetime
from db import obtener_conexion

alertas_bp = Blueprint("alertas", __name__, url_prefix="/alertas")

def evaluar_medicion(id_parcela, tipo_medida, valor):
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

                conexion.execute(
                    "INSERT INTO alertas (id_umbral, mensaje, nivel, fecha_hora) VALUES (?, ?, ?, ?)",
                    (umbral["id"], mensaje, nivel, fecha_hora)
                )

@alertas_bp.route("/")
def listar():
    filtro = request.args.get("filtro", "todas")
    with obtener_conexion() as conexion:
        if filtro == "no_leidas":
            alertas = conexion.execute("SELECT * FROM alertas WHERE leida = 0 ORDER BY fecha_hora DESC").fetchall()
        elif filtro == "leidas":
            alertas = conexion.execute("SELECT * FROM alertas WHERE leida = 1 ORDER BY fecha_hora DESC").fetchall()
        else:
            alertas = conexion.execute("SELECT * FROM alertas ORDER BY fecha_hora DESC").fetchall()

        total_alertas = conexion.execute("SELECT COUNT(*) FROM alertas").fetchone()[0]
        no_leidas = conexion.execute("SELECT COUNT(*) FROM alertas WHERE leida=0").fetchone()[0]
        criticas = conexion.execute("SELECT COUNT(*) FROM alertas WHERE nivel='Crítico'").fetchone()[0]

    return render_template("alertas/lista.html", alertas=alertas, total=total_alertas, no_leidas=no_leidas, criticas=criticas, filtro=filtro)

@alertas_bp.route("/leer/<int:id>")
def marcar_leida(id):
    with obtener_conexion() as conexion:
        conexion.execute("UPDATE alertas SET leida = 1 WHERE id = ?", (id,))
    return redirect(url_for("alertas.listar"))

@alertas_bp.route("/leer-todas")
def leer_todas():
    with obtener_conexion() as conexion:
        conexion.execute("UPDATE alertas SET leida = 1 WHERE leida = 0")
    flash("Todas las alertas han sido marcadas como leídas", "success")
    return redirect(url_for("alertas.listar"))
@alertas_bp.route("/limpiar")
def limpiar_alertas():
    with obtener_conexion() as conexion:
        conexion.execute("DELETE FROM alertas WHERE leida = 1")
    flash("Historial de alertas leídas limpiado correctamente", "success")
    return redirect(url_for("alertas.listar"))