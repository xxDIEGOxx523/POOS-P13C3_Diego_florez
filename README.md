# EcoTech Solutions

**Sistema de gestión de empleados, departamentos, proyectos y registros de tiempo**  
**Proyecto académico:** Programación Orientada a Objetos Seguro (POOS)  
**Tecnologías principales:** Python, MySQL/MariaDB o SQLite, bcrypt, requests y Mindicador.

---

## 1. Descripción del proyecto

EcoTech Solutions es una aplicación de gestión interna pensada para una empresa que necesita organizar la información de sus trabajadores y el trabajo que realizan en distintos proyectos.

La solución permite administrar empleados, departamentos, proyectos, asignaciones de trabajadores y registros de horas. Además, incorpora inicio de sesión con roles de usuario y una consulta externa del dólar observado mediante una API.

La aplicación está desarrollada en Python y utiliza programación orientada a objetos. Su persistencia se puede ejecutar con **MySQL/MariaDB** o con **SQLite**, seleccionando un solo motor por ejecución.

## 2. Caso o problema que aborda

Cuando una organización administra sus recursos humanos y proyectos mediante archivos separados, planillas o registros manuales, la información puede quedar dispersa. Esto dificulta responder preguntas operativas como:

- ¿Qué personas pertenecen a cada departamento?
- ¿Qué empleados están asignados a un proyecto?
- ¿Qué actividades se están registrando y cuántas horas se han trabajado?
- ¿Qué información puede consultar o modificar cada trabajador?
- ¿Cómo se puede consultar un indicador económico externo sin salir del sistema?

La falta de centralización puede provocar datos duplicados, registros desactualizados, errores al ingresar información y dificultades para controlar quién tiene acceso a datos internos.

## 3. Solución propuesta

EcoTech Solutions reúne las funciones principales en una aplicación de terminal conectada a una base de datos. La solución aborda el problema mediante cinco elementos:

1. **Centralización de datos:** organiza empleados, departamentos, proyectos, asignaciones y registros de tiempo en tablas relacionadas.
2. **Gestión mediante operaciones CRUD:** permite registrar, consultar, actualizar y eliminar información en las áreas habilitadas para administración.
3. **Separación por responsabilidades:** divide el dominio, la persistencia, los servicios y la interfaz para facilitar el mantenimiento del código.
4. **Control de acceso:** incorpora autenticación, contraseñas almacenadas como hashes bcrypt y permisos diferenciados para `admin` y `empleado`.
5. **Información externa:** consulta el dólar observado desde Mindicador, procesa la respuesta JSON y valida los datos antes de mostrarlos.

### 3.1. Flujo de trabajo recomendado

Un uso habitual del sistema puede seguir este orden:

1. Registrar los departamentos de la organización.
2. Registrar a los empleados y asociarlos a un departamento.
3. Registrar los proyectos que se deben gestionar.
4. Asignar empleados a los proyectos correspondientes.
5. Registrar las horas trabajadas y describir la actividad realizada.
6. Consultar los registros para revisar la información laboral disponible.
7. Utilizar las cuentas de empleado para que cada trabajador consulte sus propios datos.

Este flujo reduce la necesidad de mantener registros independientes y permite relacionar personas, departamentos, proyectos y tiempo trabajado.

## 4. Funcionalidades implementadas

### 4.1. Administración (rol `admin`)

- Registrar y listar empleados.
- Registrar y listar departamentos.
- Registrar y listar proyectos.
- Registrar horas trabajadas.
- Consultar registros laborales del sistema.
- Actualizar y eliminar empleados.
- Cargar datos ficticios de demostración.
- Consultar el dólar observado mediante la API.
- Cambiar la contraseña.
- Registrar cuentas para empleados.

### 4.2. Cuenta de empleado (rol `empleado`)

- Consultar su propia ficha.
- Consultar sus propios registros laborales.
- Modificar su nombre y correo.
- Consultar el dólar observado.
- Cambiar su contraseña.

Los servicios verifican la sesión y los permisos antes de realizar operaciones protegidas. La interfaz no es la única barrera de seguridad.

### 4.3. Autenticación y contraseñas

Las contraseñas se procesan con **bcrypt**. El sistema almacena un hash y verifica la contraseña durante el inicio de sesión; no guarda la contraseña original en texto plano.

Las reglas actuales para crear una contraseña son:

- Al menos 10 caracteres.
- Debe contener letras y números.
- No debe superar el límite de 72 bytes UTF-8 admitido por bcrypt.

La entrada de la contraseña se oculta en la terminal. Los roles disponibles son `admin` y `empleado`.

### 4.4. Consulta del dólar observado

La aplicación consulta el endpoint:

```text
https://mindicador.cl/api/dolar
```

El servicio utiliza `requests`, define un tiempo máximo de espera, comprueba el estado HTTP y valida el contenido JSON. Comprueba, entre otros aspectos, que el indicador corresponda al dólar y que el valor recibido sea numérico, positivo y finito.

La consulta requiere una sesión autenticada. El resultado muestra el nombre del indicador, valor, unidad, fecha informada por la API y fuente.

### 4.5. Datos de demostración

Al iniciar el sistema se ejecuta una semilla idempotente que completa los datos de demostración que falten. La semilla reconoce sus registros para no duplicarlos y no elimina información ajena a ella.

En una instalación vacía, la semilla prepara 10 departamentos, 10 empleados, 10 proyectos, 10 asignaciones empleado-proyecto y 10 registros de tiempo. Las cuentas de usuario no se crean en masa: durante la primera preparación se solicita definir la contraseña para la cuenta inicial `admin_ecotech`, vinculada al primer empleado de demostración, si todavía no existe una cuenta para ese empleado.

## 5. ¿Por qué EcoTech Solutions es una opción viable?

EcoTech Solutions es una alternativa viable para el **alcance de gestión interna y demostración académica** porque ofrece una solución concreta sin exigir una infraestructura compleja:

- **Costo de entrada bajo:** puede ejecutarse localmente y usar SQLite sin instalar un servidor de base de datos.
- **Opción de crecimiento:** puede utilizar MySQL/MariaDB cuando se necesita un servidor de base de datos compartido.
- **Mantenimiento más ordenado:** las clases de dominio, los DAO, los servicios y la interfaz están separados, por lo que un cambio en una capa no obliga necesariamente a reescribir todo el programa.
- **Acceso diferenciado:** los roles limitan las operaciones disponibles para administradores y empleados.
- **Protección básica de credenciales:** utiliza bcrypt y solicita las contraseñas sin mostrarlas en la terminal.
- **Validación y manejo de errores:** valida datos de entrada y controla errores esperables de la conexión y del consumo HTTP.
- **Datos de prueba reproducibles:** la semilla permite probar las funciones con información ficticia sin volver a insertar los mismos registros en cada ejecución.

Por estas razones, el proyecto es adecuado como prototipo funcional para organizar las operaciones descritas y como base para futuras mejoras. La viabilidad no significa que ya sea un sistema empresarial completo: antes de usarlo en producción sería necesario implementar y probar aspectos como respaldos automáticos, despliegue seguro, monitoreo, administración avanzada de cuentas, auditoría de cambios y controles adicionales de operación.

## 6. Alcance actual y mejoras futuras

Para presentar el proyecto correctamente, es importante distinguir las funciones implementadas de las que todavía podrían desarrollarse.

| Área | Estado en esta versión |
|---|---|
| Gestión de empleados y departamentos | Implementada. |
| Gestión de proyectos y asignaciones | Implementada. |
| Registro y consulta de tiempo trabajado | Implementada. |
| Inicio de sesión y roles | Implementados. |
| Hash de contraseñas con bcrypt | Implementado. |
| Selección entre MySQL/MariaDB y SQLite | Implementada. |
| Consulta y validación del dólar observado | Implementada. |
| Historial persistente de respuestas de la API | No implementado. |
| Integración de una API climática | No implementada. |
| Conversión automática de remuneraciones y actualización de pagos | No integrada al flujo de la aplicación. |
| Interfaz web, despliegue en la nube y reportes visuales | Fuera del alcance actual. |

## 7. Estructura del proyecto

La estructura se conserva con el código dentro de `DOC_2/src`:

```text
POOS-P13C3_Diego_florez-main/
│
├── .env.example
├── .gitignore
├── README.md
├── DOCUMENTACION_REVISION_IA.md
├── requirements.txt
├── ecotech_mysql.sql
├── diagramas UML
│
└── DOC_2/
    ├── src/
    │   ├── main.py
    │   ├── semilla.py
    │   ├── prueba_api.py
    │   ├── probar_interfaz_sin_db.py
    │   ├── dominio/
    │   ├── persistencia/
    │   ├── servicios/
    │   └── ux/
    │
    └── tests/
        └── test_api_dolar.py
```

### Responsabilidad de las capas

| Carpeta o archivo | Responsabilidad |
|---|---|
| `DOC_2/src/main.py` | Punto de entrada: prepara la base de datos, carga la semilla y presenta el inicio de sesión. |
| `dominio/` | Clases y validaciones de entidades como empleado, usuario, departamento, proyecto y registro de tiempo. |
| `persistencia/` | Conexión a la base de datos, creación del esquema y operaciones de acceso a datos mediante DAO. |
| `servicios/` | Autenticación, permisos, gestión de empleados y consumo de la API. |
| `ux/` | Menús e interacción con el usuario desde la terminal. |
| `DOC_2/src/semilla.py` | Inserción controlada de datos ficticios. |
| `DOC_2/tests/` | Pruebas unitarias del servicio de consulta del dólar. |
| `.env.example` | Plantilla de configuración para seleccionar el motor y definir la conexión. |

## 8. Requisitos previos

- Windows 10 u 11.
- Python instalado y disponible desde Git Bash o PowerShell.
- Git Bash o terminal integrada de Visual Studio Code.
- Para MySQL/MariaDB: un servidor MySQL o MariaDB instalado y en ejecución.
- Para SQLite: no se necesita instalar un servidor; la base de datos se guarda en un archivo local.
- Conexión a Internet para consultar Mindicador.

Las dependencias de Python están en `requirements.txt`:

- `mysql-connector-python`: conexión con MySQL/MariaDB.
- `python-dotenv`: lectura de variables de entorno.
- `requests`: solicitudes HTTP.
- `bcrypt`: hash y verificación de contraseñas.

## 9. Preparación común en Git Bash

Realiza estos pasos desde la carpeta raíz del proyecto, donde están `requirements.txt` y `.env.example`.

### Paso 1. Abrir la carpeta del proyecto

Descomprime el proyecto y abre esa carpeta en Visual Studio Code. Luego abre **Terminal → Nuevo terminal** y selecciona Git Bash si no está seleccionado.

Comprueba que estás en la raíz:

```bash
pwd
ls
```

Debes poder ver, entre otros elementos, `DOC_2`, `requirements.txt` y `.env.example`.

### Paso 2. Crear un entorno virtual

```bash
python -m venv .venv
```

### Paso 3. Activarlo

```bash
source .venv/Scripts/activate
```

Cuando esté activo, normalmente verás `(.venv)` al comienzo de la línea de la terminal.

### Paso 4. Instalar las dependencias

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Paso 5. Crear el archivo `.env`

```bash
cp .env.example .env
```

Abre `.env` para editar sus valores:

```bash
notepad .env
```

No reemplaces un `.env` que ya contenga tu configuración. El archivo `.env` guarda datos locales de conexión y está excluido del repositorio mediante `.gitignore`. **No publiques contraseñas ni subas el archivo `.env` a GitHub.**

---

## 10. Cómo levantar el proyecto con MySQL o MariaDB

### Paso 1. Iniciar el servidor

Inicia el servicio MySQL o MariaDB que tengas instalado. Puede ser MySQL Server, MariaDB o el servicio correspondiente de WampServer.

Comprueba el puerto configurado. En la plantilla del proyecto se utiliza `3307`, pero algunas instalaciones usan `3306`.

En Git Bash puedes probar el puerto con:

```bash
powershell.exe -Command "Test-NetConnection localhost -Port 3307"
```

Busca `TcpTestSucceeded : True`. Si tu servidor utiliza `3306`, cambia el número del comando y el valor `DB_PORT` del archivo `.env`.

### Paso 2. Configurar `.env`

Asegúrate de que la configuración sea similar a esta y reemplaza usuario, contraseña, puerto o nombre de base de datos según tu instalación:

```dotenv
DB_BACKEND=mysql
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=TU_CLAVE_DE_MYSQL
DB_NAME=ecotech_solutions_nueva

SQLITE_PATH=ecotech.db
```

- `DB_BACKEND=mysql` selecciona MySQL/MariaDB.
- `DB_HOST` indica el servidor.
- `DB_PORT` debe coincidir con el puerto real del servicio.
- `DB_USER` y `DB_PASSWORD` son las credenciales de la base de datos.
- `DB_NAME` indica el nombre de la base que utilizará el sistema.

El usuario de base de datos necesita permisos para crear la base de datos y las tablas. El programa crea la base de datos indicada en `DB_NAME` si todavía no existe y luego prepara las tablas.

### Paso 3. Ejecutar la aplicación

Desde la raíz del proyecto:

```bash
python DOC_2/src/main.py
```

No es necesario ejecutar manualmente `ecotech_mysql.sql` para el inicio habitual: `main.py` prepara el esquema según el motor seleccionado. El archivo SQL se conserva como referencia de estructura MySQL. Si decides importarlo manualmente, recuerda que crea la base `ecotech_db`; debes hacer coincidir `DB_NAME` con ese nombre para evitar que el programa utilice otra base distinta.

### Paso 4. Crear la primera cuenta de administrador

En una base nueva, la aplicación carga los datos de demostración. Si todavía no existe una cuenta para el primer empleado de la semilla, solicitará definir y confirmar una contraseña para el usuario:

```text
admin_ecotech
```

La contraseña debe tener al menos 10 caracteres, incluir letras y números y respetar el límite de 72 bytes de bcrypt. La contraseña se escribe de forma oculta.

Después, inicia sesión con `admin_ecotech` y la contraseña que definiste. Si ya existe una cuenta vinculada a ese empleado, el programa no reemplaza su contraseña ni cambia automáticamente su rol.

---

## 11. Cómo levantar el proyecto con SQLite

SQLite permite ejecutar el proyecto sin iniciar ni instalar un servidor MySQL. La información se guarda en un archivo local.

### Paso 1. Cambiar el motor en `.env`

Abre el archivo:

```bash
notepad .env
```

Configura lo siguiente:

```dotenv
DB_BACKEND=sqlite

# Estos valores solo se usan con MySQL; SQLite los ignora.
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=
DB_NAME=ecotech_solutions_nueva

# Archivo local de la base SQLite
SQLITE_PATH=ecotech.db
```

Puedes cambiar `ecotech.db` por otra ruta o nombre. Si la ruta es relativa, el archivo se crea en la raíz del proyecto.

### Paso 2. Ejecutar la aplicación

Desde la raíz del proyecto:

```bash
python DOC_2/src/main.py
```

El programa crea automáticamente el archivo SQLite, prepara las tablas, carga los datos de demostración que falten y solicita definir la cuenta inicial de administrador cuando corresponda.

**No necesitas iniciar WampServer, MySQL Workbench ni otro servicio de base de datos para utilizar SQLite.**

### Paso 3. Volver a MySQL cuando lo necesites

Cambia únicamente:

```dotenv
DB_BACKEND=mysql
```

Y revisa que `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` y `DB_NAME` correspondan a tu servidor. No utilices ambos motores simultáneamente: cada ejecución utiliza el motor indicado en `.env`.

---

## 12. Pruebas y herramientas de comprobación

### Ejecutar las pruebas unitarias

Desde la raíz del proyecto, con el entorno virtual activado y Git Bash:

```bash
PYTHONPATH=DOC_2/src python -m unittest discover -s DOC_2/tests -v
```

Las pruebas incluidas verifican la extracción y validación del JSON, el rechazo de respuestas incompletas o inválidas, la exigencia de sesión, el uso de timeout y el manejo de un error de tiempo de espera.

Las pruebas de API utilizan respuestas HTTP simuladas. Para comprobar el servicio externo real también puedes ejecutar:

```bash
PYTHONPATH=DOC_2/src python DOC_2/src/prueba_api.py
```

Este último comando requiere conexión a Internet. No reemplaza la prueba completa de la aplicación con una sesión y una base de datos reales.

### Probar la interfaz sin conectarse a una base real

El proyecto incluye un módulo de prueba de interfaz:

```bash
python DOC_2/src/probar_interfaz_sin_db.py
```

Este archivo usa objetos DAO de prueba para revisar la interacción sin depender de una instalación real de MySQL.

---

## 13. Problemas frecuentes

| Problema | Qué revisar |
|---|---|
| `python` no se reconoce | Instala Python o selecciona el intérprete correcto en Visual Studio Code. Cierra y vuelve a abrir la terminal después de instalarlo. |
| No se encuentra un módulo como `bcrypt` o `requests` | Activa `.venv` y ejecuta `python -m pip install -r requirements.txt`. |
| Error de conexión MySQL/MariaDB | Confirma que el servicio esté iniciado y que host, puerto, usuario y contraseña coincidan con `.env`. |
| Puerto `3307` no disponible | Revisa si tu servidor utiliza `3306` u otro puerto y actualiza `DB_PORT`. |
| La aplicación usa otra base de datos | Comprueba `DB_BACKEND` y `DB_NAME` en `.env`. El SQL de referencia crea `ecotech_db`, mientras que la plantilla utiliza `ecotech_solutions_nueva`. |
| Error al consultar Mindicador | Comprueba Internet. El servicio externo puede no responder o entregar un error HTTP; la aplicación informa el problema sin asumir que la respuesta es válida. |
| No puedes iniciar sesión | Verifica el nombre de usuario, la contraseña definida durante la creación inicial y que la cuenta esté activa. |
| Se vuelve a cargar la semilla | La semilla identifica los registros propios y evita duplicarlos; no elimina datos ajenos a ella. |

---

## 14. Seguridad y uso responsable

- Mantén las credenciales reales dentro de `.env` y no las publiques.
- No subas archivos de base de datos con información real a repositorios públicos.
- Utiliza contraseñas diferentes a las que ocupas en otros servicios.
- No concedas permisos de administrador a todas las cuentas.
- Para un uso real, crea un usuario específico de MySQL/MariaDB con los permisos mínimos necesarios en lugar de utilizar una cuenta administrativa global.
- Mantén copias de seguridad de los datos importantes.

## 15. Conclusión

EcoTech Solutions ofrece una base funcional para centralizar la gestión de empleados, departamentos, proyectos y tiempo trabajado. La combinación de programación orientada a objetos, DAO, autenticación con bcrypt, control por roles, validación de entradas y selección entre MySQL/MariaDB y SQLite permite explicar tanto la solución del problema como las decisiones técnicas que la sostienen.

Su principal ventaja es que puede comenzar a utilizarse en un entorno local de bajo costo y mantener una estructura que facilita futuras ampliaciones. Dentro de su alcance actual, es una opción viable como prototipo de gestión interna y como proyecto académico demostrable, siempre considerando las mejoras pendientes antes de un despliegue productivo.
