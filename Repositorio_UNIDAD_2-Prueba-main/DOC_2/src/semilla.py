"""Carga datos ficticios de demostracion para EcoTech Solutions.

Funciona tanto con los DAO reales (MySQL) como con los DAO falsos de la prueba
sin base de datos. Es idempotente: identifica los registros de semilla y no los
duplica si se vuelve a ejecutar.
"""
from datetime import date

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registrotiempo import RegistroTiempo


NOMBRES_DEPARTAMENTO = [
    "Finanzas", "Contabilidad", "Tecnologia", "Recursos Humanos",
    "Logistica", "Operaciones", "Ventas", "Marketing", "Soporte",
    "Administracion",
]

NOMBRES_PERSONA = [
    "Alex Rojas", "Camila Soto", "Matias Perez", "Valentina Diaz",
    "Benjamin Torres", "Isidora Fuentes", "Joaquin Morales", "Martina Silva",
    "Gabriel Contreras", "Antonia Reyes",
]

DIRECCIONES = [
    "Av. Los Pinos 101", "Calle Norte 202", "Pasaje Central 303",
    "Av. del Trabajo 404", "Calle Los Aromos 505", "Pasaje Sur 606",
    "Av. Industrial 707", "Calle Oriente 808", "Pasaje Nuevo 909",
    "Av. Costanera 1010",
]

NOMBRES_PROYECTO = [
    "Control de inventario", "Portal interno", "Automatizacion de reportes",
    "Plan de mantenimiento", "Gestion de clientes", "Dashboard financiero",
    "Renovacion de equipos", "Auditoria de procesos", "Optimizacion logistica",
    "Mejora de seguridad",
]

DESCRIPCIONES_PROYECTO = [
    "Proyecto de demostracion para organizar inventario.",
    "Proyecto de demostracion para centralizar informacion interna.",
    "Proyecto de demostracion para generar reportes.",
    "Proyecto de demostracion para programar mantenimiento.",
    "Proyecto de demostracion para gestionar clientes.",
    "Proyecto de demostracion de indicadores financieros.",
    "Proyecto de demostracion para renovar equipos.",
    "Proyecto de demostracion para revisar procesos.",
    "Proyecto de demostracion para mejorar rutas y entregas.",
    "Proyecto de demostracion para mejorar controles de seguridad.",
]


def _indice_por_clave(filas, clave):
    return {fila.get(clave): fila for fila in filas}


def cargar_semilla(registro_dao, empleado_dao, proyecto_dao, departamento_dao):
    """Asegura 10 registros de semilla en cada una de las cinco tablas.

    No elimina ni sobrescribe registros ajenos a la semilla. Devuelve un resumen
    con cuántos registros se agregaron y cuántos ya existían.
    """
    resumen = {
        "departamento": {"creados": 0, "existentes": 0},
        "empleado": {"creados": 0, "existentes": 0},
        "proyecto": {"creados": 0, "existentes": 0},
        "empleado_proyecto": {"creados": 0, "existentes": 0},
        "registro_tiempo": {"creados": 0, "existentes": 0},
    }

    # 1. Departamentos. Se crean primero sin gerente para evitar el ciclo FK.
    departamentos = _indice_por_clave(departamento_dao.obtener_todos(), "nombre")
    ids_departamento = {}
    for i, nombre_base in enumerate(NOMBRES_DEPARTAMENTO, start=1):
        nombre = f"SEMILLA - {nombre_base} {i:02d}"
        existente = departamentos.get(nombre)
        if existente:
            ids_departamento[i] = existente["id_departamento"]
            resumen["departamento"]["existentes"] += 1
        else:
            objeto = Departamento(nombre)
            departamento_dao.insertar(objeto)
            ids_departamento[i] = objeto.id_departamento
            resumen["departamento"]["creados"] += 1
            departamentos[nombre] = {
                "id_departamento": objeto.id_departamento,
                "nombre": nombre,
                "id_gerente": None,
            }

    # 2. Empleados. El correo funciona como clave estable para reconocerlos.
    empleados = _indice_por_clave(empleado_dao.obtener_todos(), "correo")
    ids_empleado = {}
    for i, nombre in enumerate(NOMBRES_PERSONA, start=1):
        correo = f"semilla.empleado{i:02d}@example.com"
        existente = empleados.get(correo)
        if existente:
            ids_empleado[i] = existente["id_empleado"]
            resumen["empleado"]["existentes"] += 1
        else:
            empleado = Empleado(
                nombre=nombre,
                direccion=DIRECCIONES[i - 1],
                telefono=f"+5697000{i:04d}",
                correo=correo,
                fecha_inicio_contrato=date(2025, (i - 1) % 12 + 1, min(i, 28)),
                salario=850000 + i * 45000,
                id_departamento=ids_departamento[i],
            )
            empleado_dao.insertar(empleado)
            ids_empleado[i] = empleado.id_empleado
            resumen["empleado"]["creados"] += 1
            empleados[correo] = {
                "id_empleado": empleado.id_empleado,
                "nombre": empleado.nombre,
                "correo": correo,
                "id_departamento": ids_departamento[i],
            }

    # 3. Asignar un gerente ficticio a cada departamento.
    # Los DAO reales y falsos exponen el mismo metodo.
    for i in range(1, 11):
        departamento_dao.asignar_gerente(ids_departamento[i], ids_empleado[i])

    # 4. Proyectos. El nombre de semilla los hace reconocibles y reutilizables.
    proyectos = _indice_por_clave(proyecto_dao.obtener_todos(), "nombre")
    ids_proyecto = {}
    for i, nombre_base in enumerate(NOMBRES_PROYECTO, start=1):
        nombre = f"SEMILLA - {nombre_base} {i:02d}"
        existente = proyectos.get(nombre)
        if existente:
            ids_proyecto[i] = existente["id_proyecto"]
            resumen["proyecto"]["existentes"] += 1
        else:
            proyecto = Proyecto(
                nombre=nombre,
                descripcion=DESCRIPCIONES_PROYECTO[i - 1],
                fecha_inicio=date(2026, (i - 1) % 12 + 1, min(i + 2, 28)),
            )
            proyecto_dao.insertar(proyecto)
            ids_proyecto[i] = proyecto.id_proyecto
            resumen["proyecto"]["creados"] += 1
            proyectos[nombre] = {
                "id_proyecto": proyecto.id_proyecto,
                "nombre": nombre,
            }

    # 5. Tabla asociativa: diez parejas empleado-proyecto distintas.
    for i in range(1, 11):
        id_empleado = ids_empleado[i]
        id_proyecto = ids_proyecto[i]
        if proyecto_dao.tiene_asignacion(id_proyecto, id_empleado):
            resumen["empleado_proyecto"]["existentes"] += 1
        else:
            proyecto_dao.asignar_empleado(id_proyecto, id_empleado)
            resumen["empleado_proyecto"]["creados"] += 1

    # 6. Diez registros de tiempo con marcadores estables para evitar duplicados.
    registros = registro_dao.obtener_todos()
    descripciones_existentes = {
        fila.get("descripcion_trabajo", "") for fila in registros
    }
    for i in range(1, 11):
        marcador = f"[SEMILLA-TIEMPO-{i:02d}]"
        if any(marcador in descripcion for descripcion in descripciones_existentes):
            resumen["registro_tiempo"]["existentes"] += 1
            continue

        registro = RegistroTiempo(
            fecha=date(2026, (i - 1) % 12 + 1, min(i + 4, 28)),
            horas_trabajadas=2 + (i % 7),
            descripcion_trabajo=(
                f"{marcador} Trabajo ficticio de demostracion numero {i:02d}."
            ),
            id_empleado=ids_empleado[i],
            id_proyecto=ids_proyecto[i],
        )
        registro_dao.insertar(registro)
        resumen["registro_tiempo"]["creados"] += 1
        descripciones_existentes.add(registro.descripcion_trabajo)

    return resumen


def imprimir_resumen(resumen):
    """Muestra una salida facil de entender en terminal."""
    nombres = {
        "departamento": "Departamentos",
        "empleado": "Empleados",
        "proyecto": "Proyectos",
        "empleado_proyecto": "Asignaciones empleado-proyecto",
        "registro_tiempo": "Registros de tiempo",
    }
    print("\nRESUMEN DE LA SEMILLA")
    print("-" * 56)
    for clave, etiqueta in nombres.items():
        datos = resumen[clave]
        print(
            f"{etiqueta:<36} agregados: {datos['creados']:>2} | "
            f"ya existentes: {datos['existentes']:>2}"
        )
    print("\nLa semilla no borra datos ajenos a ella.")
