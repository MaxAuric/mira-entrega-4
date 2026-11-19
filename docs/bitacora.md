# Bitácora de Ejecución, Análisis de Fallas MAST y Control Humano (`docs/bitacora.md`)
## Proyecto MIRA · Alternativa A: Desarrollo Conducido por Especificación (SDD)

| Campo | Valor |
| :--- | :--- |
| **Repositorio** | `https://github.com/MaxAuric/mira-entrega-4` |
| **Etiqueta de Partida (Tag)** | `entrega-3` (commit `33540ec`) |
| **Alternativa** | Alternativa A · Desarrollo Conducido por Especificación (SDD) |
| **Herramienta y Modelos** | GitHub Copilot en VS Code v1.99+ (conexión BYOK a Google AI Studio · Custom Agents `.agent.md` + Agent Skills `SKILL.md`) · `gemini-3.5-flash-lite` (500 RPD) y `gemini-3.5-flash` (20 RPD) |
| **Representante del Cliente** | Joaquín Aguilera Arellano *(Rol rotado respecto a la Entrega 2)* |

---

## 1. Registro de Calibración Previa y Análisis de Fallas MAST (Criterio I6)

Durante la validación inicial de los agentes definidos en el commit `6bf3725` (`feat(agents): definir 4 agentes SDD, 3 skills con script nivel 3 y decision arquitectonica`), se identificaron, clasificaron bajo la taxonomía **MAST** (*Multi-Agent System Failure Taxonomy*, Cemri et al., 2025) y corrigieron tres modos de falla en el commit `33540ec` (`fix(agents): corregir fallas MAST...`) antes de congelar la etiqueta base `entrega-3`:

### Falla MAST #1 · Categoría MAST 2: Desalineación entre agentes (*Contexto perdido en el traspaso / Ignorar artefacto compartido*)
- **Archivo y Línea Localizada:** `.github/agents/implementador.agent.md`, **Línea 26** (Sección `# 3. Procedimiento`, paso 1).
- **Síntoma observado en corrida preliminar:** Al invocar al `implementador` en una sesión limpia (contexto aislado ICM), la instrucción genérica `"1. Lee la especificación y el plan de tareas para implementar la solución"` no declaraba las rutas explícitas en `docs/trabajo/` ni exigía verificar que la especificación tuviera el estado `APROBADA POR REPRESENTANTE DEL CLIENTE` sin etiquetas `[NEEDS CLARIFICATION]` abiertas. Como consecuencia, el agente intentaba inferir las reglas desde el prompt del chat y omitía las aclaraciones respondidas por el Representante del Cliente en el archivo.
- **Cambio aplicado (`git diff` en commit `33540ec`):**
  ```diff
  --- a/.github/agents/implementador.agent.md
  +++ b/.github/agents/implementador.agent.md
  @@ -23,7 +23,7 @@
   # 3. Procedimiento
  -1. Lee la especificación y el plan de tareas para implementar la solución.
  +1. **Leer artefactos de traspaso obligatorios:** Lee explícitamente `docs/trabajo/01_especificacion.md` y `docs/trabajo/02_plan_tareas.md`. Verifica que `01_especificacion.md` tenga estado `APROBADA POR REPRESENTANTE DEL CLIENTE` y 0 etiquetas `[NEEDS CLARIFICATION]` pendientes antes de escribir código; si falta esa aprobación, detente de inmediato.
  ```
- **Resultado en nueva ejecución:** Al volver a ejecutar el `implementador`, su primera acción de herramienta (`read`) carga directamente `docs/trabajo/01_especificacion.md` y `docs/trabajo/02_plan_tareas.md`, comprobando la firma del Representante del Cliente y respetando el 100% de las aclaraciones `CL-01` a `CL-03`.

### Falla MAST #2 · Categoría MAST 3: Verificación de la tarea (*Verificación superficial o terminar antes de tiempo*)
- **Archivo y Línea Localizada:** `.github/agents/revisor.agent.md`, **Línea 27** (Sección `# 3. Procedimiento`, paso 3).
- **Síntoma observado en corrida preliminar:** La versión inicial indicaba `"3. Verifica que las pruebas pasen con pytest y que los criterios AC estén cubiertos"` (Ruta 1: esperando que el modelo decidiera por sí solo si cargaba o no la skill `verificador-trazabilidad`). El agente `revisor` ejecutaba solo `pytest -q`, inspeccionaba visualmente el código y emitía un veredicto `APROBADO` prematuro sin detectar que faltaban comentarios obligatorios de trazabilidad (`# AC-N`) en `src/`.
- **Cambio aplicado (`git diff` en commit `33540ec`):**
  ```diff
  --- a/.github/agents/revisor.agent.md
  +++ b/.github/agents/revisor.agent.md
  @@ -24,7 +24,7 @@
   # 3. Procedimiento
   1. **Leer artefactos de entrada:** Lee `docs/trabajo/01_especificacion.md`, `docs/trabajo/02_plan_tareas.md` y `docs/trabajo/03_implementacion.md`.
   2. **Inspeccionar código y pruebas:** Lee `src/models.py`, `src/repository.py`, `src/engine.py`, `src/api.py` y `tests/test_motor_decision.py`.
  -3. Verifica que las pruebas pasen con pytest y que los criterios AC estén cubiertos.
  +3. **Ejecutar auditoría determinista con skills (Ruta 3):** Carga obligatoriamente la skill `verificador-trazabilidad` y ejecuta su script Nivel 3 `python .github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py --reporte docs/trabajo/04_revision.md --iteracion <1|2>`, además de la skill `ejecutor-pruebas` (`python .github/skills/ejecutor-pruebas/scripts/ejecutar_suite.py`). Si el script devuelve código de salida distinto de `0` o falta cualquier comentario `# AC-N` en `src/` o `tests/`, el veredicto debe ser obligatoriamente `RECHAZADO`.
  ```
- **Resultado en nueva ejecución:** Al forzar la **Ruta 3** (invocación explícita de la skill y su script de Nivel 3 desde el procedimiento del agente), el `revisor` ejecuta siempre `verificar_trazabilidad.py`, detectando en la Iteración 1 de la corrida oficial la falta de `# AC-6` y el fallo de umbral igual (`75 == 75`), rechazando correctamente la entrega.

### Falla MAST #3 · Categoría MAST 1: Especificación del sistema (*Falla de descubrimiento Nivel 1 por línea vacía antes del frontmatter*)
- **Archivo y Línea Localizada:** `.github/skills/verificador-trazabilidad/SKILL.md`, **Línea 1**.
- **Síntoma observado:** Un salto de línea vacío en la línea 1 antes del delimitador `---` impedía que VS Code leyera los campos `name` y `description` en el Nivel 1 de descubrimiento. Se eliminó la línea vacía inicial en el commit `33540ec`, restaurando el reconocimiento inmediato de la skill.

---

## 2. Registro Paso a Paso de la Corrida Oficial Entregada (Desde Tag `entrega-3`)

### Resumen Cronológico de Turnos, Carga de Skills y Commits

| Paso | Agente / Actor | Prompt Literal / Acción Ejecutada | Skill Cargada (Evidencia) | Artefacto Escrito / Modificado | ¿Cumplió Contrato? | Commit Asociado |
| :---: | :--- | :--- | :--- | :--- | :---: | :---: |
| **1** | **`especificador`** | `"Actúa como especificador. Analiza la siguiente necesidad del cliente para MIRA y genera docs/trabajo/01_especificacion.md: 'Cuando un caso termina de analizarse, necesitamos que MIRA calcule un puntaje y decida sola si lo aprueba, lo deriva a revisión o lo rechaza. Si aparece una señal de fraude, eso manda por sobre todo lo demás. Cada cliente debe poder tener sus propios umbrales.'"` | **`sdd-spec-checklist`** *(Nivel 2: `SKILL.md` + Nivel 3: `templates/plantilla_especificacion.md`)* | `docs/trabajo/01_especificacion.md` (con 3 dudas `[NEEDS CLARIFICATION]`: `CL-01`, `CL-02`, `CL-03`) | **Sí** | `81ed7cf` |
| **2** | **Control Humano #1 (`PCH-1`: Joaquín Aguilera)** | El Representante del Cliente responde `CL-01` (suma ponderada y derivación por señal faltante `POL-DEC v2 §6`), `CL-02` (precedencia fraude y mínimos individuales `POL-DEC v2 §3`) y `CL-03` ($0 \le U_{\text{rec}} < U_{\text{apr}} \le 100$). Revisa `AC-1..AC-6` y firma `APROBADA POR REPRESENTANTE DEL CLIENTE` en **commit propio exclusivo**. | *(Revisión con checklist de `sdd-spec-checklist`)* | `docs/trabajo/01_especificacion.md` (Estado: `APROBADA`) | **Sí (Control Humano #1)** | **`81ed7cf`** *(Commit exclusivo de spec)* |
| **3** | **`planificador`** | *Handoff (`send: false`) aprobado:* `"Lee la especificación aprobada en docs/trabajo/01_especificacion.md y genera el plan de diseño y tareas en docs/trabajo/02_plan_tareas.md."` | *(Valida estructura contra `sdd-spec-checklist`)* | `docs/trabajo/02_plan_tareas.md` (Arquitectura, contratos, tareas `T-01..T-06` y matriz `AC-1..AC-6`) | **Sí** | `115651b` |
| **4** | **Control Humano #2 (`PCH-2`: Equipo)** | Revisión humana de los contratos JSON de los endpoints REST (`POST /api/casos/evaluar` y `PUT /api/organizaciones/{org_id}/umbrales`) y verificación de cobertura 1:1 de `AC-1..AC-6`. Se aprueba el traspaso al `implementador`. | — | `docs/trabajo/02_plan_tareas.md` (Sección 5: `PLAN APROBADO`) | **Sí (Control Humano #2)** | **`115651b`** |
| **5** | **`implementador` (Iteración 1)** | *Handoff (`send: false`) aprobado:* `"Implementa las tareas definidas en docs/trabajo/02_plan_tareas.md respetando la especificación docs/trabajo/01_especificacion.md y registra tu entrega en docs/trabajo/03_implementacion.md."` | **`ejecutor-pruebas`** *(Nivel 2: `SKILL.md` + Nivel 3: `scripts/ejecutar_suite.py`)* | `src/models.py`, `src/repository.py`, `src/engine.py`, `src/api.py`, `tests/test_motor_decision.py`, `docs/trabajo/03_implementacion.md` | **Parcial** *(15/16 tests pasan; defecto en `AC-6`)* | `1677aec` |
| **6** | **`revisor` (Iteración 1 — RECHAZO)** | *Handoff a revisión:* `"Audita la implementación documentada en docs/trabajo/03_implementacion.md contra docs/trabajo/01_especificacion.md y docs/trabajo/02_plan_tareas.md usando las skills verificador-trazabilidad y ejecutor-pruebas."` | **`verificador-trazabilidad`** (`verificar_trazabilidad.py --iteracion 1`) + **`ejecutor-pruebas`** | `docs/trabajo/04_revision.md` (**`Veredicto: RECHAZADO`** — detecta falta de `# AC-6` en `src/` y error `>` vs `>=` cuando `75.0 == 75.0`) | **Sí (Detecta y rechaza salida defectuosa)** | **`1677aec`** |
| **7** | **`implementador` (Iteración 2 — Corrección)** | *Handoff de devolución (`send: false`):* `"Corrige los hallazgos detallados en docs/trabajo/04_revision.md (respetando el límite máximo de 2 iteraciones) y actualiza docs/trabajo/03_implementacion.md."` | **`ejecutor-pruebas`** (`scripts/ejecutar_suite.py` $\rightarrow$ `16/16 PASSED`) | `src/repository.py` (`umbral_rechazo >= umbral_aprobacion # AC-6`), `src/api.py` (`# AC-6`), `docs/trabajo/03_implementacion.md` | **Sí (100% corregido)** | `28388d4` |
| **8** | **`revisor` (Iteración 2 — APROBADO)** | *Re-auditoría de cierre:* `"Verifica la Iteración 2 ejecutando verificar_trazabilidad.py --reporte docs/trabajo/04_revision.md --iteracion 2."` | **`verificador-trazabilidad`** (`verificar_trazabilidad.py --iteracion 2` $\rightarrow$ `exit code 0`) + **`ejecutor-pruebas`** | `docs/trabajo/04_revision.md` (**`Veredicto Oficial: APROBADO`**, `6/6 AC-N OK`, `16/16 tests PASSED`) | **Sí (Criterio de término cumplido)** | **`28388d4`** |

---

## 3. Evidencia de Carga y Uso de las Tres Skills en la Corrida Entregada (Rúbrica I2)

1. **Skill 1 (`sdd-spec-checklist`):**
   - **Cuándo se cargó:** En el Paso 1 por el agente `especificador`.
   - **Recurso Nivel 3 utilizado:** `.github/skills/sdd-spec-checklist/templates/plantilla_especificacion.md`.
   - **Evidencia:** El archivo `docs/trabajo/01_especificacion.md` sigue exactamente las 6 secciones de la plantilla e incluye en su Sección 6 la lista de chequeo completada.
2. **Skill 2 (`verificador-trazabilidad`):**
   - **Cuándo se cargó:** En el Paso 6 (Iteración 1 $\rightarrow$ código de salida `1`, `RECHAZADO`) y en el Paso 8 (Iteración 2 $\rightarrow$ código de salida `0`, `APROBADO`) por el agente `revisor`.
   - **Recurso Nivel 3 utilizado:** `.github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py`.
   - **Evidencia:** Generó automáticamente la matriz de trazabilidad con números de línea exactos en `docs/trabajo/04_revision.md` sin que el `revisor` tuviera la herramienta `edit`.
3. **Skill 3 (`ejecutor-pruebas`):**
   - **Cuándo se cargó:** En el Paso 5 (`15/16 passed, 1 failed`) y en el Paso 7 (`16/16 passed, 0 failed`) por el `implementador`, y verificada por el `revisor`.
   - **Recurso Nivel 3 utilizado:** `.github/skills/ejecutor-pruebas/scripts/ejecutar_suite.py`.
   - **Evidencia:** Tabla Markdown de las 16 pruebas adjunta en la Sección 3 de `docs/trabajo/03_implementacion.md`.
