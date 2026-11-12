from flask import Flask, redirect, url_for

from modulo2_mediciones_alertas.umbrales import umbrales_bp
from modulo2_mediciones_alertas.alertas import alertas_bp

from db import crear_tablas
from modulo1_parcelas_sensores.parcelas import parcelas_bp
from modulo2_mediciones_alertas.mediciones import mediciones_bp

app = Flask(__name__)
app.secret_key = "clave-de-desarrollo"
app.register_blueprint(parcelas_bp)
app.register_blueprint(mediciones_bp)

app.register_blueprint(umbrales_bp)
app.register_blueprint(alertas_bp)


@app.route("/")
def inicio():
    return redirect(url_for("parcelas.listar"))


if __name__ == "__main__":
    crear_tablas()
    app.run(debug=True)
