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
