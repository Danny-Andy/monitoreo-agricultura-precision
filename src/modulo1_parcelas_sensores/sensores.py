from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import obtener_conexion

sensores_bp = Blueprint("sensores", __name__, url_prefix="/sensores")

UNIDADES = {"humedad": "%", "temperatura": "°C", "nivel_agua": "cm"}


def obtener_parcelas():
    with obtener_conexion() as conexion:
        return conexion.execute(
            "SELECT id, nombre FROM parcelas ORDER BY nombre"
        ).fetchall()
    
def validar_sensor(codigo, tipo, id_parcela):
    """Devuelve la lista de errores. Si está vacía, los datos son válidos."""
    errores = []
    if not codigo:
        errores.append("El código es obligatorio.")
    else:
        with obtener_conexion() as conexion:
            repetido = conexion.execute(
                "SELECT id FROM sensores WHERE codigo = ?", (codigo,)
            ).fetchone()
        if repetido:
            errores.append("Ya existe un sensor con ese código.")

    if tipo not in UNIDADES:
        errores.append("El tipo debe ser humedad, temperatura o nivel_agua.")

    with obtener_conexion() as conexion:
        parcela = conexion.execute(
            "SELECT id FROM parcelas WHERE id = ?", (id_parcela,)
        ).fetchone()
    if parcela is None:
        errores.append("La parcela seleccionada no existe.")
    return errores

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
        codigo = request.form.get("codigo", "").strip()
        tipo = request.form.get("tipo", "")
        id_parcela = request.form.get("id_parcela", "")

        errores = validar_sensor(codigo, tipo, id_parcela)
        if errores:
            for error in errores:
                flash(error, "error")
            return render_template(
                "sensores/formulario.html",
                sensor=dict(request.form),
                parcelas=obtener_parcelas(),
                tipos=list(UNIDADES),
            )

        with obtener_conexion() as conexion:
            conexion.execute(
                "INSERT INTO sensores (codigo, tipo, unidad, id_parcela) "
                "VALUES (?, ?, ?, ?)",
                (codigo, tipo, UNIDADES[tipo], id_parcela),
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