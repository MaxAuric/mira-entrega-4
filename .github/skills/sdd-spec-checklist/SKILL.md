---
name: sdd-spec-checklist
description: Estandariza y valida especificaciones bajo Spec-Driven Development (SDD), asegurando historia de usuario con criterios Given/When/Then (AC-N), caso de uso completo, alcance negativo y resolución de ambigüedades [NEEDS CLARIFICATION]. Úsala al redactar o verificar docs/trabajo/01_especificacion.md.
---
# Skill: Estandarización y Lista de Verificación de Especificación SDD

Esta skill encapsula el procedimiento reutilizable de calidad documental para la fase `Specify + Clarify + Checklist` de **Spec-Driven Development (SDD)**.

## 1. Cuándo usar esta skill
- Al iniciar la traducción de una necesidad del cliente en lenguaje natural hacia `docs/trabajo/01_especificacion.md`.
- Antes de solicitar la aprobación del Representante del Cliente en el **Punto de Control Humano #1**.

## 2. Recurso de Nivel 3 asociado
- **Plantilla oficial:** `.github/skills/sdd-spec-checklist/templates/plantilla_especificacion.md`
  Carga y utiliza esta plantilla como estructura base obligatoria al escribir `docs/trabajo/01_especificacion.md`.

## 3. Procedimiento Paso a Paso
1. **Separar comportamiento de implementación:** Verifica que el documento describa *QUÉ* debe ocurrir (entradas, reglas de negocio y salidas observables) sin imponer detalles internos de código.
2. **Registrar aclaraciones (`[NEEDS CLARIFICATION]`):**
   - Toda zona gris del enunciado original debe listarse en la tabla de aclaraciones con su etiqueta `[NEEDS CLARIFICATION]`, la respuesta entregada por el Representante del Cliente y la fuente normativa citada (`POL-DEC v2`, `CAT-SEN v3`, `DOC-MIRA v1.4` o supuesto registrado).
3. **Redactar Criterios de Aceptación (`AC-1` a `AC-N`):**
   - Cada criterio debe tener identificador único (`AC-1`, `AC-2`, ...) y formato `Given` (Dado) / `When` (Cuando) / `Then` (Entonces) con valores concretos verificables en una prueba 1:1.
4. **Completar Caso de Uso y Alcance Negativo:**
   - Incluir Actores, Precondiciones, Flujo Principal, Flujos Alternativos/Excepciones y la sección explícita `Fuera de alcance` para evitar que los siguientes agentes inventen funcionalidades.
5. **Aplicar Checklist de Calidad antes de terminar:**
   - [ ] ¿Todos los criterios tienen formato `Given / When / Then` e ID `AC-N`?
   - [ ] ¿Se incluye el Caso de Uso con actores, precondiciones, flujo principal y excepciones?
   - [ ] ¿Todas las etiquetas `[NEEDS CLARIFICATION]` tienen respuesta del Representante del Cliente?
   - [ ] ¿Está declarada la sección `Fuera de alcance`?
