from flask import Flask, redirect, url_for

from db import crear_tablas
from modulo1_parcelas_sensores.parcelas import parcelas_bp

app = Flask(__name__)
app.secret_key = "clave-de-desarrollo"
app.register_blueprint(parcelas_bp)


@app.route("/")
def inicio():
    return redirect(url_for("parcelas.listar"))


if __name__ == "__main__":
    crear_tablas()
    app.run(debug=True)