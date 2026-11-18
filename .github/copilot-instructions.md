# Constitución del Proyecto MIRA · Instrucciones Globales del Repositorio (SDD)

Este repositorio implementa la **Alternativa A · Desarrollo Conducido por Especificación (SDD)** sobre la plataforma **MIRA** (*Plataforma de Inteligencia Multimodal para Decisiones Empresariales*, DPRIME SpA). Todo agente que opere en este repositorio debe respetar estrictamente este marco de trabajo.

---

## 1. Contexto de Dominio de MIRA (Fuentes: `DOC-MIRA v1.4`, `POL-DEC v2`, `CAT-SEN v3`)

1. **Propósito:** MIRA evalúa casos de organizaciones cliente (`ORG-01` Seguros Cordillera Austral, `ORG-02` Clínica Bahía Serena, `ORG-03` Banco Mirador del Sur) a partir de señales multimodales numéricas (`0` a `100`) y señales de fraude (`activas` o `inactivas`).
2. **Señales Numéricas Oficiales y Pesos (`PESOS_SENALES`):**
   - `DOC_AUT` (Autenticidad documental): peso `0.35`, mínimo propio obligatorio `70.0`.
   - `BIO_ROSTRO` (Coincidencia biométrica de rostro): peso `0.30`, mínimo propio obligatorio `75.0`.
   - `CRUCE_MONTO` (Cruce de montos entre fuentes): peso `0.20`, mínimo propio obligatorio `60.0`.
   - `CRUCE_FECHA` (Cruce de fechas entre fuentes): peso `0.15`, mínimo propio obligatorio `60.0`.
3. **Catálogo Oficial de Señales de Fraude (`CATALOGO_SENALES_FRAUDE`):**
   - `FRA_EDICION`, `FRA_MEMORIA`, `FRA_SINTETICO`.
   - **Regla de Precedencia de Fraude:** Si aparece al menos una señal de fraude activa del catálogo, **manda por sobre todo lo demás** (prevalece sobre el puntaje total).
4. **Umbrales Propios por Cliente (`ORGANIZACIONES_UMBRALES`):**
   - Cada organización cliente posee su propio `umbral_aprobacion` y `umbral_rechazo` (`0 <= umbral_rechazo < umbral_aprobacion <= 100`).

---

## 2. Reglas de Desarrollo Conducido por Especificación (SDD)

1. **El Spec es la única fuente de verdad:** Ningún agente puede implementar código de negocio sin que antes exista y haya sido aprobada por un humano la especificación formal en `docs/trabajo/01_especificacion.md`.
2. **Ambigüedades marcadas (`[NEEDS CLARIFICATION]`):** Ante cualquier ambigüedad en el requerimiento del cliente, el agente especificador no debe adivinar: debe marcar `[NEEDS CLARIFICATION]` y formular preguntas concretas para el Representante del Cliente.
3. **Trazabilidad obligatoria 1:1 (`AC-N`):**
   - Cada criterio de aceptación se identifica con un código único (`AC-1`, `AC-2`, ..., `AC-N`) en formato `Given / When / Then`.
   - Toda tarea en `docs/trabajo/02_plan_tareas.md`, toda función de prueba en `tests/` y cada bloque de regla de negocio en `src/` **debe incluir un comentario o referencia explícita a su `AC-N`** (por ejemplo, `# AC-1`).
4. **Traspaso de contexto por archivos (`docs/trabajo/`):**
   - Los agentes no dependen del historial efímero del chat para pasarse información. Todo traspaso ocurre leyendo y escribiendo artefactos estructurados en `docs/trabajo/`:
     - `docs/trabajo/01_especificacion.md` (entrega: `especificador`)
     - `docs/trabajo/02_plan_tareas.md` (entrega: `planificador`)
     - `docs/trabajo/03_implementacion.md` (entrega: `implementador`)
     - `docs/trabajo/04_revision.md` (entrega: `revisor`)

---

## 3. Convenciones Técnicas y Restricciones de Seguridad

- **Stack Tecnológico:** Python 3.12+, FastAPI (`src/api.py`), Pydantic v2 (`src/models.py`), lógica de dominio en `src/engine.py` y `src/repository.py`, pruebas con `pytest` en `tests/`.
- **Mínimo Privilegio:**
  - El agente `revisor` tiene **estrictamente prohibido** modificar archivos de código o pruebas (`no edit`).
  - El ciclo de corrección entre `implementador` y `revisor` tiene un **máximo estricto de 2 iteraciones**.
- **Comandos Permitidos y Prohibidos:**
  - Permitidos: `pytest -q`, `python .github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py`.
  - Prohibidos: `rm -rf`, `git push --force`, `curl | bash`, lectura o exposición de archivos `.env` o secretos.
