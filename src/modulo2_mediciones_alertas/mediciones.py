import math
from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for

from db import obtener_conexion


mediciones_bp = Blueprint("mediciones", __name__, url_prefix="/mediciones")


def _obtener_parcelas():
    with obtener_conexion() as conexion:
        return conexion.execute(
            "SELECT id, nombre FROM parcelas ORDER BY nombre COLLATE NOCASE, id"
        ).fetchall()


def _leer_medicion(id_medicion=None, parcela_id=None):
    consulta = (
        "SELECT m.*, p.nombre AS parcela_nombre, p.ubicacion AS parcela_ubicacion "
        "FROM mediciones AS m JOIN parcelas AS p ON p.id = m.parcela_id"
    )
    parametros = []
    filtros = []
    if id_medicion is not None:
        filtros.append("m.id = ?")
        parametros.append(id_medicion)
    if parcela_id is not None:
        filtros.append("m.parcela_id = ?")
        parametros.append(parcela_id)
    if filtros:
        consulta += " WHERE " + " AND ".join(filtros)
    consulta += " ORDER BY m.fecha_medicion DESC, m.id DESC LIMIT 1"
    with obtener_conexion() as conexion:
        return conexion.execute(consulta, parametros).fetchone()


def _validar_rango(desde, hasta):
    errores = []
    fecha_desde = None
    fecha_hasta = None
    if desde:
        try:
            fecha_desde = date.fromisoformat(desde)
        except ValueError:
            errores.append("La fecha inicial no es válida.")
    if hasta:
        try:
            fecha_hasta = date.fromisoformat(hasta)
        except ValueError:
            errores.append("La fecha final no es válida.")
    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
        errores.append("La fecha inicial debe ser anterior o igual a la fecha final.")
    return errores


def _datos_formulario():
    sensor = request.form.get("sensor", "").strip()
    valor = request.form.get("valor", "").strip()
    unidad = request.form.get("unidad", "").strip()
    fecha_medicion = request.form.get("fecha_medicion", "").strip()
    observacion = request.form.get("observacion", "").strip()
    parcela_id = request.form.get("parcela_id", "").strip()
    errores = []

    if not sensor:
        errores.append("El nombre del sensor o tipo de medición es obligatorio.")
    elif len(sensor) > 80:
        errores.append("El sensor no puede superar los 80 caracteres.")
    if not unidad:
        errores.append("La unidad es obligatoria.")
    elif len(unidad) > 20:
        errores.append("La unidad no puede superar los 20 caracteres.")
    if len(observacion) > 500:
        errores.append("La observación no puede superar los 500 caracteres.")

    numero = None
    try:
        numero = float(valor)
        if not math.isfinite(numero):
            errores.append("El valor debe ser un número válido.")
    except ValueError:
        errores.append("El valor de la medición debe ser numérico.")

    fecha_normalizada = ""
    try:
        fecha_hora = datetime.fromisoformat(fecha_medicion)
        if fecha_hora.tzinfo is not None:
            raise ValueError
        fecha_normalizada = fecha_hora.isoformat(timespec="minutes")
    except ValueError:
        errores.append("La fecha y hora de la medición no son válidas.")

    id_parcela = None
    try:
        id_parcela = int(parcela_id)
    except ValueError:
        errores.append("Selecciona una parcela válida.")
    if id_parcela is not None:
        with obtener_conexion() as conexion:
            existe = conexion.execute(
                "SELECT 1 FROM parcelas WHERE id = ?", (id_parcela,)
            ).fetchone()
        if existe is None:
            errores.append("La parcela seleccionada no existe.")

    formulario = {
        "sensor": sensor,
        "valor": valor,
        "unidad": unidad,
        "fecha_medicion": fecha_medicion,
        "observacion": observacion,
        "parcela_id": parcela_id,
    }
    valores = (id_parcela, sensor, numero, unidad, fecha_normalizada, observacion)
    return formulario, errores, valores


@mediciones_bp.route("/")
def historial():
    desde = request.args.get("desde", "").strip()
    hasta = request.args.get("hasta", "").strip()
    parcela_id = request.args.get("parcela_id", "").strip()
    errores = _validar_rango(desde, hasta)
    id_parcela = None
    if parcela_id:
        try:
            id_parcela = int(parcela_id)
        except ValueError:
            errores.append("La parcela seleccionada no es válida.")
        if id_parcela is not None:
            with obtener_conexion() as conexion:
                existe = conexion.execute(
                    "SELECT 1 FROM parcelas WHERE id = ?", (id_parcela,)
                ).fetchone()
            if existe is None:
                errores.append("La parcela seleccionada no existe.")
    if errores:
        for error in errores:
            flash(error, "error")
        mediciones = []
        respuesta = 400
    else:
        consulta = (
            "SELECT m.*, p.nombre AS parcela_nombre "
            "FROM mediciones AS m JOIN parcelas AS p ON p.id = m.parcela_id"
        )
        filtros = []
        parametros = []
        if desde:
            filtros.append("m.fecha_medicion >= ?")
            parametros.append(f"{desde}T00:00")
        if hasta:
            filtros.append("m.fecha_medicion <= ?")
            parametros.append(f"{hasta}T23:59")
        if id_parcela is not None:
            filtros.append("m.parcela_id = ?")
            parametros.append(id_parcela)
        if filtros:
            consulta += " WHERE " + " AND ".join(filtros)
        consulta += " ORDER BY m.fecha_medicion DESC, m.id DESC"
        with obtener_conexion() as conexion:
            mediciones = conexion.execute(consulta, parametros).fetchall()
        respuesta = 200

    with obtener_conexion() as conexion:
        total = conexion.execute("SELECT COUNT(*) FROM mediciones").fetchone()[0]
    return render_template(
        "mediciones/historial.html",
        mediciones=mediciones,
        ultima_medicion=_leer_medicion(),
        parcelas=_obtener_parcelas(),
        desde=desde,
        hasta=hasta,
        parcela_id=parcela_id,
        total=total,
    ), respuesta


@mediciones_bp.route("/ultima")
def ultima():
    parcela_id = request.args.get("parcela_id", "").strip()
    id_parcela = None
    if parcela_id:
        try:
            id_parcela = int(parcela_id)
        except ValueError:
            flash("La parcela seleccionada no es válida.", "error")
            return redirect(url_for("mediciones.ultima"))
        with obtener_conexion() as conexion:
            existe = conexion.execute(
                "SELECT 1 FROM parcelas WHERE id = ?", (id_parcela,)
            ).fetchone()
        if existe is None:
            flash("La parcela seleccionada no existe.", "error")
            return redirect(url_for("mediciones.ultima"))
    return render_template(
        "mediciones/ultima.html",
        medicion=_leer_medicion(parcela_id=id_parcela),
        parcelas=_obtener_parcelas(),
        parcela_id=parcela_id,
    )


@mediciones_bp.route("/nueva", methods=["GET", "POST"])
def registrar():
    parcelas = _obtener_parcelas()
    if request.method == "POST":
        formulario, errores, valores = _datos_formulario()
        id_parcela, sensor, numero, unidad, fecha_medicion, observacion = valores
        if errores:
            for error in errores:
                flash(error, "error")
            return render_template(
                "mediciones/formulario.html", parcelas=parcelas, medicion=formulario
            ), 400
        with obtener_conexion() as conexion:
            conexion.execute(
                "INSERT INTO mediciones "
                "(parcela_id, sensor, valor, unidad, fecha_medicion, observacion) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (id_parcela, sensor, numero, unidad, fecha_medicion, observacion),
            )
        flash("Medición registrada correctamente.", "ok")
        return redirect(url_for("mediciones.historial"))

    ahora = datetime.now().replace(second=0, microsecond=0).isoformat(timespec="minutes")
    return render_template(
        "mediciones/formulario.html",
        parcelas=parcelas,
        medicion={"fecha_medicion": ahora},
    )
