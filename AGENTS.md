# AGENTS.md · Constitución del Proyecto MIRA (Espejo de `.github/copilot-instructions.md`)

> Este archivo mantiene compatibilidad directa con herramientas basadas en el estándar `AGENTS.md` (Codex, Gemini CLI, Claude Code) y refleja las reglas de `.github/copilot-instructions.md`.

## 1. Contexto de MIRA y Reglas SDD
- **Alternativa:** Alternativa A · Desarrollo Conducido por Especificación (SDD).
- **Stack:** Python 3.12+, FastAPI (`src/`), Pytest (`tests/`).
- **Trazabilidad obligatoria:** Todo criterio de aceptación `AC-1..AC-N` definido en `docs/trabajo/01_especificacion.md` debe estar referenciado en `docs/trabajo/02_plan_tareas.md`, en los comentarios de `tests/` (`# AC-N`) y en la implementación `src/` (`# AC-N`).
- **Archivos de traspaso entre los 4 agentes:**
  1. `especificador` $\rightarrow$ `docs/trabajo/01_especificacion.md` (Requiere aprobación humana en commit propio antes de programar).
  2. `planificador` $\rightarrow$ `docs/trabajo/02_plan_tareas.md` (Requiere revisión humana).
  3. `implementador` $\rightarrow$ `src/`, `tests/` y `docs/trabajo/03_implementacion.md`.
  4. `revisor` (sin herramienta `edit`) $\rightarrow$ `docs/trabajo/04_revision.md` (máximo 2 iteraciones con `implementador`).
