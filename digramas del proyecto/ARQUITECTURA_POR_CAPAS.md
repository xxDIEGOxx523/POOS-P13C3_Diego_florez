# Arquitectura por capas de EcoTech Solutions

```text
Presentación / UX
  src/ux/interfaz.py
  src/ux/menu_usuario.py
          | llama casos de uso y entrega la sesión
          v
Servicios / Aplicación
  src/servicios/autenticacion.py
  src/servicios/permisos.py
  src/servicios/mi_cuenta.py
  src/servicios/gestion_empleados.py
  src/servicios/gestion_departamentos.py
  src/servicios/gestion_proyectos.py
  src/servicios/gestion_tiempos.py
  src/servicios/api_dolar.py
  src/servicios/deserializador_indicador.py
  src/servicios/indicadores.py
          | aplica reglas y coordina operaciones
          v
Dominio
  src/dominio/empleado.py
  src/dominio/usuario.py
  src/dominio/departamento.py
  src/dominio/proyecto.py
  src/dominio/registrotiempo.py
  src/dominio/indicador.py
          | entidades y validaciones, sin SQL ni HTTP
          v
Persistencia / DAO
  src/persistencia/conexion.py
  src/persistencia/crear_db.py
  src/persistencia/*_dao.py
          | SQL parametrizado, commit/rollback y cierre
          v
MySQL o SQLite (un motor por ejecución)
```

## Seguridad de acceso

- `exigir_sesion()` protege las consultas que requieren autenticación.
- `exigir_admin()` protege la administración y se ejecuta en los servicios antes de llamar al DAO.
- El rol se recupera desde la cuenta validada, no desde lo que escriba el usuario en el menú.
- El empleado se obtiene desde `sesion["empleado_id"]`; nunca se usa un ID arbitrario para consultar su propia información o registrar horas.
- `mi_cuenta.registrar_horas()` confirma que el proyecto está asociado al empleado en `empleado_proyecto`.
- Los dos roles pueden consultar el dólar y su historial local, siempre con una sesión válida.

## Flujo de indicadores (Clase 6)

1. UX llama a `servicios.indicadores.consultar_indicador(sesion, dao)`.
2. El servicio ejecuta `exigir_sesion()` y llama al cliente HTTP `api_dolar.obtener_datos()`.
3. `DeserializadorIndicador` usa `extraer_primero()` y crea `dominio.Indicador`.
4. `IndicadorDAO.guardar()` hace insert/update por la clave única `(fuente, codigo, fecha)`.
5. Ante una falla HTTP o una respuesta inválida, el servicio consulta `buscar_ultimo()` y lo identifica como `BD local`.
6. `obtener_historial()` exige sesión y solo consulta la BD; no ejecuta una solicitud HTTP.
