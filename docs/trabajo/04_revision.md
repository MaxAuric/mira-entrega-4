# Reporte de Revisión y Auditoría SDD · Iteración 1 de 2

| Campo | Valor |
| :--- | :--- |
| **Agente Auditor** | `revisor` (`.github/agents/revisor.agent.md`) |
| **Skill Ejecutada** | `verificador-trazabilidad` (Recurso Nivel 3: `verificar_trazabilidad.py`) |
| **Iteración del Ciclo** | `1 / 2` (Máximo declarado: 2 iteraciones) |
| **Veredicto Oficial** | **`RECHAZADO`** |

---

## 1. Matriz de Trazabilidad 1:1 (`AC-N`)

| Criterio | En Especificación | En Plan (`02_plan_tareas.md`) | En Pruebas (`tests/`) | En Código (`src/`) | Estado |
| :--- | :---: | :---: | :--- | :--- | :---: |
| **`AC-1`** | SI | SI | `tests/test_motor_decision.py:18, tests/test_motor_decision.py:31, tests/test_motor_decision.py:38` | `src/api.py:59, src/api.py:61, src/engine.py:32, src/engine.py:40, src/engine.py:42, src/engine.py:105, src/engine.py:106` | **OK** |
| **`AC-2`** | SI | SI | `tests/test_motor_decision.py:60, tests/test_motor_decision.py:73, tests/test_motor_decision.py:80` | `src/api.py:61, src/engine.py:27, src/engine.py:29, src/engine.py:54, src/engine.py:55, src/engine.py:61` | **OK** |
| **`AC-3`** | SI | SI | `tests/test_motor_decision.py:99, tests/test_motor_decision.py:112, tests/test_motor_decision.py:118, tests/test_motor_decision.py:131` | `src/api.py:61, src/engine.py:52, src/engine.py:88, src/engine.py:89, src/engine.py:95, src/engine.py:105, src/engine.py:118` | **OK** |
| **`AC-4`** | SI | SI | `tests/test_motor_decision.py:137, tests/test_motor_decision.py:164, tests/test_motor_decision.py:169, tests/test_motor_decision.py:181` | `src/api.py:61, src/engine.py:47, src/engine.py:71, src/engine.py:72, src/engine.py:78, src/engine.py:105, src/engine.py:112` | **OK** |
| **`AC-5`** | SI | SI | `tests/test_motor_decision.py:186, tests/test_motor_decision.py:194, tests/test_motor_decision.py:195, tests/test_motor_decision.py:202` | `src/api.py:33, src/api.py:35, src/api.py:59, src/api.py:61, src/engine.py:24, src/engine.py:25, src/engine.py:105, src/repository.py:60, src/repository.py:62, src/repository.py:72` | **OK** |
| **`AC-6`** | SI | SI | `tests/test_motor_decision.py:208, tests/test_motor_decision.py:222` | `FALTA` | **INCUMPLE** |

---

## 2. Resultado de Verificación Ejecutable (`pytest -q`)

```text
...............F                                                         [100%]
================================== FAILURES ===================================
____________ test_ac6_actualizar_umbrales_iguales_o_invertidos_400 ____________

    def test_ac6_actualizar_umbrales_iguales_o_invertidos_400() -> None:  # AC-6
        """AC-6: Rechaza con HTTP 400 tanto umbrales invertidos (85 > 70) como iguales (75 == 75)."""
        resp_invertido = client.put(
            "/api/organizaciones/ORG-01/umbrales",
            json={"umbral_aprobacion": 70.0, "umbral_rechazo": 85.0, "autor": "admin"},
        )
        assert resp_invertido.status_code == 400
    
        resp_iguales = client.put(
            "/api/organizaciones/ORG-01/umbrales",
            json={"umbral_aprobacion": 75.0, "umbral_rechazo": 75.0, "autor": "admin"},
        )
>       assert resp_iguales.status_code == 400
E       assert 200 == 400
E        +  where 200 = <Response [200 OK]>.status_code

tests\test_motor_decision.py:234: AssertionError
============================== warnings summary ===============================
..\..\..\..\AppData\Local\Programs\Python\Python312\Lib\site-packages\fastapi\testclient.py:1
  C:\Users\Shila\AppData\Local\Programs\Python\Python312\Lib\site-packages\fastapi\testclient.py:1: StarletteDeprecationWarning: Using `httpx` with `starlette.testclient` is deprecated; install `httpx2` instead.
    from starlette.testclient import TestClient as TestClient  # noqa

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
FAILED tests/test_motor_decision.py::test_ac6_actualizar_umbrales_iguales_o_invertidos_400
1 failed, 15 passed, 1 warning in 1.05s
```

---

## 3. Hallazgos y Observaciones del Revisor

1. **[HALLAZGO-01]** El criterio `AC-6` no tiene comentario de trazabilidad `# AC-6` en `src/*.py`.
2. **[HALLAZGO-02]** La ejecución de `python -m pytest -q` reportó fallas en la suite de pruebas.

### Nota de Auditoría del Revisor
En la Iteracion 1, el agente revisor detecta dos incumplimientos en src/repository.py::actualizar_umbrales_organizacion: (1) falta el comentario obligatorio de trazabilidad para el sexto criterio en src/, y (2) la validacion usa '>' en lugar de '>=', permitiendo configurar umbral_rechazo == umbral_aprobacion (75.0 == 75.0), lo que hace fallar test_ac6_actualizar_umbrales_iguales_o_invertidos_400. Se emite veredicto RECHAZADO y se devuelve al implementador.

---

## 4. Decisión de Traspaso
- **Acción:** Se devuelve el trabajo al agente `implementador` para corregir los hallazgos listados (Iteración 2 de 2).
