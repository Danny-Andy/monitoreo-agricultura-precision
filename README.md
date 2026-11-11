# Monitoreo Agricultura de Precisión

Sistema web de monitoreo para agricultura de precisión del Grupo 5 de Ingeniería de Software UDH.

## Iniciar la aplicación

Desde PowerShell, abre la carpeta `src` y ejecuta:

```powershell
cd src
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Abre <http://127.0.0.1:5000> en el navegador. Si ya existe `.venv`, actívalo y omite la creación del entorno. La base de datos SQLite se crea en `src/agricultura.db` al iniciar `app.py`.

## Módulo de parcelas

Permite registrar, listar, buscar, editar y eliminar parcelas. Los datos incluyen nombre, ubicación, área en hectáreas y cultivo.

## Módulo de mediciones

Las mediciones se registran manualmente y se asocian a una parcela existente. Cada lectura incluye sensor o tipo de medición, valor, unidad, fecha, hora y una observación opcional.

- `/mediciones/` muestra el historial y permite filtrar por rango de fechas y parcela.
- `/mediciones/ultima` muestra la lectura más reciente de todo el sistema o de una parcela seleccionada.
- `/mediciones/nueva` permite registrar una lectura.

Las fechas del historial incluyen el día inicial y el día final seleccionados. Si se elimina una parcela, SQLite elimina también las mediciones vinculadas a ella.
