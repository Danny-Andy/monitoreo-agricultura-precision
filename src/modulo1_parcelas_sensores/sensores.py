from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import obtener_conexion

sensores_bp = Blueprint("sensores", __name__, url_prefix="/sensores")

UNIDADES = {"humedad": "%", "temperatura": "°C", "nivel_agua": "cm"}


def obtener_parcelas():
    with obtener_conexion() as conexion:
        return conexion.execute(
            "SELECT id, nombre FROM parcelas ORDER BY nombre"
        ).fetchall()


@sensores_bp.route("/")
def listar():
    id_parcela = request.args.get("parcela", "")
    consulta = (
        "SELECT s.id, s.codigo, s.tipo, s.unidad, s.activo, "
        "p.nombre AS parcela "
        "FROM sensores s JOIN parcelas p ON p.id = s.id_parcela"
    )
    parametros = ()
    if id_parcela:
        consulta += " WHERE s.id_parcela = ?"
        parametros = (id_parcela,)
    consulta += " ORDER BY s.id"

    with obtener_conexion() as conexion:
        sensores = conexion.execute(consulta, parametros).fetchall()
    return render_template(
        "sensores/lista.html",
        sensores=sensores,
        parcelas=obtener_parcelas(),
        id_parcela=id_parcela,
    )

@sensores_bp.route("/nuevo", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        codigo = request.form["codigo"].strip()
        tipo = request.form["tipo"]
        id_parcela = request.form["id_parcela"]
        unidad = UNIDADES[tipo]

        with obtener_conexion() as conexion:
            conexion.execute(
                "INSERT INTO sensores (codigo, tipo, unidad, id_parcela) "
                "VALUES (?, ?, ?, ?)",
                (codigo, tipo, unidad, id_parcela),
            )
        flash("Sensor registrado correctamente.", "ok")
        return redirect(url_for("sensores.listar"))

    return render_template(
        "sensores/formulario.html",
        sensor={},
        parcelas=obtener_parcelas(),
        tipos=list(UNIDADES),
    )
@sensores_bp.route("/<int:id_sensor>/estado", methods=["POST"])
def cambiar_estado(id_sensor):
    with obtener_conexion() as conexion:
        sensor = conexion.execute(
            "SELECT activo FROM sensores WHERE id = ?", (id_sensor,)
        ).fetchone()
        if sensor is None:
            flash("El sensor no existe.", "error")
            return redirect(url_for("sensores.listar"))

        nuevo_estado = 0 if sensor["activo"] else 1
        conexion.execute(
            "UPDATE sensores SET activo = ? WHERE id = ?",
            (nuevo_estado, id_sensor),
        )
    flash("Sensor activado." if nuevo_estado else "Sensor desactivado.", "ok")
    return redirect(url_for("sensores.listar"))