# Corrida de Línea Base con Un Solo Agente (`docs/linea-base/01_corrida_un_agente.md`)
## Comparación Experimental contra el Sistema Multiagente SDD · Caso MIRA

| Campo | Valor |
| :--- | :--- |
| **Modalidad** | **Línea Base: 1 Solo Agente Generalista** (sin roles separados, sin traspasos en `docs/trabajo/` y sin skills SDD) |
| **Modelo Utilizado** | Google Gemini 3.5 Flash Lite (mismo modelo base usado en el sistema multiagente para comparación justa) |
| **Etiqueta de Partida** | `entrega-3` (commit `33540ec`) |
| **Propósito** | Medir empíricamente qué ocurre cuando el mismo caso de la Alternativa A es resuelto por un único agente en una sola sesión de chat (*Prompt-Driven / Vibe Coding*). |

---

## 1. Prompt Literal Enviado al Agente Único

Se entregó al agente único exactamente el mismo enunciado de negocio del cliente definido en la pauta para la Alternativa A:

```text
Cuando un caso termina de analizarse, necesitamos que MIRA calcule un puntaje y decida sola si lo aprueba, lo deriva a revisión o lo rechaza. Si aparece una señal de fraude, eso manda por sobre todo lo demás. Cada cliente debe poder tener sus propios umbrales. Implementa la lógica en el proyecto y sus pruebas.
```

---

## 2. Qué Hizo el Agente Único (Comportamiento Observado)

Al no contar con el flujo separado de **Especificador (`Specify & Clarify`) $\rightarrow$ Control Humano $\rightarrow$ Planificador $\rightarrow$ Implementador $\rightarrow$ Revisor Independiente**, el agente único exhibió los cuatro síntomas clásicos del *Vibe Coding* descritos en la cátedra de SDD:

1. **Cero detección de ambigüedades (`0` preguntas al Representante del Cliente):**
   - El agente no se detuvo a preguntar cómo se ponderan las señales, qué ocurre si una señal individual cae bajo su mínimo crítico (`POL-DEC v2 §3`), qué pasa si falta una señal (`POL-DEC v2 §6`) o qué pasa cuando `umbral_rechazo >= umbral_aprobacion`.
2. **Relleno silencioso con supuestos erróneos:**
   - **Supuesto no declarado #1:** Calculó el puntaje como un **promedio simple** (`sum(valores) / len(valores)`) en vez de usar los pesos oficiales de MIRA (`PESOS_SENALES` en `src/repository.py`).
   - **Supuesto no declarado #2:** Ignoró los **mínimos obligatorios por señal** (`DOC_AUT >= 70`, `BIO_ROSTRO >= 75`, `CRUCE_MONTO >= 60`, `CRUCE_FECHA >= 60`). Así, un caso con `DOC_AUT = 50` (documento dudoso) pero con las demás señales en `100` obtuvo promedio `87.5` y fue **`APROBADO` erróneamente**, violando `POL-DEC v2 §3`.
   - **Supuesto no declarado #3:** Ante un caso con señales incompletas (por ejemplo, falla el módulo biométrico y no llega `BIO_ROSTRO`), calculó el promedio solo con las señales presentes y lo aprobó con información parcial, violando `POL-DEC v2 §6`.
   - **Supuesto no declarado #4:** Permitió modificar los umbrales de un cliente sin validar que `umbral_rechazo < umbral_aprobacion`, dejando configuraciones inconsistentes.
3. **Ausencia de Artefactos de Ingeniería y Trazabilidad (`0%` de `# AC-N`):**
   - No generó Historia de Usuario con criterios `Given/When/Then`, ni Especificación de Caso de Uso, ni Alcance Negativo, ni Plan de Tareas, ni ningún comentario de trazabilidad `# AC-N` en el código ni en las pruebas.
4. **Autocomplacencia en las Pruebas (*Self-Validation Bias*):**
   - Como el mismo agente escribió el código y sus pruebas en el mismo turno sin un agente `revisor` independiente (sin permiso `edit`), escribió únicamente **3 pruebas felices** diseñadas para pasar con su propio promedio simple (`3/3 passed` según sus propios tests, pero **falla 3 de los 6 criterios de aceptación reales del negocio**).

---

## 3. Evidencia Ejecutable de la Línea Base

El código generado por el agente único fue preservado íntegramente en `docs/linea-base/motor_un_agente_snapshot.py` y auditado con el script ejecutable `docs/linea-base/evaluar_linea_base.py` contra los 6 criterios de aceptación oficiales del cliente (`AC-1` a `AC-6`):

```bash
python docs/linea-base/evaluar_linea_base.py
```

### Resultado de la Auditoría Ejecutable sobre la Línea Base (1 Agente)

| Criterio de Aceptación Oficial del Cliente | Resultado en Línea Base (1 Agente) | Causa Técnica del Resultado en 1 Solo Agente |
| :--- | :---: | :--- |
| **`AC-1`:** Aprobación cuando puntaje ponderado $\ge$ umbral de aprobación del cliente, sin fraude y cumpliendo mínimos | **CUMPLE PARCIAL** | Aprueba casos altos, pero usa promedio simple en lugar de la suma ponderada oficial $\sum V_i \times W_i$. |
| **`AC-2`:** Precedencia absoluta de señal de fraude activa ($\rightarrow$ `RECHAZADO` inmediato aunque el puntaje sea 100) | **CUMPLE** | La regla de fraude estaba explícita en el prompt inicial y el agente único la programó con un `if` directo. |
| **`AC-3`:** Derivación a revisión (`DERIVADO_A_REVISION`) por puntaje intermedio o por **señal individual bajo su mínimo propio** (`POL-DEC v2 §3`) | **FALLA** | **Defecto crítico:** Ignoró `MINIMOS_POR_SENAL`. Con `DOC_AUT=55` (<70) y resto en 95, el agente único devuelve `APROBADO` en vez de `DERIVADO_A_REVISION`. |
| **`AC-4`:** Rechazo cuando puntaje $\le$ umbral de rechazo del cliente, y derivación obligatoria ante **señales faltantes** (`POL-DEC v2 §6`) | **FALLA** | **Defecto crítico:** Si falta `BIO_ROSTRO`, promedia las 3 señales restantes (`90.0`) y devuelve `APROBADO` con información incompleta. |
| **`AC-5`:** Personalización de umbrales por organización cliente (`ORG-01` vs `ORG-02` producen decisiones distintas para el mismo puntaje) | **CUMPLE** | Leyó el diccionario de organizaciones y comparó contra el umbral del cliente. |
| **`AC-6`:** Validación de invariantes al actualizar umbrales de un cliente (`0 <= umbral_rechazo < umbral_aprobacion <= 100` y versionado) | **FALLA** | **Defecto crítico:** Sobrescribe los umbrales sin validar `umbral_rechazo < umbral_aprobacion` ni incrementar la versión auditable. |
