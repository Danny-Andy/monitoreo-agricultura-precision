from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import obtener_conexion

umbrales_bp = Blueprint("umbrales", __name__, url_prefix="/umbrales")

@umbrales_bp.route("/")
def listar():
    with obtener_conexion() as conexion:
        umbrales = conexion.execute("SELECT * FROM umbrales").fetchall()
    return render_template("umbrales/lista.html", umbrales=umbrales)

@umbrales_bp.route("/crear", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        id_parcela = request.form["id_parcela"]
        tipo_medida = request.form["tipo_medida"]
        valor_minimo = float(request.form["valor_minimo"])
        valor_maximo = float(request.form["valor_maximo"])

        # Validación (SEC-13)
        if valor_minimo >= valor_maximo:
            flash("El valor mínimo debe ser menor que el valor máximo", "error")
            return redirect(url_for("umbrales.crear"))

        with obtener_conexion() as conexion:
            conexion.execute(
                "INSERT INTO umbrales (id_parcela, tipo_medida, valor_minimo, valor_maximo) VALUES (?, ?, ?, ?)",
                (id_parcela, tipo_medida, valor_minimo, valor_maximo)
            )

        flash("Umbral registrado correctamente", "success")
        return redirect(url_for("umbrales.listar"))

    # Para el GET, necesitamos listar las parcelas para el select
    with obtener_conexion() as conexion:
        parcelas = conexion.execute("SELECT id, nombre FROM parcelas").fetchall()
    return render_template("umbrales/formulario.html", parcelas=parcelas)
    @umbrales_bp.route("/cambiar-estado/<int:id>")
    def cambiar_estado(id):
        with obtener_conexion() as conexion:
            # Buscamos el estado actual
            umbral = conexion.execute("SELECT activo FROM umbrales WHERE id = ?", (id,)).fetchone()
            if umbral:
                nuevo_estado = 0 if umbral["activo"] == 1 else 1
                conexion.execute("UPDATE umbrales SET activo = ? WHERE id = ?", (nuevo_estado, id))
        return redirect(url_for("umbrales.listar"))