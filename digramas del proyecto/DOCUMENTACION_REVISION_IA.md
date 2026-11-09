# Evidencia de uso y revisión crítica de herramientas de IA

## 1. Propósito

Este documento registra el apoyo de una herramienta de IA durante la revisión y refactorización de EcoTech Solutions. Debe completarse con los datos reales de la persona que desarrolló el proyecto (herramienta, fecha, consultas y pruebas ejecutadas). No debe presentarse como evidencia de acciones que no se realizaron.

## 2. Uso de IA en esta revisión

La IA se utilizó como apoyo para:
- revisar la separación entre interfaz, servicios, dominio y persistencia;
- detectar que la consulta HTTP de prueba estaba separada del flujo autenticado de la aplicación;
- proponer una capa de servicio para encapsular la solicitud HTTP, el análisis JSON y el control de errores;
- revisar validaciones de datos externos y controles de sesión;
- redactar una guía para explicar las decisiones técnicas.

**Herramienta utilizada:** completar con el nombre y versión que efectivamente se utilizó.  
**Fecha de revisión:** completar con la fecha real.  
**Responsable de revisión y validación:** completar con el nombre del estudiante.

## 3. Hallazgos técnicos identificados en la versión revisada

| Hallazgo | Riesgo o consecuencia | Decisión adoptada |
|---|---|---|
| La prueba HTTP estaba en `prueba_api.py`, separada del servicio de aplicación. | La prueba por sí sola no demostraba integración con los menús ni con una sesión real. | Se creó `servicios/api_dolar.py` y el menú llama al servicio después de comprobar la sesión. |
| La URL y la lógica HTTP estaban concentradas en una prueba independiente. | Dificultaba reutilizar la consulta y probarla de forma centralizada. | Se centralizó la URL fija, el timeout, los encabezados y el procesamiento en el servicio. |
| La respuesta JSON se leía sin una entidad de salida común. | La interfaz podía depender directamente de claves del proveedor. | Se agregó `IndicadorDolar` y una función deserializadora que valida y extrae los campos requeridos. |
| El control de errores de red estaba limitado al script de prueba. | Una falla podía propagarse sin un mensaje útil al flujo principal. | El servicio traduce timeout, conexión, HTTP y errores de solicitud a mensajes controlados. |
| La ruta de `.env` dependía del directorio desde el que se iniciara Python. | Podía cargar una configuración distinta o no encontrarla. | Se resolvió la ruta desde la ubicación del módulo de conexión y la raíz del repositorio. |
| La plantilla no reflejaba el puerto y nombre de base de datos acordados para el entorno de desarrollo. | Podía conectarse a otra instancia o base. | `.env.example` propone puerto 3307 y base `ecotech_solutions_nueva`; deben ajustarse al servidor instalado. |

## 4. Explicación técnica de la refactorización

### 4.1 Solicitud HTTP

`servicios/api_dolar.py` utiliza `requests.get()` contra un endpoint constante de Mindicador. No acepta URLs escritas por el usuario. Define un timeout de conexión y lectura, solicita JSON mediante el encabezado `Accept` y llama a `raise_for_status()` para detectar respuestas HTTP no exitosas.

### 4.2 Procesamiento JSON

La función `deserializar_indicador()` verifica que la respuesta sea un diccionario, que el código sea `dolar`, que `serie` sea una lista no vacía y que el primer elemento tenga un valor numérico positivo y finito y una fecha parseable. Luego construye un objeto inmutable `IndicadorDolar`.

### 4.3 Integración y sesión

La función `consultar_dolar(sesion)` llama primero a `exigir_sesion()`. Solo después realiza la solicitud. La interfaz de terminal invoca esta función desde las opciones de administrador y empleado, de modo que el consumo queda dentro del flujo autenticado.

### 4.4 Manejo de errores

Se distinguen timeout, error de conexión, error HTTP, otros errores de red y respuesta JSON/datos inválidos. Los mensajes no incluyen contraseñas, tokens ni contenido sensible de la configuración.

### 4.5 Credenciales y datos sensibles

Las contraseñas de usuarios se procesan con bcrypt y se verifica el hash con `checkpw`; bcrypt es hash unidireccional, no cifrado reversible. La contraseña de la base de datos se configura en `.env`, que se excluye de Git mediante `.gitignore`. No se deben guardar credenciales reales en el repositorio ni imprimirlas en consola.

## 5. Límites y riesgos que siguen requiriendo atención

- La conexión HTTP utiliza HTTPS, pero la verificación de la API depende de la disponibilidad y certificado del proveedor.
- La consulta actual no implementa caché ni historial persistente de cotizaciones en esta rama del proyecto.
- La API no recibe parámetros libres desde el usuario; por diseño, la URL es fija. Si en el futuro se agregan filtros, deben validarse con listas permitidas y nunca concatenarse a una URL arbitraria.
- El manejo de excepciones evita mostrar secretos, pero el equipo debe revisar los registros de errores para no incorporar datos personales.
- La protección del archivo `.env` depende también de permisos adecuados del sistema operativo y de no compartirlo.
- La sesión actual es un diccionario de aplicación en memoria; no es una sesión firmada ni un mecanismo para un sistema distribuido.

## 6. Pruebas que debe ejecutar y registrar el estudiante

Marcar solo después de ejecutar cada prueba en el equipo:

- [ ] Consulta exitosa a Mindicador con conexión a Internet.
- [ ] Prueba con conexión a Internet desactivada: se muestra mensaje controlado.
- [ ] Prueba de timeout/error de red (puede simularse mediante pruebas automatizadas).
- [ ] Prueba con respuesta HTTP no exitosa simulada.
- [ ] Prueba con JSON mal formado simulado.
- [ ] Prueba con `serie` vacía o con valor no numérico simulado.
- [ ] Llamada a `consultar_dolar(None)`: debe rechazarse por falta de sesión.
- [ ] Consulta desde una sesión de empleado válida.
- [ ] Consulta desde una sesión de administrador válida.
- [ ] Verificación de que `.env` no está incluido en el ZIP/repo compartido.

## 7. Registro de prompts y análisis del estudiante

Completar con las consultas reales que se hicieron a la herramienta de IA. Para cada una, explicar qué sugerencia se aceptó, qué se descartó y cómo se verificó.

| Consulta real a la IA | Sugerencia recibida | Decisión del estudiante y justificación | Prueba realizada |
|---|---|---|---|
| Completar | Completar | Completar | Completar |
| Completar | Completar | Completar | Completar |

## 8. Conclusión para la defensa

La IA se utilizó como herramienta de apoyo y no como sustituto de la revisión. El estudiante debe poder explicar el flujo `requests.get()` → comprobación HTTP → JSON → validación y extracción → objeto `IndicadorDolar` → presentación en el menú autenticado. También debe explicar por qué la URL es fija, por qué se utiliza timeout, cómo se gestionan los errores y por qué bcrypt almacena hashes en vez de contraseñas recuperables.

**Importante:** esta documentación describe los cambios incluidos en esta versión. El estudiante debe completar los datos de uso real de IA y marcar únicamente las pruebas que haya ejecutado personalmente.
