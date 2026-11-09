README - GUÍA RÁPIDA POOS
===========================

OBJETIVO
Implementar el UML en Python, aplicar POO, conectar MySQL, realizar CRUD,
manejar errores, validar datos y poder explicar el uso de IA.

INICIO EN GIT BASH
------------------

mkdir proyecto-poos
cd proyecto-poos
python -m venv venv
source venv/Scripts/activate
pip install mysql-connector-python
pip freeze > requirements.txt
touch main.py conexion.py modelos.py crud.py

Si usarás Git:
git init
git add .
git commit -m "Inicio proyecto POOS"

UML A PYTHON
------------

1. Identifica clases, atributos, constructor, métodos y relaciones.
2. Crea las clases según el UML.
3. Implementa __init__ y los métodos.
4. Implementa herencia o asociaciones cuando correspondan.

Ejemplo:

class Empleado:
    def __init__(self, nombre, sueldo):
        self.__nombre = nombre
        self.__sueldo = sueldo

    def get_nombre(self):
        return self.__nombre

El código debe mantener correspondencia con el UML.

HERENCIA Y ASOCIACIÓN
---------------------

Herencia:

class Gerente(Empleado):
    def __init__(self, nombre, area):
        super().__init__(nombre)
        self.area = area

Asociación:

class Empleado:
    def __init__(self, nombre, departamento):
        self.nombre = nombre
        self.departamento = departamento

ENCAPSULAMIENTO
---------------

Usa atributos privados cuando corresponda:

self.__nombre

Y métodos para controlar su acceso:

def get_nombre(self):
    return self.__nombre

def set_nombre(self, nombre):
    if nombre.strip():
        self.__nombre = nombre

Explicación: permite controlar y validar el acceso a los datos.

MYSQL
-----

Crear la base de datos:

CREATE DATABASE empresa;
USE empresa;

CREATE TABLE empleado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    sueldo DECIMAL(10,2) NOT NULL
);

Comprobar:

SHOW DATABASES;
SHOW TABLES;
DESCRIBE empleado;

CONEXIÓN MYSQL + PYTHON
-----------------------

Instalar:

pip install mysql-connector-python

conexion.py:

import mysql.connector

def conectar():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="TU_PASSWORD",
            database="empresa",
            port=3306
        )
        return conexion
    except mysql.connector.Error as e:
        print("Error de conexión:", e)
        return None

Parámetros: host, usuario, contraseña, base de datos y puerto.

CRUD
----

CREATE:
sql = "INSERT INTO empleado (nombre, sueldo) VALUES (%s, %s)"
cursor.execute(sql, (nombre, sueldo))
conexion.commit()

READ:
cursor.execute("SELECT * FROM empleado")
datos = cursor.fetchall()

UPDATE:
sql = """UPDATE empleado
         SET nombre = %s, sueldo = %s
         WHERE id = %s"""
cursor.execute(sql, (nombre, sueldo, id))
conexion.commit()

DELETE:
cursor.execute("DELETE FROM empleado WHERE id = %s", (id,))
conexion.commit()

CRUD significa:
CREATE = registrar
READ = consultar
UPDATE = actualizar
DELETE = eliminar

Usa parámetros (%s) y no concatentes directamente los datos del usuario.

VALIDACIONES Y TRY-EXCEPT
-------------------------

try:
    sueldo = float(input("Sueldo: "))
    if sueldo <= 0:
        print("Debe ser mayor que 0.")
except ValueError:
    print("Debe ingresar un número.")

Para MySQL:

except mysql.connector.Error as e:
    print("Error de MySQL:", e)

Explicación: try contiene la operación que puede fallar y except
captura el error para evitar que el programa termine abruptamente.

ORDEN PARA LA PRUEBA
--------------------

1. Revisar UML.
2. Crear clases, atributos, constructor y métodos.
3. Implementar relaciones y encapsulamiento.
4. Crear la base de datos MySQL.
5. Conectar Python con MySQL.
6. Probar la conexión.
7. Implementar y probar INSERT, SELECT, UPDATE y DELETE.
8. Agregar validaciones y try-except.
9. Probar errores.
10. Revisar y adaptar el código apoyado por IA.
11. Probar todo nuevamente.
12. Preparar la defensa.

PRUEBAS
-------

[ ] Registro válido.
[ ] Registro inválido.
[ ] Consulta.
[ ] Actualización.
[ ] Eliminación.
[ ] ID inexistente.
[ ] Campos vacíos.
[ ] Letras donde se espera un número.
[ ] Error de conexión o base de datos.

GIT BASH
--------

Ejecutar:
python main.py

Después de cambios:
git status
git add .
git commit -m "Implementar CRUD MySQL"

Si tienes repositorio remoto:
git remote add origin URL_DEL_REPOSITORIO
git branch -M main
git push -u origin main

COMANDOS MYSQL
--------------

SHOW DATABASES;
CREATE DATABASE empresa;
USE empresa;
SHOW TABLES;
DESCRIBE empleado;

SELECT * FROM empleado;

INSERT INTO empleado (nombre, sueldo)
VALUES ('Juan', 500000);

UPDATE empleado
SET sueldo = 600000
WHERE id = 1;

DELETE FROM empleado
WHERE id = 1;

DEFENSA
-------

¿Cómo corresponde Python con UML?
"Cada clase del UML se implementa como una clase Python y se mantienen
sus atributos, métodos y relaciones."

¿Qué es encapsulamiento?
"Permite controlar el acceso a los datos de una clase."

¿Qué es herencia?
"Permite que una clase hija reutilice atributos y métodos de una clase padre."

¿Qué es CRUD?
"Crear, consultar, actualizar y eliminar datos."

¿Por qué usar WHERE?
"Para identificar el registro que se quiere modificar o eliminar."

¿Por qué usar try-except?
"Para controlar errores y evitar que el programa termine."

¿Por qué validar?
"Para evitar datos incorrectos y comportamientos inesperados."

¿Por qué revisar el código de IA?
"Porque puede contener errores o no coincidir con el UML. Debe probarse,
analizarse y adaptarse."

IA
--

La guía permite utilizar IA como apoyo, pero exige comprender, analizar y
validar el código.

En la defensa:
"Utilicé IA como apoyo preliminar. Probé el código, lo comparé con el UML
y realicé modificaciones para cumplir los requerimientos."

Debes saber explicar qué generó la IA, qué modificaste y por qué.

CHECKLIST
---------

[ ] UML coincide con Python.
[ ] Clases, atributos, __init__ y métodos completos.
[ ] Relaciones implementadas.
[ ] Encapsulamiento aplicado.
[ ] MySQL conectado.
[ ] CRUD funcionando.
[ ] Validaciones funcionando.
[ ] try-except funcionando.
[ ] Probé errores.
[ ] Revisé y adapté el código de IA.
[ ] Puedo explicar el código y mis decisiones.

REGLA PARA RECORDAR
-------------------

UML → CLASES → POO → MYSQL → CRUD → VALIDACIONES → PRUEBAS → IA → DEFENSA


=== UNIDAD 3: LOGIN, HASH, ROLES Y PERMISOS ===

1. Instale las dependencias desde la carpeta raíz:
   python -m pip install -r requirements.txt
2. Copie .env.example a .env y configure DB_BACKEND=mysql o DB_BACKEND=sqlite.
3. Ejecute desde DOC_2:
   python main.py
4. El programa crea/migra las tablas y carga la semilla de datos sin duplicarla.
5. Si no existe cuenta para el primer empleado de semilla, el programa crea la
   cuenta admin_ecotech y solicita definir una contraseña oculta. Debe tener al
   menos 10 caracteres, incluir letras y números y no superar 72 bytes UTF-8.
6. El login utiliza nombre de usuario y getpass oculta la contraseña. bcrypt guarda
   password_hash, nunca la contraseña original.
7. El administrador puede crear cuentas de empleado desde su menú. El formulario no
   permite escoger el rol: las cuentas habituales siempre se crean como empleado.
8. El empleado solo puede consultar su ficha, revisar sus registros laborales y
   modificar su propio nombre y correo. El ID se obtiene de la sesión, no del teclado.
9. El menú administrativo solo se muestra al rol admin. Además, los servicios vuelven
   a comprobar la sesión/rol antes de consultar o modificar datos.
10. Cerrar sesión vuelve a la pantalla de login. Repetir la semilla no cambia roles
    ni eleva cuentas existentes.
11. La opción API consulta el dólar observado en mindicador.cl. Requiere internet.

Nota: mantenga .env fuera del repositorio y no comparta sus credenciales de MySQL.

El modelo con la entidad Usuario y la relación 1 a 0..1 con Empleado se encuentra en:
   diagrama uml actualizado roles.svg
   diagrama uml del proyecto actualizado.puml (fuente PlantUML editable)
El diagrama SVG original del proyecto se conserva sin cambios.


USAR MYSQL O SQLITE EN ECOTECH SOLUTIONS
----------------------------------------
El programa utiliza UN solo motor de base de datos por ejecución. Selecciónelo en el archivo .env mediante DB_BACKEND.

Para MySQL (modo predeterminado):
    DB_BACKEND=mysql
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=root
    DB_PASSWORD=tu_clave
    DB_NAME=ecotech_db

Para SQLite (base local en un archivo):
    DB_BACKEND=sqlite
    SQLITE_PATH=ecotech.db

Al cambiar de motor, detenga el programa y cambie DB_BACKEND en .env. MySQL y SQLite son bases separadas: los datos guardados en una no se copian automáticamente a la otra. SQLite no requiere servidor ni usuario/contraseña. El archivo ecotech.db se crea automáticamente en la raíz del proyecto.

Instale las dependencias desde la raíz del proyecto en PowerShell: 
    python -m pip install -r requirements.txt

Después ejecute desde la carpeta DOC_2 con `python main.py`. El esquema y la semilla se preparan automáticamente para el motor seleccionado.


INTEGRACION API MINDICADOR Y SEGURIDAD (REVISION ACTUAL)
--------------------------------------------------------
La consulta del dolar esta centralizada en:
DOC_2/src/servicios/api_dolar.py

Flujo:
1. La interfaz invoca consultar_dolar(self.usuario).
2. exigir_sesion valida la sesion antes de acceder a la red.
3. requests.get consulta una URL HTTPS fija, con timeout.
4. raise_for_status comprueba el codigo HTTP.
5. response.json interpreta el JSON.
6. deserializar_indicador valida estructura, codigo, serie, valor y fecha.
7. Se devuelve un objeto IndicadorDolar para mostrarlo en el menu.

Errores controlados:
- timeout y conectividad;
- errores HTTP;
- otros errores de requests;
- JSON invalido y datos incompletos o inesperados.

No se solicita al usuario una URL ni se construye la URL con texto ingresado.
Las credenciales de BD deben estar en .env (no subir .env al repositorio).
Las contrasenas de usuarios se almacenan como hashes bcrypt, no como texto plano.

EVIDENCIA Y REVISION DE IA
--------------------------
Consultar DOCUMENTACION_REVISION_IA.md. El estudiante debe completar el
registro con las consultas reales realizadas y marcar solo las pruebas que
haya ejecutado. No declarar pruebas no realizadas.


PRUEBAS AUTOMATIZADAS DE API
----------------------------
Desde la raiz del proyecto, con el entorno virtual activo:

python -m unittest discover -s DOC_2/tests -v

Las pruebas validan extraccion JSON, rechazo de datos invalidos, sesion,
timeout y uso de timeout HTTP. No sustituyen una prueba real con Internet.
