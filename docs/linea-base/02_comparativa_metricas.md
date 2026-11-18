# Comparativa Cuantitativa: Línea Base (1 Agente) vs. Sistema Multiagente SDD (`docs/linea-base/02_comparativa_metricas.md`)
## Sección 5.3 y 6.5 de la Pauta · Evaluación de Utilidad y Costo-Beneficio

Este documento consolida las métricas empíricas obtenidas al resolver exactamente el mismo caso de negocio de la **Alternativa A** sobre **MIRA** mediante dos enfoques:
1. **Línea Base (`1 Solo Agente`):** Un agente generalista en una sola sesión de chat (*Prompt-Driven / Vibe Coding*).
2. **Sistema Multiagente SDD (`4 Agentes + 3 Skills`):** Flujo `especificador` $\rightarrow$ `[Control Humano #1]` $\rightarrow$ `planificador` $\rightarrow$ `[Control Humano #2]` $\rightarrow$ `implementador` $\leftrightarrow$ `revisor` (con scripts ejecutables Nivel 3).

---

## 1. Tabla Comparativa en Todas las Métricas (Rúbrica I5)

| Métrica Evaluada | Línea Base (1 Solo Agente) | Sistema Multiagente SDD (4 Agentes + 3 Skills) | Diferencia / Comparación | ¿A quién favorece? |
| :--- | :---: | :---: | :---: | :---: |
| **1. Solicitudes al modelo (Requests / Prompts)** | **2 requests** (1 prompt inicial + 1 ajuste menor) | **7 requests** (1 especificador + 1 aclaración + 1 planificador + 2 implementador + 2 revisor) | $+5\text{ requests}$ ($3,5\times$ más llamadas) | **Favorece a 1 Solo Agente** *(menor consumo de cuota diaria RPD)* |
| **2. Consumo total estimado de Tokens (Entrada + Salida)** | **$\approx 3.850\text{ tokens}$** | **$\approx 13.200\text{ tokens}$** | $+9.350\text{ tokens}$ ($\approx 3,43\times$ más tokens) | **Favorece a 1 Solo Agente** *(más económico en tokens)* |
| **3. Tiempo total de ejecución extremo a extremo** | **$\approx 1\text{ min } 45\text{ s}$** | **$\approx 8\text{ min } 20\text{ s}$** *(incluyendo 2 controles humanos y 1 ciclo de rechazo/corrección)* | $+6\text{ min } 35\text{ s}$ ($4,76\times$ más lento) | **Favorece a 1 Solo Agente** *(mucha menor latencia)* |
| **4. Ambigüedades detectadas antes de programar (`[NEEDS CLARIFICATION]`)** | **0 de 3 (0,0%)** *(asumió promedio simple e ignoró mínimos y señales faltantes)* | **3 de 3 (100,0%)** *(detectó fórmula ponderada, mínimos/faltantes `POL-DEC v2` e invariante de umbrales)* | $+3\text{ ambigüedades críticas resueltas con el cliente}$ | **Favorece al Sistema Multiagente** *(evita programar supuestos falsos)* |
| **5. Criterios de aceptación reales del negocio cumplidos (`AC-1` a `AC-6`)** | **2 de 6 estrictos (33,3%)** *(falla en `AC-1` ponderado, `AC-3` mínimo por señal, `AC-4` señal faltante y `AC-6` invariante)* | **6 de 6 estrictos (100,0%)** *(todos verificados con casos de borde en `pytest`)* | $+66,7\text{ puntos porcentuales}$ en fidelidad funcional | **Favorece al Sistema Multiagente** *(calidad verificable)* |
| **6. Trazabilidad obligatoria 1:1 (`# AC-N` en Plan, Tests y Código)** | **0 de 6 (0,0%)** *(sin artefactos en `docs/trabajo/` ni comentarios `# AC-N`)* | **6 de 6 (100,0%)** *(auditado con código `0` por `verificar_trazabilidad.py`)* | $+100\%\text{ de trazabilidad auditable}$ | **Favorece al Sistema Multiagente** *(mantenibilidad SDD)* |
| **7. Pruebas automatizadas generadas y casos de borde cubiertos** | **3 pruebas básicas** *(solo caminos felices autocomplacientes)* | **12 pruebas del motor + 4 pruebas base (16 tests en total)** *(incluye fraude, mínimos, faltantes, API y errores 400/404)* | $+13\text{ pruebas automatizadas}$ | **Favorece al Sistema Multiagente** *(separación implementador vs. revisor)* |
| **8. Defectos silenciosos que llegaron al cierre sin ser detectados** | **4 defectos de negocio** *(no detectados porque el mismo agente escribió el código y sus 3 tests)* | **0 defectos al cierre** *(1 brecha en Iteración 1 fue detectada y rechazada por `revisor` y corregida en Iteración 2)* | $-4\text{ defectos escapados a producción}$ | **Favorece al Sistema Multiagente** *(verificación independiente)* |

---

## 2. Interpretación Honesta Apoyada en los Números (Sin Maquillar Resultados Desfavorables)

### 2.1. Dónde el Sistema Multiagente NO compensó su costo (Conclusiones Desfavorables)
1. **Sobrecosto de Tokens ($\approx 3,43\times$) y Cuota Diaria (RPD):**
   - Resolver la funcionalidad con 4 agentes consumió **13.200 tokens y 7 turnos/requests** frente a solo **3.850 tokens y 2 requests** del agente único. En un entorno con cuota diaria restringida (como modelos *Flash* de 20 RPD), un flujo multiagente con ciclos de revisión agota el presupuesto rápidamente si la tarea es pequeña.
2. **Latencia Humana y Tiempo de Ciclo ($4,76\times$ más lento):**
   - Mientras el agente único entregó código funcionando en **1 minuto y 45 segundos**, el sistema multiagente tomó **8 minutos y 20 segundos**. El cuello de botella no fue la inferencia del LLM, sino los **dos Puntos de Control Humano (`send: false`)** y la escritura/lectura de cuatro archivos intermedios en `docs/trabajo/`. Para un cambio trivial o un prototipo exploratorio (como se vio en la lámina 19 de la clase de SDD: *"Prototipo desechable de una tarde o script de un solo uso"*), **el sistema de 4 agentes es excesivo y no compensa su costo operativo**.

### 2.2. Dónde el Sistema Multiagente SÍ aportó valor decisivo
1. **Eliminación de Supuestos Silenciosos (*Spec-Driven* vs. *Vibe Coding*):**
   - El enunciado original del cliente tenía tres zonas grises deliberadas: no especificaba los pesos de las señales, ni qué hacer si una señal individual caía bajo su mínimo (`POL-DEC v2 §3`) o faltaba (`POL-DEC v2 §6`), ni las restricciones al editar umbrales. El **agente único no preguntó nada (`0/3`)** y programó un promedio aritmético simple que **aprobaba casos con autenticidad documental reprobada (`DOC_AUT = 55 < 70`)**. En cambio, el agente `especificador` con la skill `sdd-spec-checklist` detuvo el flujo, marcó tres bloques `[NEEDS CLARIFICATION]` y obligó al Representante del Cliente a definir la regla exacta antes de escribir una sola línea de código (`3/3`).
2. **Ruptura del Sesgo de Autocomplacencia mediante el Agente `revisor` sin `edit`:**
   - En la línea base, el agente único escribió código defectuoso y creó 3 pruebas que validaban su propio error, reportando engañosamente `"100% tests passing"`. En el sistema multiagente, al separar al `implementador` del `revisor` (quien carece de la herramienta `edit` y está obligado a correr el script de Nivel 3 `verificar_trazabilidad.py`), se detectó y rechazó en la Iteración 1 una omisión real antes de dar por cerrado el caso, alcanzando un **100% (6/6)** en los criterios reales del negocio frente al **33,3% (2/6)** del agente único.
