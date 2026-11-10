from flask import Blueprint, render_template, request, redirect, url_for, flash

from db import obtener_conexion

sensores_bp = Blueprint("sensores", __name__, url_prefix="/sensores")


@sensores_bp.route("/")
def listar():
    with obtener_conexion() as conexion:
        sensores = conexion.execute(
            "SELECT s.id, s.codigo, s.tipo, s.unidad, s.activo, "
            "p.nombre AS parcela "
            "FROM sensores s JOIN parcelas p ON p.id = s.id_parcela "
            "ORDER BY s.id"
        ).fetchall()
    return render_template("sensores/lista.html", sensores=sensores)