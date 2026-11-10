from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import obtener_conexion

parcelas_bp = Blueprint("parcelas", __name__, url_prefix="/parcelas")


def validar_parcela(nombre, ubicacion, area, cultivo):
    """Devuelve la lista de errores. Si está vacía, los datos son válidos."""
    errores = []
    if not nombre:
        errores.append("El nombre es obligatorio.")
    if not ubicacion:
        errores.append("La ubicación es obligatoria.")
    if not cultivo:
        errores.append("El cultivo es obligatorio.")
    try:
        if float(area) <= 0:
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
        request.form["nombre"].strip(),
        request.form["ubicacion"].strip(),
        request.form["area"].strip(),
        request.form["cultivo"].strip(),
    )


@parcelas_bp.route("/")
def listar():
    with obtener_conexion() as conexion:
        parcelas = conexion.execute("SELECT * FROM parcelas ORDER BY id").fetchall()
    return render_template("parcelas/lista.html", parcelas=parcelas)


@parcelas_bp.route("/nueva", methods=["GET", "POST"])
def crear():
    if request.method == "POST":
        nombre, ubicacion, area, cultivo = leer_formulario()

        errores = validar_parcela(nombre, ubicacion, area, cultivo)
        if errores:
            for error in errores:
                flash(error, "error")
            return render_template("parcelas/formulario.html", parcela=dict(request.form))

        with obtener_conexion() as conexion:
            conexion.execute(
                "INSERT INTO parcelas (nombre, ubicacion, area_hectareas, cultivo) "
                "VALUES (?, ?, ?, ?)",
                (nombre, ubicacion, float(area), cultivo),
            )
        flash("Parcela registrada correctamente.", "ok")
        return redirect(url_for("parcelas.listar"))

    return render_template("parcelas/formulario.html", parcela={})


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
            return render_template("parcelas/formulario.html", parcela=dict(request.form))

        with obtener_conexion() as conexion:
            conexion.execute(
                "UPDATE parcelas SET nombre = ?, ubicacion = ?, "
                "area_hectareas = ?, cultivo = ? WHERE id = ?",
                (nombre, ubicacion, float(area), cultivo, id_parcela),
            )
        flash("Parcela actualizada correctamente.", "ok")
        return redirect(url_for("parcelas.listar"))

    return render_template("parcelas/formulario.html", parcela=dict(parcela))


@parcelas_bp.route("/<int:id_parcela>/eliminar", methods=["POST"])
def eliminar(id_parcela):
    with obtener_conexion() as conexion:
        conexion.execute("DELETE FROM parcelas WHERE id = ?", (id_parcela,))
    flash("Parcela eliminada.", "ok")
    return redirect(url_for("parcelas.listar"))