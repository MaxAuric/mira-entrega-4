---
name: ejecutor-pruebas
description: Ejecuta la suite de pruebas automatizadas pytest y resume el estado de cada prueba junto con el criterio AC-N asociado en una tabla Markdown compacta. Úsala cuando el implementador o el revisor necesiten verificar cambios en el código Python.
---
# Skill: Ejecutor y Resumidor de Pruebas Automatizadas (`pytest`)

Esta skill encapsula el procedimiento estándar para correr la suite de pruebas de **MIRA** y presentar su salida en una tabla estructurada sin modificar ningún archivo de código.

## 1. Cuándo usar esta skill
- Cuando el agente `implementador` termina de escribir o corregir código en `src/` y pruebas en `tests/` y debe adjuntar evidencia en `docs/trabajo/03_implementacion.md`.
- Cuando el agente `revisor` necesita confirmar de forma independiente que ningún test existente o nuevo falla.

## 2. Recurso de Nivel 3 (Script Ejecutable)
- **Ruta del script:** `.github/skills/ejecutor-pruebas/scripts/ejecutar_suite.py`

## 3. Procedimiento
1. Ejecuta desde la raíz del proyecto:
   ```bash
   python .github/skills/ejecutor-pruebas/scripts/ejecutar_suite.py
   ```
2. Adjunta la tabla Markdown generada por el script directamente en el archivo de entrega (`docs/trabajo/03_implementacion.md` o `docs/trabajo/04_revision.md`).
3. **Restricción:** No modifiques código fuente ni archivos de prueba desde esta skill, y jamás inventes ni resumas manualmente resultados de `pytest`.
