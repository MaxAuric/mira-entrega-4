# Especificación SDD · <ID-FEATURE>: <Título de la Funcionalidad>

| Campo | Valor |
| :--- | :--- |
| **ID Especificación** | `SPEC-MIRA-E4` |
| **Alternativa** | Alternativa A · Desarrollo Conducido por Especificación (SDD) |
| **Estado** | `PENDIENTE_APROBACION` / `APROBADA POR REPRESENTANTE DEL CLIENTE` |
| **Representante del Cliente** | Joaquín Aguilera Arellano |
| **Fuentes Normativas** | `POL-DEC v2`, `CAT-SEN v3`, `DOC-MIRA v1.4`, Especificación F4/F5 |

---

## 1. Enunciado de la Necesidad del Cliente
> "<Cita textual de la necesidad del cliente en lenguaje natural>"

---

## 2. Detección de Ambigüedades (`[NEEDS CLARIFICATION]`) y Respuestas del Cliente

| ID | Ambigüedad Detectada (`[NEEDS CLARIFICATION]`) | Respuesta del Representante del Cliente | Fuente / Respaldo |
| :--- | :--- | :--- | :--- |
| **CL-01** | `[NEEDS CLARIFICATION]` <Pregunta 1> | <Respuesta 1> | <Fuente> |
| **CL-02** | `[NEEDS CLARIFICATION]` <Pregunta 2> | <Respuesta 2> | <Fuente> |

---

## 3. Historia de Usuario y Criterios de Aceptación (`Given / When / Then`)

**Historia de Usuario (`HU-01`):**
- **Como** organización cliente que opera sobre la plataforma MIRA,
- **Quiero** que al terminar de analizarse un caso se calcule su puntaje ponderado, se evalúe la precedencia de señales de fraude y mínimos por señal, y se determine automáticamente su decisión (`APROBADO`, `DERIVADO_A_REVISION` o `RECHAZADO`) usando mis propios umbrales configurados,
- **Para** agilizar la resolución auditable de casos sin comprometer las políticas de riesgo ni permitir que un puntaje alto oculte una alerta de fraude.

### Criterios de Aceptación Verificables (`AC-1` a `AC-N`)
- **`AC-1` (<Título>):**
  - **Given (Dado):** ...
  - **When (Cuando):** ...
  - **Then (Entonces):** ...

---

## 4. Especificación del Caso de Uso (`CU-MIRA-DECISION`)

- **Actores:** ...
- **Precondiciones:** ...
- **Flujo Principal:** ...
- **Flujos Alternativos y Excepciones:** ...

---

## 5. Fuera de Alcance (Alcance Negativo Explícito)
- ...

---

## 6. Punto de Control Humano #1 · Aprobación de la Especificación
- **Revisor Humano:** Joaquín Aguilera Arellano (Representante del Cliente)
- **Qué revisó:** ...
- **Decisión:** `APROBADA`
