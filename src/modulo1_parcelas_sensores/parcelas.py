import math

from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import obtener_conexion

parcelas_bp = Blueprint("parcelas", __name__, url_prefix="/parcelas")


def validar_parcela(nombre, ubicacion, area, cultivo):
    """Devuelve la lista de errores. Si está vacía, los datos son válidos."""
    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio.")
    elif len(nombre) > 100:
        errores.append("El nombre no puede superar los 100 caracteres.")
    if not ubicacion:
        errores.append("La ubicación es obligatoria.")
    elif len(ubicacion) > 200:
        errores.append("La ubicación no puede superar los 200 caracteres.")
    if not cultivo:
        errores.append("El cultivo es obligatorio.")
    elif len(cultivo) > 100:
        errores.append("El cultivo no puede superar los 100 caracteres.")
    try:
        valor_area = float(area)
        if not math.isfinite(valor_area):
            errores.append("El área debe ser un número válido.")
        elif valor_area <= 0:
            errores.append("El área debe ser mayor que 0.")
    except ValueError:
        errores.append("El área debe ser un número.")
    return errores


def obtener_parcela(id_parcela):
    with obtener_conexion() as conexion:
        return conexion.execute(
            "SELECT * FROM parcelas WHERE id = ?", (id_parcela,)
        ).fetchone()


def leer_formulario():
    return (
        request.form.get("nombre", "").strip(),
        request.form.get("ubicacion", "").strip(),
        request.form.get("area", "").strip(),
        request.form.get("cultivo", "").strip(),
    )


@parcelas_bp.route("/")
def listar():
    busqueda = request.args.get("q", "").strip()
    with obtener_conexion() as conexion:
        if busqueda:
            termino = f"%{busqueda}%"
            parcelas = conexion.execute(
                "SELECT * FROM parcelas "
                "WHERE nombre LIKE ? COLLATE NOCASE "
                "OR ubicacion LIKE ? COLLATE NOCASE "
                "OR cultivo LIKE ? COLLATE NOCASE ORDER BY nombre COLLATE NOCASE, id",
                (termino, termino, termino),
            ).fetchall()
        else:
            parcelas = conexion.execute(
                "SELECT * FROM parcelas ORDER BY nombre COLLATE NOCASE, id"
            ).fetchall()
        resumen = conexion.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(area_hectareas), 0) AS hectareas, "
            "COUNT(DISTINCT cultivo) AS cultivos FROM parcelas"
        ).fetchone()
    return render_template(
        "parcelas/lista.html", parcelas=parcelas, busqueda=busqueda, resumen=resumen
    )


@parcelas_bp.route("/nueva", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        nombre, ubicacion, area, cultivo = leer_formulario()

        errores = validar_parcela(nombre, ubicacion, area, cultivo)
        if errores:
            for error in errores:
                flash(error, "error")
            return render_template(
                "parcelas/formulario.html", parcela=dict(request.form), modo="crear"
            ), 400

        with obtener_conexion() as conexion:
            conexion.execute(
                "INSERT INTO parcelas (nombre, ubicacion, area_hectareas, cultivo) "
                "VALUES (?, ?, ?, ?)",
                (nombre, ubicacion, float(area), cultivo),
            )
        flash("Parcela registrada correctamente.", "ok")
        return redirect(url_for("parcelas.listar"))

    return render_template("parcelas/formulario.html", parcela={}, modo="crear")


@parcelas_bp.route("/<int:id_parcela>/editar", methods=["GET", "POST"])
def editar(id_parcela):
    parcela = obtener_parcela(id_parcela)
    if parcela is None:
        flash("La parcela no existe.", "error")
        return redirect(url_for("parcelas.listar"))

    if request.method == "POST":
        nombre, ubicacion, area, cultivo = leer_formulario()

        errores = validar_parcela(nombre, ubicacion, area, cultivo)
        if errores:
            for error in errores:
                flash(error, "error")
            return render_template(
                "parcelas/formulario.html", parcela=dict(request.form),
                modo="editar", id_parcela=id_parcela,
            ), 400

        with obtener_conexion() as conexion:
            conexion.execute(
                "UPDATE parcelas SET nombre = ?, ubicacion = ?, "
                "area_hectareas = ?, cultivo = ? WHERE id = ?",
                (nombre, ubicacion, float(area), cultivo, id_parcela),
            )
        flash("Parcela actualizada correctamente.", "ok")
        return redirect(url_for("parcelas.listar"))

    return render_template(
        "parcelas/formulario.html", parcela=dict(parcela),
        modo="editar", id_parcela=id_parcela,
    )


@parcelas_bp.route("/<int:id_parcela>/eliminar", methods=["POST"])
def eliminar(id_parcela):
    with obtener_conexion() as conexion:
        resultado = conexion.execute("DELETE FROM parcelas WHERE id = ?", (id_parcela,))
    if resultado.rowcount == 0:
        flash("La parcela que intentas eliminar ya no existe.", "error")
        return redirect(url_for("parcelas.listar"))
    flash("Parcela eliminada.", "ok")
    return redirect(url_for("parcelas.listar"))
