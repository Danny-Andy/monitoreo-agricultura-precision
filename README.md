# Sistema de monitoreo para agricultura de precisión

Proyecto grupal del Grupo 5 - Ingeniería de Software - Universidad de Huánuco.
Docente: Mg. Omar Sulca Correa.

## Descripción
Sistema web para registrar parcelas, sensores y mediciones agrícolas, con umbrales y alertas.

## Integrantes y módulos
- Danny Andy Parinango Navarro: Módulo 1 - Parcelas
- Manuel Baylon Castro: Módulo 1 - Sensores
- Ronaldho Mallqui Paredes: Módulo 2 - Mediciones
- Jhoe Josue Rivera Ponce: Módulo 2 - Umbrales y alertas

## Tecnologías
Python 3, Flask, SQLite, HTML y CSS.

## Cómo ejecutar

### Requisitos
- Python 3.10 o superior
- Git

### Configuración
```powershell
git clone https://github.com/Danny-Andy/monitoreo-agricultura-precision.git
cd monitoreo-agricultura-precision
pip install -r src\requirements.txt
```

### Pasos
1. Iniciar la aplicación: `python src\app.py`
2. Abrir en el navegador: http://127.0.0.1:5000
3. Detener el servidor con Ctrl + C.

La base de datos se crea sola en `src/agricultura.db` y no se sube al repositorio.

## Forma de trabajo
- Una rama por integrante (`feature/...`).
- Cambios a `main` con pull request revisado por otro integrante.
- Mensajes de commit claros y en presente.
