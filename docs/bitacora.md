# Bitácora de Ejecución, Análisis de Fallas MAST y Control Humano (`docs/bitacora.md`)
## Proyecto MIRA · Alternativa A: Desarrollo Conducido por Especificación (SDD)

| Campo | Valor |
| :--- | :--- |
| **Repositorio** | `https://github.com/MaxAuric/mira-entrega-4` |
| **Etiqueta de Partida (Tag)** | `entrega-3` |
| **Alternativa** | Alternativa A · Desarrollo Conducido por Especificación (SDD) |
| **Herramienta y Modelos** | VS Code v1.99+ (Custom Agents `.agent.md` + Agent Skills `SKILL.md`) · Gemini 3.5 Flash Lite / Flash |
| **Representante del Cliente** | Joaquín Aguilera Arellano (Rol rotado respecto a la Entrega 2) |

---

## 1. Registro de Calibración Previa y Análisis de Fallas MAST (Criterio I6)

Durante la validación inicial de los agentes definidos en el commit `6bf3725` (`feat(agents): definir 4 agentes SDD, 3 skills con script nivel 3 y decision arquitectonica`), se identificaron, clasificaron bajo la taxonomía **MAST** (*Multi-Agent System Failure Taxonomy*, Cemri et al., 2025) y corrigieron tres modos de falla antes de congelar la etiqueta base `entrega-3`:

### Falla MAST #1 · Categoría MAST 2: Desalineación entre agentes (*Contexto perdido en el traspaso / Ignorar artefacto compartido*)
- **Archivo y Línea Localizada:** `.github/agents/implementador.agent.md`, **Línea 26** (Sección `# 3. Procedimiento`, paso 1).
- **Síntoma observado en corrida preliminar:** Al invocar al `implementador` en una sesión limpia (contexto aislado ICM), la instrucción genérica `"1. Lee la especificación y el plan de tareas para implementar la solución"` no declaraba las rutas explícitas en `docs/trabajo/` ni exigía verificar que la especificación tuviera el estado `APROBADA POR REPRESENTANTE DEL CLIENTE` sin etiquetas `[NEEDS CLARIFICATION]` abiertas. Como consecuencia, el agente intentaba inferir las reglas desde el prompt del chat y omitía las aclaraciones respondidas por el Representante del Cliente en el archivo.
- **Cambio aplicado (`git diff`):**
  ```diff
  --- a/.github/agents/implementador.agent.md
  +++ b/.github/agents/implementador.agent.md
  @@ -23,7 +23,7 @@
   # 3. Procedimiento
  -1. Lee la especificación y el plan de tareas para implementar la solución.
  +1. **Leer artefactos de traspaso obligatorios:** Lee explícitamente `docs/trabajo/01_especificacion.md` y `docs/trabajo/02_plan_tareas.md`. Verifica que `01_especificacion.md` tenga estado `APROBADA POR REPRESENTANTE DEL CLIENTE` y 0 etiquetas `[NEEDS CLARIFICATION]` pendientes antes de escribir código; si falta esa aprobación, detente de inmediato.
  ```
- **Resultado en nueva ejecución:** Al volver a ejecutar el `implementador`, su primera acción de herramienta (`read`) carga directamente `docs/trabajo/01_especificacion.md` y `docs/trabajo/02_plan_tareas.md`, comprobando la firma del Representante del Cliente y respetando el 100% de las aclaraciones `CL-01` a `CL-03`.

---

### Falla MAST #2 · Categoría MAST 3: Verificación de la tarea (*Verificación superficial o terminar antes de tiempo*)
- **Archivo y Línea Localizada:** `.github/agents/revisor.agent.md`, **Línea 27** (Sección `# 3. Procedimiento`, paso 3).
- **Síntoma observado en corrida preliminar:** La versión inicial indicaba `"3. Verifica que las pruebas pasen con pytest y que los criterios AC estén cubiertos"` (Ruta 1: esperando que el modelo decidiera por sí solo si cargaba o no la skill `verificador-trazabilidad`). El agente `revisor` ejecutaba solo `pytest -q`, inspeccionaba visualmente el código y emitía un veredicto `APROBADO` prematuro sin detectar que faltaban comentarios obligatorios de trazabilidad (`# AC-4` y `# AC-5`) en `src/engine.py`.
- **Cambio aplicado (`git diff`):**
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
- **Resultado en nueva ejecución:** Al forzar la **Ruta 3** (invocación explícita de la skill y su script de Nivel 3 desde el procedimiento del agente), el `revisor` ejecuta siempre `verificar_trazabilidad.py`, detectando cualquier `# AC-N` faltante con código de salida `1` y rechazando la entrega hasta que la trazabilidad sea del 100%.

---

### Falla MAST #3 · Categoría MAST 1: Especificación del sistema (*Falla de descubrimiento Nivel 1 por línea vacía antes del frontmatter*)
- **Archivo y Línea Localizada:** `.github/skills/verificador-trazabilidad/SKILL.md`, **Línea 1**.
- **Síntoma observado:** Durante la edición manual de `.github/skills/verificador-trazabilidad/SKILL.md`, se introdujo un salto de línea en blanco en la línea 1 antes del delimitador `---`. Tal como se advirtió en clases (*Pauta de revisión cruzada*: *"El archivo empieza con `---` en la línea 1; una línea vacía antes impide leer el frontmatter"*), el parser de VS Code ignoraba los campos `name` y `description` en el Nivel 1 de descubrimiento.
- **Cambio aplicado (`git diff`):**
  ```diff
  --- a/.github/skills/verificador-trazabilidad/SKILL.md
  +++ b/.github/skills/verificador-trazabilidad/SKILL.md
  @@ -1,4 +1,3 @@
  -
   ---
   name: verificador-trazabilidad
   description: Ejecuta un script de Nivel 3 en Python que audita la trazabilidad SDD 1:1 de todos los criterios de aceptación AC-N...
  ```
- **Resultado en nueva ejecución:** El frontmatter YAML es reconocido inmediatamente desde la línea 1 en el catálogo de skills de VS Code.

---

## 2. Registro de la Corrida Oficial Entregada (Se completará en Fase 4)

*(Esta sección registrará paso a paso los prompts literales, la carga de las 3 skills, las decisiones humanas en PCH-1 y PCH-2 y el ciclo de rechazo/corrección entre implementador y revisor).*
