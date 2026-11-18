---
name: verificador-trazabilidad
description: Ejecuta un script de Nivel 3 en Python que audita la trazabilidad SDD 1:1 de todos los criterios de aceptación AC-N entre la especificación (01_especificacion.md), el plan (02_plan_tareas.md), las pruebas (tests/) y el código fuente (src/). Úsala durante la revisión de calidad o antes de cerrar una iteración de implementación.
---
# Skill: Verificador Automatizado de Trazabilidad SDD (`AC-N`)

Esta skill encapsula un procedimiento ejecutable de **Nivel 3** para verificar sin intervención manual que cada criterio de aceptación (`AC-1..AC-N`) definido en la especificación SDD esté trazado en el plan de tareas, en los comentarios de las pruebas unitarias (`tests/`) y en la implementación (`src/`).

## 1. Cuándo usar esta skill
- Cuando el agente `revisor` audita la entrega del `implementador` para comprobar el cumplimiento de la regla SDD de trazabilidad obligatoria.
- Cuando se requiere generar o actualizar la matriz auditable en `docs/trabajo/04_revision.md` sin usar la herramienta `edit`.

## 2. Recurso de Nivel 3 (Script Ejecutable)
- **Ruta del script:** `.github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py`

## 3. Procedimiento de Ejecución
1. Ejecuta el script desde la raíz del repositorio:
   ```bash
   python .github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py
   ```
2. Para generar además el reporte auditable en `docs/trabajo/04_revision.md`, ejecuta:
   ```bash
   python .github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py --reporte docs/trabajo/04_revision.md --iteracion 1
   ```
3. **Interpretación del resultado:**
   - **Código de salida `0` (`VEREDICTO: APROBADO`):** Todos los criterios `AC-N` de la especificación aparecen en el plan, en `tests/` (`# AC-N`) y en `src/` (`# AC-N`), y todas las pruebas de `pytest` pasan en verde.
   - **Código de salida `1` (`VEREDICTO: RECHAZADO`):** Falta al menos un comentario de trazabilidad `# AC-N` en `src/` o `tests/`, o alguna prueba de `pytest` falló. El agente `revisor` debe rechazar la entrega y devolverla al `implementador`.
