# Reporte de Implementación SDD (`docs/trabajo/03_implementacion.md`)
## Iteración 1 de 2 · Agente `implementador`

| Campo | Valor |
| :--- | :--- |
| **Agente Autor** | `implementador` (`.github/agents/implementador.agent.md`) |
| **Iteración** | `Iteración 1` (Primera entrega al agente `revisor`) |
| **Artefactos de Entrada Leídos** | `docs/trabajo/01_especificacion.md` (`APROBADA`) y `docs/trabajo/02_plan_tareas.md` (`PLAN APROBADO`) |
| **Skill Cargada** | `ejecutor-pruebas` (`.github/skills/ejecutor-pruebas/SKILL.md` + `scripts/ejecutar_suite.py`) |

---

## 1. Archivos Creados y Modificados en `Iteración 1`

1. **`src/models.py`**: Se incorporó el modelo `ActualizacionUmbralesInput` para el endpoint `PUT /api/organizaciones/{org_id}/umbrales`.
2. **`src/repository.py`**: Se implementó `actualizar_umbrales_organizacion` con validación de rango `[0.0, 100.0]` e incremento de `version`.
3. **`src/engine.py`**: Se implementó `evaluar_caso(caso: CasoEntrada) -> ResultadoDecision` respetando la suma ponderada (`# AC-1`), la precedencia absoluta de señal de fraude (`# AC-2`), los mínimos individuales por señal (`# AC-3`), la derivación por señales faltantes (`# AC-4`) y el aislamiento por organización cliente (`# AC-5`).
4. **`src/api.py`**: Se expusieron los endpoints `POST /api/casos/evaluar` y `PUT /api/organizaciones/{org_id}/umbrales`.
5. **`tests/test_motor_decision.py`**: Se implementaron 12 pruebas unitarias y de integración (`TestClient`) mapeadas a `AC-1..AC-6`.

---

## 2. Mapeo de Implementación por Criterio (`AC-1` a `AC-6`)

| Criterio | Archivo y Función de Código | Archivo y Función de Prueba |
| :--- | :--- | :--- |
| **`AC-1`** | `src/engine.py::evaluar_caso`, `src/api.py::evaluar_caso_endpoint` | `tests/test_motor_decision.py::test_ac1_aprobacion_puntaje_ponderado`, `test_ac1_endpoint_evaluar_aprobado` |
| **`AC-2`** | `src/engine.py::evaluar_caso`, `src/api.py::evaluar_caso_endpoint` | `tests/test_motor_decision.py::test_ac2_precedencia_fraude_sobre_puntaje_alto`, `test_ac2_senal_fraude_desconocida_error` |
| **`AC-3`** | `src/engine.py::evaluar_caso` | `tests/test_motor_decision.py::test_ac3_derivacion_rango_intermedio`, `test_ac3_derivacion_senal_bajo_minimo_aunque_puntaje_alto` |
| **`AC-4`** | `src/engine.py::evaluar_caso` | `tests/test_motor_decision.py::test_ac4_rechazo_puntaje_bajo_umbral`, `test_ac4_derivacion_obligatoria_senal_faltante` |
| **`AC-5`** | `src/repository.py::obtener_umbrales_organizacion`, `src/engine.py::evaluar_caso` | `tests/test_motor_decision.py::test_ac5_umbrales_propios_por_cliente_mismo_puntaje`, `test_ac5_organizacion_inexistente_404` |
| **`AC-6`** | `src/repository.py::actualizar_umbrales_organizacion`, `src/api.py::actualizar_umbrales_endpoint` | `tests/test_motor_decision.py::test_ac6_actualizar_umbrales_valido_incrementa_version`, `test_ac6_actualizar_umbrales_iguales_o_invertidos_400` |

---

## 3. Salida de la Skill `ejecutor-pruebas` en Iteración 1

| Prueba Unitaria | Archivo | Criterio Cubierto | Resultado |
| :--- | :--- | :---: | :---: |
| `test_pesos_senales_suman_uno` | `tests/test_base_mira.py` | `Base MIRA` | **PASSED** |
| `test_minimos_y_catalogo_fraude_definidos` | `tests/test_base_mira.py` | `Base MIRA` | **PASSED** |
| `test_obtener_umbrales_organizacion_existente` | `tests/test_base_mira.py` | `Base MIRA` | **PASSED** |
| `test_endpoint_health_y_organizaciones` | `tests/test_base_mira.py` | `Base MIRA` | **PASSED** |
| `test_ac1_aprobacion_puntaje_ponderado` | `tests/test_motor_decision.py` | `AC-1` | **PASSED** |
| `test_ac1_endpoint_evaluar_aprobado` | `tests/test_motor_decision.py` | `AC-1` | **PASSED** |
| `test_ac2_precedencia_fraude_sobre_puntaje_alto` | `tests/test_motor_decision.py` | `AC-2` | **PASSED** |
| `test_ac2_senal_fraude_desconocida_error` | `tests/test_motor_decision.py` | `AC-2` | **PASSED** |
| `test_ac3_derivacion_rango_intermedio` | `tests/test_motor_decision.py` | `AC-3` | **PASSED** |
| `test_ac3_derivacion_senal_bajo_minimo_aunque_puntaje_alto` | `tests/test_motor_decision.py` | `AC-3` | **PASSED** |
| `test_ac4_rechazo_puntaje_bajo_umbral` | `tests/test_motor_decision.py` | `AC-4` | **PASSED** |
| `test_ac4_derivacion_obligatoria_senal_faltante` | `tests/test_motor_decision.py` | `AC-4` | **PASSED** |
| `test_ac5_umbrales_propios_por_cliente_mismo_puntaje` | `tests/test_motor_decision.py` | `AC-5` | **PASSED** |
| `test_ac5_organizacion_inexistente_404` | `tests/test_motor_decision.py` | `AC-5` | **PASSED** |
| `test_ac6_actualizar_umbrales_valido_incrementa_version` | `tests/test_motor_decision.py` | `AC-6` | **PASSED** |
| `test_ac6_actualizar_umbrales_iguales_o_invertidos_400` | `tests/test_motor_decision.py` | `AC-6` | **FAILED** |

**Estado de Traspaso:** Se envía la Iteración 1 al agente `revisor` para su auditoría formal en `docs/trabajo/04_revision.md`.
