# EcoTech Solutions

Sistema de gestión de empleados, departamentos, proyectos, registros de tiempo e indicadores externos.

## Estructura del proyecto

Se conserva la organización de la entrega original: los módulos de la aplicación permanecen dentro de `DOC_2/src`, separados por capas. Los archivos de configuración, SQL, documentación y diagramas quedan en la raíz.

```text
POOS-P13C3_Diego_florez-main/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── ecotech_mysql.sql
├── diagrama uml del proyecto.svg
├── diagrama uml del proyecto actualizado.puml
├── diagrama uml actualizado roles.svg
├── DOC_2/
│   └── src/
│       ├── main.py
│       ├── semilla.py
│       ├── prueba_api.py
│       ├── probar_interfaz_sin_db.py
│       ├── dominio/
│       ├── persistencia/
│       ├── servicios/
│       └── ux/
└── README_POOS_Paso_a_Paso_Resumido_MySQL_GitBash.txt
```

## Funcionalidades incluidas

- Gestión de empleados, departamentos, proyectos, asignaciones y registros de tiempo.
- Roles `admin` y `empleado`, autenticación bcrypt y controles de permisos.
- Consulta del dólar mediante Mindicador, validación/deserialización JSON e historial local.
- Respaldo desde el último indicador guardado cuando la API no responde.
- Semilla de datos ficticios idempotente.
- Selección de MariaDB/MySQL o SQLite.

## 1. Preparación en Git Bash

Abre en VS Code la carpeta raíz que contiene `requirements.txt` y `DOC_2`. En Git Bash ejecuta:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
cp .env.example .env
```

Edita `.env` y escribe la contraseña real de MariaDB en `DB_PASSWORD`. La configuración inicial apunta al puerto `3307` y a una base de datos nueva llamada `ecotech_solutions_nueva`. No modifica `ecotech_db`.

```dotenv
DB_BACKEND=mysql
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=TU_CONTRASENA
DB_NAME=ecotech_solutions_nueva
SQLITE_PATH=ecotech_solutions_nueva.db
```

## 2. Ejecutar el sistema

Desde la raíz del proyecto:

```bash
python DOC_2/src/main.py
```

La aplicación crea la base y sus tablas si no existen, carga los datos de demostración sin duplicarlos y prepara la cuenta administrativa inicial si corresponde. Define una contraseña cuando el programa lo solicite.

## 3. Comprobar la semilla en Workbench

Conecta Workbench a `127.0.0.1`, puerto `3307`, usuario `root`, y ejecuta:

```sql
USE ecotech_solutions_nueva;
SELECT COUNT(*) FROM departamento;
SELECT COUNT(*) FROM empleado;
SELECT COUNT(*) FROM proyecto;
SELECT COUNT(*) FROM empleado_proyecto;
SELECT COUNT(*) FROM registro_tiempo;
SELECT COUNT(*) FROM indicador_api;
```

Los nombres de demostración comienzan con `SEMILLA -` en departamentos y proyectos; los correos de empleados comienzan con `semilla.empleado`.

## 4. Pruebas auxiliares

```bash
python DOC_2/src/prueba_api.py
python DOC_2/src/probar_interfaz_sin_db.py
```

La prueba de interfaz utiliza DAO simulados en memoria y no comprueba la conexión real a MySQL. La prueba API requiere Internet.

## 5. Usar SQLite en vez de MariaDB

En `.env`, cambia `DB_BACKEND=mysql` por `DB_BACKEND=sqlite`. El archivo local se guardará en la raíz del proyecto. MySQL y SQLite no comparten ni sincronizan datos.

## 6. Precauciones

- No elimines `ecotech_db`: esta versión utiliza `ecotech_solutions_nueva`.
- No compartas el archivo `.env`, porque contiene credenciales.
- La semilla no borra datos ajenos ni modifica automáticamente roles de cuentas existentes.
- La API climática y el cálculo de pagos internacionales no se consideran implementados en esta versión.
