# Especificación SDD · `SPEC-MIRA-E4`: Motor de Puntaje Ponderado, Precedencia de Fraude y Decisión por Umbrales de Cliente

| Campo | Valor |
| :--- | :--- |
| **ID Especificación** | `SPEC-MIRA-E4` |
| **Agente Autor** | `especificador` (`.github/agents/especificador.agent.md`) |
| **Skill Cargada** | `sdd-spec-checklist` (`.github/skills/sdd-spec-checklist/SKILL.md` + Plantilla Nivel 3 `plantilla_especificacion.md`) |
| **Alternativa** | Alternativa A · Desarrollo Conducido por Especificación (SDD) |
| **Estado** | `APROBADA POR REPRESENTANTE DEL CLIENTE` |
| **Representante del Cliente** | Joaquín Aguilera Arellano *(Rol rotado respecto a la Entrega 2)* |
| **Fuentes Normativas** | `POL-DEC v2`, `CAT-SEN v3`, `DOC-MIRA v1.4`, Especificación F4/F5 (Entregas 1 y 2) |
| **Fecha de Aprobación** | 18 de Noviembre de 2026 |

---

## 1. Enunciado de la Necesidad del Cliente

> *"Cuando un caso termina de analizarse, necesitamos que MIRA calcule un puntaje y decida sola si lo aprueba, lo deriva a revisión o lo rechaza. Si aparece una señal de fraude, eso manda por sobre todo lo demás. Cada cliente debe poder tener sus propios umbrales."*

---

## 2. Detección de Ambigüedades (`[NEEDS CLARIFICATION]`) y Respuestas del Representante del Cliente

Siguiendo la fase `Clarify` de SDD, el agente `especificador` identificó tres zonas grises en el enunciado inicial y las consultó al Representante del Cliente antes de congelar los criterios de aceptación:

| ID | Ambigüedad Detectada (`[NEEDS CLARIFICATION]`) | Respuesta Oficial del Representante del Cliente (Joaquín Aguilera) | Fuente / Respaldo |
| :--- | :--- | :--- | :--- |
| **`CL-01`** | `[NEEDS CLARIFICATION]` ¿Cómo se ponderan las señales individuales para calcular el puntaje del caso y qué debe decidir MIRA si falta alguna de las señales esperadas? | El puntaje se calcula mediante la suma ponderada $\text{Puntaje} = \sum (V_i \times W_i)$ redondeada a 2 decimales con los pesos oficiales de MIRA: `DOC_AUT` ($0.35$), `BIO_ROSTRO` ($0.30$), `CRUCE_MONTO` ($0.20$) y `CRUCE_FECHA` ($0.15$). Si falta cualquiera de esas 4 señales obligatorias, el caso **jamás se aprueba con información parcial**: debe derivarse a revisión (`DERIVADO_A_REVISION`) indicando qué señal faltó. | `SPEC-F4` (Entrega 1/2) y `POL-DEC v2 §6` (*Señales faltantes*) |
| **`CL-02`** | `[NEEDS CLARIFICATION]` ¿Qué ocurre si el puntaje total alcanza el umbral de aprobación pero una señal individual está bajo su mínimo crítico, y qué códigos exactos de decisión se esperan frente a fraude o puntaje bajo? | Las tres decisiones posibles son `APROBADO`, `DERIVADO_A_REVISION` y `RECHAZADO`, con este orden estricto de precedencia: 1) Si existe al menos una señal de fraude activa del catálogo (`FRA_EDICION`, `FRA_MEMORIA`, `FRA_SINTETICO`), manda sobre todo y la decisión es `RECHAZADO` inmediato (`fraude_detectado = True`). 2) Si no hay fraude pero falta una señal o alguna señal incumple su mínimo propio (`DOC_AUT < 70`, `BIO_ROSTRO < 75`, `CRUCE_MONTO < 60`, `CRUCE_FECHA < 60`), la decisión es `DERIVADO_A_REVISION`. 3) Si cumple mínimos y no hay fraude: $\text{Puntaje} \ge \text{umbral\_aprobacion} \rightarrow$ `APROBADO`; $\text{Puntaje} \le \text{umbral\_rechazo} \rightarrow$ `RECHAZADO`; y entre ambos umbrales $\rightarrow$ `DERIVADO_A_REVISION`. | `POL-DEC v2 §3-§4`, `CAT-SEN v3 §6` y `SPEC-F4` |
| **`CL-03`** | `[NEEDS CLARIFICATION]` ¿Qué restricciones de negocio deben validarse cuando una organización cliente configura o modifica sus propios umbrales? | Cada organización cliente (`ORG-01`, `ORG-02`, `ORG-03`) gestiona su propio `umbral_aprobacion` y `umbral_rechazo` de forma aislada. Ambos valores deben estar entre `0.0` y `100.0` y debe cumplirse estrictamente `umbral_rechazo < umbral_aprobacion`. Si se intenta configurar un umbral negativo, mayor a 100 o con `umbral_rechazo >= umbral_aprobacion`, la operación debe rechazarse con un error de validación sin alterar la configuración vigente. Toda actualización válida incrementa en $+1$ la versión de umbrales del cliente. | `SPEC-F5` (`AC-F5-03`), `POL-DEC v2 §5` y `DOC-MIRA v1.4 §3` |

---

## 3. Historia de Usuario y Criterios de Aceptación (`Given / When / Then`)

### Historia de Usuario (`HU-01`)
- **Como** organización cliente que opera en la plataforma MIRA (`ORG-01`, `ORG-02`, `ORG-03`),
- **Quiero** que cuando un caso termine de analizarse, MIRA calcule su puntaje de confianza ponderado, verifique la precedencia absoluta de señales de fraude y el cumplimiento de mínimos por señal, y determine sola si lo aprueba (`APROBADO`), lo deriva a revisión (`DERIVADO_A_REVISION`) o lo rechaza (`RECHAZADO`) aplicando los umbrales propios y versionados de mi organización,
- **Para** automatizar decisiones consistentes y auditables sin que un puntaje promedio alto oculte señales de fraude o documentos bajo el estándar mínimo de calidad.

---

### Criterios de Aceptación Verificables (`AC-1` a `AC-6`)

* **`AC-1` · Cálculo de puntaje ponderado y aprobación automática sobre el umbral del cliente:**
  - **Given (Dado):** Una organización cliente registrada (por ejemplo `ORG-01` con `umbral_aprobacion = 85.0` y `umbral_rechazo = 60.0`) y un caso analizado que contiene las cuatro señales obligatorias sobre sus mínimos individuales (`DOC_AUT = 90.0`, `BIO_ROSTRO = 85.0`, `CRUCE_MONTO = 80.0`, `CRUCE_FECHA = 80.0`) y ninguna señal de fraude activa.
  - **When (Cuando):** El caso termina de analizarse y se solicita a MIRA su evaluación.
  - **Then (Entonces):** MIRA calcula el puntaje ponderado exacto $\text{Puntaje} = 90\times 0.35 + 85\times 0.30 + 80\times 0.20 + 80\times 0.15 = 85.0$, registra el desglose de aporte por componente y emite la decisión `APROBADO` con `fraude_detectado = False` y la versión de umbrales aplicada.

* **`AC-2` · Precedencia absoluta de señal de fraude activa por sobre cualquier puntaje:**
  - **Given (Dado):** Un caso analizado perteneciente a cualquier organización cliente cuyas señales numéricas arrojan un puntaje ponderado sobresaliente (por ejemplo `96.45 >= umbral_aprobacion`), pero que presenta al menos una señal de fraude activa del catálogo oficial (`FRA_EDICION`, `FRA_MEMORIA` o `FRA_SINTETICO`).
  - **When (Cuando):** MIRA evalúa el caso para tomar la decisión.
  - **Then (Entonces):** La señal de fraude prevalece por sobre el puntaje total y MIRA emite inmediatamente la decisión `RECHAZADO`, marcando `fraude_detectado = True` e indicando en el motivo los códigos de fraude detectados. Si se envía un código de fraude inexistente en `CAT-SEN v3`, el sistema informa un error de validación.

* **`AC-3` · Derivación a revisión por puntaje intermedio o por señal individual bajo su mínimo propio (`POL-DEC v2 §3`):**
  - **Given (Dado):** Un caso sin señales de fraude activas que: (a) obtiene un puntaje ponderado estrictamente entre `umbral_rechazo` y `umbral_aprobacion` (ej. `75.0` en `ORG-01`), o bien (b) obtiene un puntaje ponderado total $\ge \text{umbral\_aprobacion}$ (ej. `85.25` con `DOC_AUT = 55.0`, `BIO_ROSTRO = 98.0`, `CRUCE_MONTO = 98.0`, `CRUCE_FECHA = 98.0`), pero donde al menos una señal cae bajo su mínimo propio (`DOC_AUT < 70.0`, `BIO_ROSTRO < 75.0`, `CRUCE_MONTO < 60.0` o `CRUCE_FECHA < 60.0`).
  - **When (Cuando):** MIRA evalúa el caso.
  - **Then (Entonces):** MIRA emite la decisión `DERIVADO_A_REVISION` y, en el caso (b), lista explícitamente en `senales_bajo_minimo` los códigos de las señales que incumplieron su umbral mínimo individual.

* **`AC-4` · Rechazo por puntaje bajo el umbral de rechazo y derivación obligatoria ante señales faltantes (`POL-DEC v2 §6`):**
  - **Given (Dado):** Un caso sin señales de fraude activas donde: (a) están presentes las cuatro señales y el puntaje ponderado resultante es $\le \text{umbral\_rechazo}$ de la organización (ej. `52.0 <= 60.0` en `ORG-01`), o bien (b) falta una o más de las cuatro señales obligatorias del catálogo (`DOC_AUT`, `BIO_ROSTRO`, `CRUCE_MONTO`, `CRUCE_FECHA`).
  - **When (Cuando):** MIRA evalúa el caso.
  - **Then (Entonces):** En el escenario (a) MIRA emite la decisión `RECHAZADO` por puntaje insuficiente; en el escenario (b) MIRA jamás aprueba con información parcial y emite obligatoriamente `DERIVADO_A_REVISION` detallando en el motivo qué señales faltaron.

* **`AC-5` · Independencia y aislamiento de umbrales propios por organización cliente (`DOC-MIRA v1.4 §3`):**
  - **Given (Dado):** Dos organizaciones cliente con distintos umbrales vigentes en MIRA (por ejemplo `ORG-01` con `umbral_aprobacion = 85.0` y `ORG-02` con `umbral_aprobacion = 80.0`) y dos casos con idénticas señales numéricas que producen un puntaje ponderado de `82.0` (cumpliendo todos los mínimos individuales y sin fraude).
  - **When (Cuando):** MIRA evalúa el primer caso para `ORG-01` y el segundo caso para `ORG-02`.
  - **Then (Entonces):** MIRA aplica los umbrales propios de cada organización, resolviendo `DERIVADO_A_REVISION` para `ORG-01` (`82.0 < 85.0`) y `APROBADO` para `ORG-02` (`82.0 >= 80.0`). Si se consulta o evalúa una organización inexistente, el sistema rechaza la solicitud indicando que la organización no existe.

* **`AC-6` · Configuración y actualización validada de umbrales por cliente con control de versión:**
  - **Given (Dado):** Una organización cliente existente en MIRA (ej. `ORG-01` en `version = 1`) que solicita actualizar su `umbral_aprobacion` y su `umbral_rechazo`.
  - **When (Cuando):** Se envían nuevos valores de umbrales.
  - **Then (Entonces):** Si los valores cumplen $0.0 \le \text{umbral\_rechazo} < \text{umbral\_aprobacion} \le 100.0$, MIRA actualiza los umbrales de esa organización, incrementa su `version` en $+1$ y registra el `autor_ultimo_cambio`. Si `umbral_rechazo >= umbral_aprobacion` o algún valor está fuera de $[0, 100]$, MIRA rechaza el cambio con error de validación y conserva intacta la versión anterior.

---

## 4. Especificación del Caso de Uso (`CU-MIRA-DECISION`)

| Elemento | Especificación Formal |
| :--- | :--- |
| **Código y Nombre** | `CU-MIRA-DECISION` · Calcular puntaje de confianza, aplicar precedencia de fraude y decidir caso según umbrales del cliente |
| **Actores** | **Actor Primario:** Sistema Analizador Multimodal de MIRA / Operador o Administrador de Organización Cliente (`ORG-01`, `ORG-02`, `ORG-03`). **Actor Secundario:** Representante de Riesgo / Cumplimiento de la Organización Cliente. |
| **Precondiciones** | 1. La organización cliente (`org_id`) se encuentra registrada en MIRA con una versión vigente de `umbral_aprobacion` y `umbral_rechazo`. <br/> 2. El catálogo oficial de pesos (`PESOS_SENALES`), mínimos (`MINIMOS_POR_SENAL`) y señales de fraude (`CATALOGO_SENALES_FRAUDE`) está cargado. |
| **Flujo Principal (Camino Feliz)** | 1. El cliente o módulo analizador envía a MIRA los datos del caso (`caso_id`, `org_id`, `senales_numericas` y `senales_fraude_activas`). <br/> 2. MIRA recupera la configuración vigente de umbrales perteneciente a `org_id` (`AC-5`). <br/> 3. MIRA verifica que los códigos de fraude enviados pertenezcan a `CATALOGO_SENALES_FRAUDE` y que los valores numéricos estén en el rango $[0, 100]$. <br/> 4. MIRA calcula el aporte ponderado de cada señal presente ($\text{Valor}_i \times \text{Peso}_i$) y obtiene el `puntaje_confianza` total redondeado a 2 decimales (`AC-1`). <br/> 5. MIRA verifica que no existan señales de fraude activas, que estén presentes las 4 señales obligatorias y que todas cumplan su mínimo individual en `MINIMOS_POR_SENAL`. <br/> 6. MIRA compara el `puntaje_confianza` contra `umbral_aprobacion` y `umbral_rechazo` de la organización y determina la decisión (`APROBADO`, `DERIVADO_A_REVISION` o `RECHAZADO`). <br/> 7. MIRA retorna el resultado completo auditable (`ResultadoDecision`). |
| **Flujos Alternativos** | **FA-1 (Señal de fraude activa — `AC-2`):** En el paso 5, si `senales_fraude_activas` contiene al menos una señal válida, MIRA asigna inmediatamente `decision = "RECHAZADO"`, `fraude_detectado = True` y detalla en `motivo` la precedencia de fraude sobre el puntaje. <br/> **FA-2 (Señales faltantes — `AC-4`):** En el paso 5, si no hay fraude pero falta alguna de las 4 señales de `PESOS_SENALES`, MIRA asigna `decision = "DERIVADO_A_REVISION"` indicando las señales faltantes. <br/> **FA-3 (Señal bajo mínimo propio — `AC-3`):** En el paso 5, si están las 4 señales sin fraude pero alguna es menor a su mínimo en `MINIMOS_POR_SENAL`, MIRA asigna `decision = "DERIVADO_A_REVISION"` y registra los códigos en `senales_bajo_minimo`. <br/> **FA-4 (Actualización de umbrales del cliente — `AC-6`):** El administrador de una organización actualiza sus umbrales cumpliendo $0 \le \text{rechazo} < \text{aprobacion} \le 100$; MIRA incrementa `version` en $+1$ y aplica los nuevos umbrales a las evaluaciones siguientes. |
| **Excepciones** | **EX-1 (Organización no registrada — `AC-5`):** Si `org_id` no existe en MIRA, se rechaza la operación con error de organización no encontrada (HTTP 404 / `KeyError`). <br/> **EX-2 (Umbrales inválidos o invertidos — `AC-6`):** Si se intenta actualizar umbrales con `umbral_rechazo >= umbral_aprobacion` o fuera de $[0, 100]$, se lanza error de validación (HTTP 400 / `ValueError`) sin mutar el estado. <br/> **EX-3 (Señal de fraude desconocida o valor numérico fuera de $[0, 100]$):** Se rechaza la solicitud con error de validación (HTTP 400 / `ValueError`). |

---

## 5. Fuera de Alcance (Alcance Negativo Explícito)

Para evitar que los agentes `planificador` o `implementador` agreguen complejidad innecesaria o funcionalidades no solicitadas, queda explícitamente **fuera de alcance**:
1. No se implementará procesamiento OCR, visión por computadora ni extracción cruda de imágenes/PDF (el motor recibe las señales ya medidas de `0` a `100`).
2. No se implementarán motores de bases de datos externos (PostgreSQL/MongoDB en la nube) que requieran credenciales o conexión a internet; toda la persistencia opera en memoria de forma determinista y autónoma.
3. No se implementará autenticación OAuth/JWT ni envío de correos o notificaciones externas.

---

## 6. Checklist de Calidad (`sdd-spec-checklist`) y Punto de Control Humano #1

### Verificación de la Skill `sdd-spec-checklist`
- [x] ¿Todos los criterios tienen formato `Given / When / Then` e identificador único `AC-1` a `AC-6`? **Sí.**
- [x] ¿Se incluye el Caso de Uso con actores, precondiciones, flujo principal, flujos alternativos y excepciones? **Sí.**
- [x] ¿Todas las etiquetas `[NEEDS CLARIFICATION]` (`CL-01`, `CL-02`, `CL-03`) tienen respuesta del Representante del Cliente con su fuente? **Sí.**
- [x] ¿Está declarada la sección `Fuera de alcance` y la especificación no acopla detalles internos de código? **Sí.**

### Registro de Decisión Humana · Punto de Control Humano #1 (`PCH-1`)
- **Persona que revisa:** Joaquín Aguilera Arellano (*Representante del Cliente*).
- **Qué revisó:**
  1. Que las respuestas a las tres ambigüedades (`CL-01` suma ponderada y señales faltantes, `CL-02` precedencia de fraude y mínimos individuales `POL-DEC v2 §3`, `CL-03` invariante `umbral_rechazo < umbral_aprobacion`) reflejen fielmente las reglas de negocio de MIRA.
  2. Que los 6 criterios de aceptación (`AC-1` a `AC-6`) cubran todos los escenarios que luego se probarán en vivo en el Backend y en el Frontend.
- **Decisión tomada:** **`APROBADA POR REPRESENTANTE DEL CLIENTE`**. Se autoriza versionar esta especificación en un **commit propio exclusivo** antes de pasar al agente `planificador` y antes de escribir cualquier línea de código.
