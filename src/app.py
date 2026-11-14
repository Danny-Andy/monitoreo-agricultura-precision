from flask import Flask, redirect, url_for

from db import crear_tablas
from modulo1_parcelas_sensores.parcelas import parcelas_bp
from modulo1_parcelas_sensores.sensores import sensores_bp
from modulo2_mediciones_alertas.mediciones import mediciones_bp

app = Flask(__name__)
app.secret_key = "clave-de-desarrollo"
app.register_blueprint(parcelas_bp)
app.register_blueprint(sensores_bp)
app.register_blueprint(mediciones_bp)