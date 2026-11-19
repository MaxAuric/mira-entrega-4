# Documento de Decisión Arquitectónica (`docs/decision.md`)
## Sistema Multiagente para Desarrollo Conducido por Especificación (SDD) · Caso MIRA

| Campo | Detalle |
| :--- | :--- |
| **Proyecto** | MIRA — Plataforma de Inteligencia Multimodal para Decisiones Empresariales (DPRIME SpA) |
| **Alternativa Elegida** | **Alternativa A · Desarrollo de Software Conducido por Especificación (SDD)** |
| **Patrón Principal** | Combinación de **Patrón 1 (Secuencial / Prompt Chaining)** + **Patrón 6 (Traspaso con Humano en el Ciclo / Handoffs)** + **Patrón 5 (Evaluador y Optimizador)** en la etapa de verificación (máx. 2 iteraciones) |
| **Patrones Descartados** | **Patrón 3 (Paralelización)** y **Patrón 4 (Orquestador Autónomo sin control humano intermedio)** |
| **Integrantes** | Max Latuz Zepeda & Joaquín Aguilera Arellano (Representante del Cliente) |

---

## 1. Diagrama del Sistema Multiagente, Traspasos y Puntos de Control Humano

El siguiente diagrama Mermaid representa el recorrido completo de la **Alternativa A (SDD)** desde la entrada de la necesidad del cliente en lenguaje natural hasta el cierre con código y pruebas en verde, detallando los **4 agentes**, las **3 skills**, los **4 archivos de traspaso en `docs/trabajo/`** y los **Puntos de Control Humano**:

```mermaid
flowchart TD
    Cliente(["Necesidad del Cliente en Lenguaje Natural"])
    
    subgraph Fase_Especificacion ["Etapa 1: Specify & Clarify"]
        A1["Agente 1: especificador<br/>tools: read, search, edit"]
        S1[["Skill 1: sdd-spec-checklist<br/>Nivel 3: plantilla_especificacion.md"]]
        S1 -.->|Carga plantilla y checklist| A1
        F1[/"docs/trabajo/01_especificacion.md<br/>(HU Given/When/Then + CU + Aclaraciones)"/]
        A1 -->|Escribe| F1
    end

    PCH1{{"PUNTO DE CONTROL HUMANO #1 (Obligatorio Alt. A)<br/>Representante del Cliente (Joaquín Aguilera)<br/>Responde [NEEDS CLARIFICATION] y aprueba Spec en commit propio"}}

    subgraph Fase_Planificacion ["Etapa 2: Plan & Tasks"]
        A2["Agente 2: planificador<br/>tools: read, search, edit"]
        F2[/"docs/trabajo/02_plan_tareas.md<br/>(Arquitectura + Tareas T-01..T-N + Matriz AC-N)"/]
        A2 -->|Escribe| F2
    end

    PCH2{{"PUNTO DE CONTROL HUMANO #2 (Adicional)<br/>Revisión Humana de Arquitectura y Tareas<br/>Valida contratos API y cobertura AC-1..AC-6 antes de codificar"}}

    subgraph Fase_Construccion_Revision ["Etapas 3 y 4: Ciclo Evaluador-Optimizador (Máx. 2 Iteraciones)"]
        A3["Agente 3: implementador<br/>tools: read, search, edit, execute"]
        S3[["Skill 3: ejecutor-pruebas<br/>Nivel 3: ejecutar_suite.py"]]
        S3 -.->|Ejecuta pytest y resume tabla| A3
        F3[/"src/*.py + tests/*.py (# AC-N)<br/>docs/trabajo/03_implementacion.md"/]
        A3 -->|Escribe| F3

        A4["Agente 4: revisor (SIN edit)<br/>tools: read, search, execute"]
        S2[["Skill 2: verificador-trazabilidad<br/>Nivel 3: verificar_trazabilidad.py"]]
        S2 -.->|Audita AC-N y genera reporte| A4
        F4[/"docs/trabajo/04_revision.md<br/>(Veredicto: APROBADO o RECHAZADO)"/]
        A4 -->|Genera vía script Nivel 3| F4
    end

    Cierre(["Cierre: Código con Pruebas en Verde y Trazabilidad 100%"])

    Cliente --> A1
    F1 --> PCH1
    PCH1 -->|Handoff aprobado| A2
    F2 --> PCH2
    PCH2 -->|Handoff aprobado| A3
    F3 -->|Handoff a revisión| A4
    F4 -->|RECHAZADO (Iteración < 2)| A3
    F4 -->|APROBADO (100% AC-N y pytest OK)| Cierre
```

---

## 2. Tabla de Diseño de los Cuatro Agentes (Rúbrica I1)

Cada agente tiene un rol único sin superposición, un contrato de salida explícito en `docs/trabajo/` y un criterio de término verificable:

| Agente (`.github/agents/`) | Rol y Responsabilidad Principal | Herramientas (`tools`) | Entrada que Consume | Contrato de Salida (Archivo que Escribe) | Criterio de Término | Skills que Usa | ¿Qué pasa si lo quito? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`especificador`** (`especificador.agent.md`) | **Ingeniero de Requisitos SDD (*Specify & Clarify*):** Traduce la necesidad del cliente en Historia de Usuario (`Given/When/Then`), Caso de Uso, Alcance Negativo y detecta ambigüedades `[NEEDS CLARIFICATION]`. | `['read', 'search', 'edit']` | Enunciado del cliente + respuestas del Representante del Cliente + `.github/copilot-instructions.md`. | `docs/trabajo/01_especificacion.md` | Todas las dudas `[NEEDS CLARIFICATION]` están respondidas, el checklist SDD se cumple al 100% y el humano aprueba en commit propio. | `sdd-spec-checklist` (Plantilla Nivel 3) | El programador asume reglas ambiguas en silencio (*vibe coding*), inventando qué hacer ante empate de umbral o señal faltante. |
| **`planificador`** (`planificador.agent.md`) | **Arquitecto de Software (*Plan & Tasks*):** Diseña contratos de funciones y API y desglosa tareas ordenadas por dependencia con mapeo 1:1 hacia `AC-1..AC-6`. | `['read', 'search', 'edit']` | `docs/trabajo/01_especificacion.md` aprobada + lectura de `src/` y `tests/` base. | `docs/trabajo/02_plan_tareas.md` | El 100% de los criterios `AC-1..AC-6` tiene tarea de código y tarea de test asignada, y el humano aprueba el plan. | *(Lee salida de `sdd-spec-checklist`)* | El implementador mezcla decisiones de arquitectura con codificación, omitiendo endpoints o rompiendo modelos existentes en `src/models.py`. |
| **`implementador`** (`implementador.agent.md`) | **Desarrollador Backend Senior (*Implement*):** Escribe pruebas (`tests/`) y código (`src/`) con comentarios obligatorios `# AC-N` y corrige hallazgos del revisor. | `['read', 'search', 'edit', 'execute']` | `docs/trabajo/01_especificacion.md` + `docs/trabajo/02_plan_tareas.md` (+ `04_revision.md` si es iteración 2). | `src/*.py`, `tests/*.py` y `docs/trabajo/03_implementacion.md` | Todas las tareas del plan están codificadas con `# AC-N`, `pytest` se ejecuta vía skill y `03_implementacion.md` queda escrito. | `ejecutor-pruebas` (Script Nivel 3) | No hay construcción ejecutable del motor de decisión ni de la suite de pruebas automatizadas. |
| **`revisor`** (`revisor.agent.md`) | **Auditor QA / SDD Independiente (*Verify & Analyze*):** Audita en modo **solo lectura** que el código y tests cumplan la especificación y la trazabilidad 1:1. | `['read', 'search', 'execute']` *(SIN `edit`)* | `01_especificacion.md`, `02_plan_tareas.md`, `03_implementacion.md`, `src/` y `tests/`. | `docs/trabajo/04_revision.md` *(generado por script Nivel 3)* | `Veredicto: APROBADO` con 0 hallazgos de trazabilidad y 100% de tests en verde (o tope máximo de 2 iteraciones alcanzado). | `verificador-trazabilidad` y `ejecutor-pruebas` (Scripts Nivel 3) | El mismo agente que programa evalúa su propio código: puede debilitar un test o pasar por alto un `# AC-N` faltante para terminar rápido. |

---

## 3. Justificación del Patrón de Coordinación y Alternativa Descartada (Rúbrica I3)

### 3.1. Patrón Elegido: Secuencial con Traspaso Humano (*Handoffs*) + Cierre Evaluador-Optimizador
Entre los seis patrones vistos en clases, diseñamos una **combinación justificada** de tres patrones complementarios que sigue la arquitectura de contexto **ICM** vista en clases (*un agente a la vez: parte en limpio en cada etapa y las notas/archivos en `docs/trabajo/` llevan el trabajo*):
1. **Patrón 1 · Secuencial (*Prompt Chaining*)** entre las etapas `especificador` $\rightarrow$ `planificador` $\rightarrow$ `implementador`:
   - *Por qué se ajusta al caso:* El flujo SDD (`Specify` $\rightarrow$ `Clarify` $\rightarrow$ `Plan` $\rightarrow$ `Tasks` $\rightarrow$ `Implement`) tiene una dependencia causal estricta: no se puede planificar la arquitectura sin una especificación cerrada, ni programar sin tareas trazadas a los criterios `AC-N`.
2. **Patrón 6 · Traspaso con Humano en el Ciclo (*Handoffs con `send: false`*)** en los Puntos de Control Humano #1 y #2:
   - *Por qué se ajusta al caso:* La Alternativa A exige que ninguna línea de código se escriba antes de que una persona apruebe la especificación en un commit propio. Configurar `handoffs` con `send: false` garantiza que el agente se detenga, entregue su archivo en `docs/trabajo/` y espere la decisión humana.
3. **Patrón 5 · Evaluador y Optimizador** entre `implementador` $\leftrightarrow$ `revisor` (acotado a **máximo 2 iteraciones**):
   - *Por qué se ajusta al caso:* La verificación de código y trazabilidad tiene criterios objetivos y ejecutables (`pytest` + `verificar_trazabilidad.py`). Cuando el `revisor` (que no puede editar) detecta una brecha frente a la especificación, devuelve un reporte accionable en `docs/trabajo/04_revision.md` para que el `implementador` lo corrija en una segunda iteración controlada.

### 3.2. Patrones Descartados: Argumentos de Costo, Riesgo y Control
Se descartaron explícitamente el **Patrón 3 (Paralelización)** y el **Patrón 4 (Orquestador y Trabajadores totalmente autónomo)** por tres razones técnicas fundamentales:

| Dimensión | Patrón Elegido (Secuencial + Handoff Humano + Evaluador-Optimizador) | Patrón Descartado 1: Paralelización (Agentes corriendo en simultáneo) | Patrón Descartado 2: Orquestador Autónomo (`tools: ['agent']` sin frenos intermedios) |
| :--- | :--- | :--- | :--- |
| **Costo (Tokens y Cuota RPD)** | **Bajo y predecible (~8 a 12 requests en total):** Cada agente se invoca solo cuando el artefacto previo en `docs/trabajo/` está validado, cuidando la cuota diaria (RPD) de Gemini Flash Lite. | **Alto e ineficiente ($N\times$ tokens):** Si se lanzan agentes en paralelo antes de congelar la especificación, cualquier aclaración del cliente invalida el trabajo simultáneo y obliga a re-ejecutar todo. | **Medio-Alto y variable:** El agente orquestador consume tokens extra en cada turno para decidir a qué subagente invocar y reenviar el contexto completo (*Default context passing*). |
| **Riesgo Técnico (MAST / OWASP)** | **Bajo (Mitigación de Cascading Failures `ASI08`):** Las compuertas humanas entre etapas cortan la propagación de errores tempranos antes de llegar al código. | **Muy Alto (Desalineación MAST):** El programador y el creador de tests trabajando en paralelo sin un `01_especificacion.md` congelado asumen contratos de datos incompatibles. | **Alto (Pérdida de traza y violación de regla SDD):** Un orquestador autónomo puede invocar al `implementador` inmediatamente después del `especificador`, saltándose el commit humano obligatorio de aprobación del spec. |
| **Control y Auditabilidad** | **Total:** Cada traspaso queda persistido en `docs/trabajo/01..04.md` y versionado en commits separados de Git, permitiendo auditar exactamente qué entró y qué salió en cada etapa. | **Bajo:** No existe orden causal; requiere un agente agregador adicional que reconcilie salidas contradictorias. | **Opaco:** Los subagentes se ejecutan como cajas negras internas del orquestador sin botones `handoff` (`send: false`) para que el Representante del Cliente intervenga. |

---

## 4. Justificación de Herramientas (`tools`) y Seguridad por Agente (Rúbrica I1 + Seguridad)

Aplicando el principio de **Mínimo Privilegio** visto en la clase de *Seguridad en Agentes de IA* (`seguridad-agentes.pptx`), ningún agente recibe herramientas que no sean estrictamente indispensables para su rol:

### 4.1. Justificación de cada herramienta de Escritura (`edit`) y Ejecución (`execute`)
1. **`especificador` (`tools: ['read', 'search', 'edit']` — SIN `execute`):**
   - **Por qué tiene `edit`:** Necesita escribir su contrato de salida `docs/trabajo/01_especificacion.md` a partir de la plantilla de la skill `sdd-spec-checklist`. Sus instrucciones restringen `edit` exclusivamente a ese archivo, prohibiendo tocar `src/` o `tests/`.
   - **Por qué NO tiene `execute`:** Redactar requisitos y casos de uso es una tarea documental; quitarle `execute` elimina de raíz el riesgo de ejecución de código inesperado (**OWASP `ASI05`**).
2. **`planificador` (`tools: ['read', 'search', 'edit']` — SIN `execute`):**
   - **Por qué tiene `edit`:** Necesita escribir el diseño arquitectónico y la matriz de tareas en `docs/trabajo/02_plan_tareas.md`. Tiene prohibido editar `src/`, `tests/` o la especificación aprobada.
   - **Por qué NO tiene `execute`:** No necesita ejecutar comandos de terminal para planificar la arquitectura.
3. **`implementador` (`tools: ['read', 'search', 'edit', 'execute']`):**
   - **Por qué tiene `edit`:** Es el **único agente de todo el sistema autorizado a escribir código de negocio (`src/`) y pruebas (`tests/`)**, además de su reporte de traspaso `docs/trabajo/03_implementacion.md`.
   - **Por qué tiene `execute`:** Necesita correr la skill `ejecutor-pruebas` (`python -m pytest`) para comprobar que su código compila y pasa las pruebas unitarias antes de entregarlo al revisor. Su uso de `execute` está acotado por una lista blanca estricta de comandos.
4. **`revisor` (`tools: ['read', 'search', 'execute']` — SIN `edit`):**
   - **Por qué NO tiene `edit` (Regla Específica Alternativa A):** Si un agente revisor tiene permiso de edición, tiende a corregir silenciosamente el código o modificar el test que falla en lugar de auditar y reportar el defecto (contaminación de roles). Al quitarle `edit` desde el frontmatter YAML, es imposible que altere `src/` o `tests/`.
   - **Por qué tiene `execute`:** Para que la verificación no sea una opinión subjetiva del LLM (Mitigación **MAST Categoría 3: Verificación de la tarea**), el `revisor` debe ejecutar directamente `verificar_trazabilidad.py` y `ejecutar_suite.py`, generando de forma determinista el archivo auditable `docs/trabajo/04_revision.md`.

### 4.2. Corte de la Trifecta Letal y Mitigación OWASP Top 10 Agéntico (2026)
- **Corte de la Trifecta Letal (Simon Willison, 2025):**
  1. *Sin acceso a datos privados ni secretos de producción:* Ningún agente lee `.env` ni tiene credenciales externas (**mitiga `ASI03` Identity & Privilege Abuse**).
  2. *Sin comunicación externa libre:* Ningún agente tiene la herramienta `web` ni puede ejecutar `curl`, `git push` o llamadas de red hacia el exterior.
  3. *Contratos de traspaso estructurados:* Los archivos en `docs/trabajo/` siguen plantillas cerradas y son auditados por una persona en los Puntos de Control Humano #1 y #2 antes de avanzar (**mitiga `ASI07` Insecure Inter-Agent Communication**, **`ASI08` Cascading Failures** y **`ASI09` Human-Agent Trust Exploitation**).

---

## 5. Diseño y Justificación de las Tres Skills (Rúbrica I2)

Siguiendo el principio de **Divulgación Progresiva en 3 Niveles** (*Nivel 1: Descubrimiento en catálogo*, *Nivel 2: Instrucciones en `SKILL.md`*, *Nivel 3: Recursos ejecutables y plantillas*), creamos tres skills en `.github/skills/` que no duplican las instrucciones de los agentes, sino que encapsulan capacidades reutilizables:

| Skill (`.github/skills/<nombre>/SKILL.md`) | Qué Procedimiento Reutilizable Encapsula | Recurso de Nivel 3 Incluido | Quién la Carga y Cuándo | ¿Por qué es una Skill y NO parte fija de un Agente? |
| :--- | :--- | :--- | :--- | :--- |
| **`sdd-spec-checklist`** | Procedimiento de estructuración y validación de calidad de una especificación SDD (`Given/When/Then`, Caso de Uso, Alcance Negativo y tabla `[NEEDS CLARIFICATION]`). | **Plantilla Markdown:** `templates/plantilla_especificacion.md` | La carga el `especificador` al crear `01_especificacion.md` (y puede usarla el `planificador` para validar la entrada). | Porque la plantilla formal y la lista de chequeo SDD sirven para cualquier nueva funcionalidad futura del proyecto sin inflar permanentemente el prompt base del agente en cada turno. |
| **`verificador-trazabilidad`** | Auditoría automatizada de la matriz de trazabilidad SDD: parsea `01_especificacion.md`, extrae todos los `AC-1..AC-N` y verifica con expresiones regulares que estén citados en `02_plan_tareas.md`, en `tests/*.py` (`# AC-N`) y en `src/*.py` (`# AC-N`), generando el reporte de auditoría. | **Script ejecutable Python:** `scripts/verificar_trazabilidad.py` | La carga el `revisor` durante la auditoría de cada iteración del `implementador`. | Porque un LLM contando apariciones de `# AC-N` a ojo suele cometer alucinaciones; encapsularlo como una skill con un script determinista de Nivel 3 garantiza verificación exacta y reutilizable por cualquier agente o desarrollador. |
| **`ejecutor-pruebas`** | Ejecución controlada de `pytest -v --tb=short`, extracción del estado de cada test, asociación con su criterio `AC-N` y formateo en una tabla Markdown estandarizada. | **Script ejecutable Python:** `scripts/ejecutar_suite.py` | Es una **capacidad compartida**: la usan tanto el `implementador` (al cerrar `03_implementacion.md`) como el `revisor` (al auditar en `04_revision.md`). | Tal como se vio en clase (*"Una skill no es exclusiva de un agente: es una capacidad compartida"*), permite que tanto `implementador` como `revisor` ejecuten y reporten las pruebas con el mismo formato sin duplicar instrucciones en ambos `.agent.md`. |
