# Ficha de trabajo - Clase 2

## Comprensión del problema y alcance

**Asignatura:** Programación Orientada a Objeto Seguro (TI3021)  
**Unidad:** 1  
**Modalidad:** Parejas  
**Tipo de actividad:** Formativa  

| Identificación | Información |
|---|---|
| Integrante 1 | diego flores |
| Integrante 2 | COMPLETAR |
| Sección y fecha | 13/08/2026 TI3021 |
| URL del repositorio | COMPLETAR AL FINAL |

## Propósito

Analizar y delimitar una funcionalidad antes de diseñar clases o escribir código. La ficha final debe permitir que otra persona comprenda qué necesita el sistema, qué reglas debe respetar y cómo comprobar si responde correctamente.

> **Regla de trabajo:** en esta clase no se diseñan clases, atributos ni métodos. Primero se justifica qué se necesita; la solución técnica comenzará en la Clase 3.

Sí, claro. Te lo dejo en formato de código/bloque de texto, manteniendo la misma estructura que me diste y completando únicamente los COMPLETAR.

## Situación inicial

> Un entrenador se encuentra con una criatura salvaje cercana e intenta capturarla utilizando una cápsula de su inventario.

## 1. Lectura activa: hechos, dudas y supuestos

### 1.1 Tres hechos explícitos

1. existe una criatura
2. que exista un entrenador
3. que ambos se encuentren

### 1.2 Tres ambigüedades convertidas en preguntas

| N.º | Expresión ambigua | Pregunta que debe responder el cliente |
|---:|---|---|
| 1 | debe de capturar a la criatura | que tan cercano debe ser para la captura |
| 2 | cual criatura se debe de capturar | que tipo de criatura se captura |
| 3 | debe tener exito o no | cual es el rango de exito o fallo de la captura |

### 1.3 Supuesto provisional

**Supuesto:** un entrenador desea capturar una criatura salvaje para incorporarla a su colección
**Por qué es provisional:** el enunciado indica que el entrenador intenta capturarla, pero no confirma que su objetivo sea incorporarla a su colección
**Cómo podría confirmarse:** preguntando al cliente cuál es el objetivo de realizar la captura

Un supuesto no es una verdad del caso. Debe quedar marcado hasta que el cliente, una regla oficial o una evidencia lo confirme.

## 2. Del enunciado a una necesidad clara

Fórmula orientadora:

> Permitir que **[actor]** realice **[acción]** sobre **[elemento]**, bajo **[condición]**, y obtenga **[resultado observable]**.

### 2.1 Actor, necesidad y objetivo

**Actor principal:** entrenador y criatura
**Necesidad:** Capturar a la criatura
**Objetivo reescrito:** se desea capturar a la criatura para la colección del entrenador

### 2.2 Entrada, proceso y salida (EPS)

#### Entradas necesarias

1. criatura salvaje
2. entrenador
3. cápsula disponible en el inventario
4. distancia entre el entrenador y la criatura

#### Proceso observable

1. el entrenador encuentra una criatura salvaje
2. se verifica la distancia entre el entrenador y la criatura
3. el entrenador selecciona una cápsula de su inventario
4. se intenta realizar la captura
5. se determina si la captura fue exitosa o fallida
6. si la captura es exitosa y el equipo tiene menos de seis criaturas, la criatura se incorpora al equipo; si el equipo está completo, se envía a la reserva

#### Salidas esperadas

1. resultado de la captura: exitosa o fallida
2. si la captura es exitosa y hay espacio, la criatura queda en el equipo del entrenador
3. si la captura es exitosa y el equipo tiene seis criaturas, la criatura queda en la reserva
4. si la captura falla, la criatura permanece salvaje y no se incorpora al equipo ni a la reserva

**Prueba de coherencia:** cada salida debe poder explicarse a partir de una entrada, una regla conocida y un paso del proceso.

## 3. Reglas, restricciones y alcance

Una **regla** define qué comportamiento es válido. Una **restricción** limita la solución posible. Un **supuesto** es una condición aceptada temporalmente.

### 3.1 Reglas del problema

1. solo se puede intentar capturar una criatura que se encuentre dentro de la distancia permitida
2. el entrenador debe disponer de una cápsula para intentar la captura
3. una captura puede resultar exitosa o fallida según una condición de éxito que debe ser confirmada
4. un entrenador puede tener como máximo seis criaturas activas; si una captura es exitosa y el equipo está completo, la criatura debe enviarse a la reserva

### 3.2 Restricciones

1. el entrenador no puede llevar más de seis criaturas activas
2. la captura requiere una cápsula disponible en el inventario
3. la distancia entre el entrenador y la criatura debe cumplir la condición establecida para poder intentar la captura

### 3.3 Delimitación de la primera versión

#### Dentro del alcance

1. encontrar una criatura salvaje y verificar si se encuentra dentro de la distancia permitida
2. intentar capturar la criatura utilizando una cápsula disponible
3. incorporar la criatura al equipo si la captura tiene éxito o enviarla a la reserva si el equipo está completo

#### Fuera del alcance

1. combates entre el entrenador y la criatura
2. evolución o entrenamiento de las criaturas
3. administración detallada de la reserva

#### Supuestos por confirmar

1. se supone que la criatura capturada pasa a formar parte de la colección del entrenador
2. se supone que existe una distancia máxima para poder intentar la captura
3. se supone que existe una condición o probabilidad que determina si la captura tiene éxito o falla

### 3.4 Preguntas pendientes

1. ¿Cuál es la distancia máxima permitida para intentar capturar una criatura?
2. ¿Qué condición determina si la captura tiene éxito o falla?

## 4. Criterios de aceptación y revisión entre pares

Un **criterio de aceptación** es una condición concreta y comprobable que permite decidir si una necesidad fue resuelta correctamente.

Estructura sugerida:

> Dado **[contexto]**, cuando **[acción]**, entonces **[resultado observable]**.

**Criterio 1:** Dado que el entrenador tiene una cápsula disponible y la criatura se encuentra dentro de la distancia permitida, cuando intenta capturarla y la captura es exitosa, entonces la criatura se incorpora al equipo si hay menos de seis criaturas activas.

**Criterio 2:** Dado que el entrenador tiene seis criaturas activas, cuando realiza una captura exitosa, entonces la nueva criatura se envía a la reserva.

### 4.1 Intercambio con otra pareja

La pareja revisora debe leer la ficha sin una explicación oral y detectar una ambigüedad que obligaría a inventar una regla al diseñar la solución.

**Pareja revisora:** otra pareja del curso
**Ambigüedad detectada:** no está definida la condición exacta que determina el éxito o fallo de la captura
**Pregunta sugerida:** ¿Qué condición determina que una captura sea exitosa o falle?
**Decisión del equipo:** ACEPTAR
**Justificación:** es una regla necesaria para determinar el resultado de la captura y actualmente no está definida.

## 5. IA como auditora de requisitos

Primero guarden la ficha original. La IA puede detectar vacíos y formular preguntas, pero el equipo conserva la responsabilidad de decidir y justificar cada cambio.

### 5.1 Registro de la consulta

**Herramienta y fecha:** ChatGPT, 13 de agosto de 2026
**Versión original guardada:** NO

**Prompt sugerido:**

> Actúa como revisor de requisitos. Analiza esta ficha de captura sin diseñar clases ni escribir código. Detecta ambigüedades o contradicciones; formula cinco preguntas; señala reglas no verificables; no inventes respuestas y marca cada supuesto.

### 5.2 Evaluación de observaciones

| Observación de la IA | Decisión | Justificación del equipo | Cambio realizado |
|---|---|---|---|
| No está definida la distancia necesaria para intentar una captura | Aceptar | Es una condición necesaria para determinar si se puede realizar el intento | Se marcó como supuesto y pregunta pendiente |
| No está definida la condición que determina el éxito o fallo de la captura | Aceptar | No se debe inventar una regla que el enunciado no proporciona | Se marcó como supuesto y pregunta pendiente |
| No se indicaba qué ocurre cuando el entrenador tiene seis criaturas activas | Aceptar | La nueva condición establece que una captura exitosa debe enviarse a la reserva | Se agregó la regla al proceso, las salidas y los criterios de aceptación |

### 5.3 Pregunta de autoría

**¿Qué sugerencia rechazaron?** Ninguna de las observaciones anteriores fue rechazada
**¿Por qué no correspondía?** No corresponde rechazar las observaciones porque identifican vacíos reales del enunciado
**¿Qué decisión fue exclusivamente del equipo?** Decidir que una captura exitosa se incorpore al equipo cuando exista espacio y se envíe a la reserva cuando el equipo tenga seis criaturas

> No publiquen contraseñas, correos personales, claves, tokens ni información sensible en la consulta o en el repositorio.

## 6. Mini desafío: cambia una condición

> Cada entrenador puede llevar como máximo seis criaturas activas. Si su equipo está completo, una captura exitosa debe enviarse a la reserva.

### 6.1 Análisis del impacto

**Qué cambió:** se estableció un máximo de seis criaturas activas y se definió que una captura exitosa debe enviarse a la reserva cuando el equipo está completo
**Secciones afectadas:** ENTRADA / PROCESO / SALIDA / REGLA / ALCANCE / SUPUESTO
**Nueva decisión:** si el entrenador tiene menos de seis criaturas activas, la criatura capturada se incorpora al equipo; si tiene seis, se envía a la reserva
**Justificación:** permite determinar qué ocurre con una captura exitosa cuando el equipo del entrenador está completo

### 6.2 Actualización

| Elemento | Antes | Después del cambio |
|---|---|---|
| Entrada/EPS | criatura, entrenador y cápsula disponible | criatura, entrenador, cápsula disponible y cantidad de criaturas activas del entrenador |
| Proceso | la captura exitosa incorpora la criatura al entrenador | se verifica la cantidad de criaturas activas; si hay menos de seis, se incorpora al equipo; si hay seis, se envía a la reserva |
| Regla | no existía un límite definido de criaturas activas | el entrenador puede llevar como máximo seis criaturas activas |
| Alcance | incorporación de una criatura capturada | incorporación al equipo o envío a la reserva cuando el equipo está completo |

### 6.3 Nuevo criterio de aceptación

**Criterio:** Dado que el entrenador tiene seis criaturas activas, cuando realiza una captura exitosa, entonces la nueva criatura debe enviarse a la reserva y el equipo debe continuar teniendo seis criaturas activas
**Evidencia esperada:** la criatura capturada aparece en la reserva y el equipo del entrenador mantiene seis criaturas activas

## 7. Ticket de salida

**Resumen en una frase con actor, necesidad, regla principal y resultado:** El entrenador necesita capturar una criatura salvaje mediante una cápsula y, si la captura es exitosa, incorporarla a su equipo siempre que tenga menos de seis criaturas activas; si el equipo está completo, debe enviarse a la reserva
**Evidencia más clara:** una captura exitosa con el equipo del entrenador completo que muestre que la nueva criatura fue enviada a la reserva
**Ambigüedad pendiente:** no está definida la condición exacta que determina el éxito o fallo de la captura
**Mejora concreta:** confirmar con el cliente la distancia máxima de captura y la condición que determina el éxito o fallo de la captura

## 8. Comprobación final

- [ ] Conservamos una versión anterior a la auditoría con IA.
- [ ] Actor, necesidad, entradas, proceso y salidas son coherentes.
- [ ] Reglas, restricciones, supuestos y alcance están diferenciados.
- [ ] Los criterios de aceptación son observables y verificables.
- [ ] El cambio del cliente quedó incorporado y justificado.
- [ ] No diseñamos clases ni escribimos código antes de tiempo.

## 9. Entrega

1. Crear un repositorio privado por pareja y agregar al docente como colaborador.
2. Guardar este archivo como `docs/ficha_clase_2.md`.
3. Realizar commits con mensajes claros. Se espera al menos un aporte identificable de cada integrante.
4. Cada estudiante debe pegar el mismo enlace del repositorio en AAI/Intranet e identificar a su pareja.
5. Incluir el identificador del commit final en la entrega.

Convención sugerida para el repositorio:

```text
  poos-p13-c3-portafolio-apellido-nombre
```

Primer flujo Git:

```bash
git clone URL_DEL_REPOSITORIO
cd NOMBRE_DEL_REPOSITORIO
git status
git add docs/ficha_clase_2.md
git commit -m "Completa ficha de alcance de captura"
git push
```

Si existe un bloqueo real de cuenta, autenticación o conectividad, cada integrante debe subir temporalmente la ficha en DOCX o PDF a AAI/Intranet y regularizar el repositorio en la clase siguiente. En esta primera práctica, el dominio técnico de Git no modifica la valoración conceptual de la ficha.
