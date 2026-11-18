# Plan de Diseño Técnico y Tareas SDD (`docs/trabajo/02_plan_tareas.md`)
## Funcionalidad: Motor de Puntaje Ponderado, Precedencia de Fraude y Umbrales por Cliente

| Campo | Valor |
| :--- | :--- |
| **ID Plan** | `PLAN-MIRA-E4` |
| **Agente Autor** | `planificador` (`.github/agents/planificador.agent.md`) |
| **Entrada Consumida** | `docs/trabajo/01_especificacion.md` (`APROBADA POR REPRESENTANTE DEL CLIENTE` en commit `81ed7cf`) |
| **Estado del Plan** | `APROBADO EN CONTROL HUMANO #2 (PCH-2)` |
| **Criterios Trazados** | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-6` (Cobertura: 6/6 = 100%) |

---

## 1. Verificación de Precondición y Resumen de Arquitectura

Se verificó que `docs/trabajo/01_especificacion.md` cuenta con estado `APROBADA POR REPRESENTANTE DEL CLIENTE` y con `0` etiquetas `[NEEDS CLARIFICATION]` abiertas. A partir de la inspección del repositorio base (`src/models.py`, `src/repository.py`, `src/engine.py`, `src/api.py` y `tests/test_base_mira.py`), la solución se estructura en cuatro módulos sin agregar dependencias externas adicionales:

| Módulo / Archivo | Responsabilidad en el Diseño | Criterios `AC-N` que Implementa / Verifica |
| :--- | :--- | :--- |
| `src/models.py` | Mantiene los modelos Pydantic `ConfiguracionUmbrales`, `CasoEntrada`, `ResultadoDecision` y agrega `ActualizacionUmbralesInput` para el payload de actualización de umbrales vía API REST. | `AC-1`, `AC-5`, `AC-6` |
| `src/repository.py` | Gestiona la consulta aislada por cliente (`obtener_umbrales_organizacion`) y la función `actualizar_umbrales_organizacion` con validación de invariantes ($0 \le U_{\text{rechazo}} < U_{\text{aprobacion}} \le 100$) e incremento de versión. | `AC-5`, `AC-6` |
| `src/engine.py` | Implementa el motor algorítmico `evaluar_caso(caso: CasoEntrada) -> ResultadoDecision`: validación de catálogo de fraude, cálculo de suma ponderada $\sum V_i W_i$, precedencia absoluta de fraude, verificación de señales faltantes y mínimos por señal (`POL-DEC v2 §3-§6`). | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5` |
| `src/api.py` | Expone la interfaz HTTP/REST en FastAPI: `POST /api/casos/evaluar` y `PUT /api/organizaciones/{org_id}/umbrales`, traduciendo `KeyError` a HTTP `404` y `ValueError` a HTTP `400`. | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-6` |
| `tests/test_motor_decision.py` | Suite de pruebas unitarias y de integración (`TestClient`) con trazabilidad explícita `# AC-1` a `# AC-6`. | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-6` |

---

## 2. Contratos Técnicos y Algoritmo de Decisión

### 2.1. Contrato de Actualización de Umbrales (`src/repository.py` — `AC-5`, `AC-6`)
```python
def actualizar_umbrales_organizacion(
    org_id: str,
    umbral_aprobacion: float,
    umbral_rechazo: float,
    autor: str = "admin_cliente",
) -> ConfiguracionUmbrales:
```
- **Reglas e Invariantes:**
  1. Si `org_id` no existe en `ORGANIZACIONES_UMBRALES`, lanza `KeyError` (`# AC-5`).
  2. Si `umbral_aprobacion` o `umbral_rechazo` están fuera de `[0.0, 100.0]`, o si `umbral_rechazo >= umbral_aprobacion`, lanza `ValueError` sin modificar la configuración vigente (`# AC-6`).
  3. Si es válido, crea y almacena una nueva instancia `ConfiguracionUmbrales` con `version = actual.version + 1` y `autor_ultimo_cambio = autor` (`# AC-6`).

### 2.2. Contrato del Motor de Evaluación (`src/engine.py` — `AC-1` a `AC-5`)
```python
def evaluar_caso(caso: CasoEntrada) -> ResultadoDecision:
```
- **Orden estricto de evaluación (según aclaraciones `CL-01` y `CL-02`):**
  1. **Recuperar umbrales del cliente (`# AC-5`):** Llama a `obtener_umbrales_organizacion(caso.org_id)`.
  2. **Validar catálogo de señales de fraude y rangos numéricos (`# AC-2`):**
     - Si algún código en `caso.senales_fraude_activas` no pertenece a `CATALOGO_SENALES_FRAUDE`, lanza `ValueError`.
     - Si algún valor en `caso.senales_numericas` está fuera de `[0.0, 100.0]`, lanza `ValueError`.
  3. **Calcular puntaje ponderado y desglose por componente (`# AC-1`):**
     - Para cada señal oficial `cod, peso` en `PESOS_SENALES`: si está presente en `caso.senales_numericas`, `aporte = round(valor * peso, 4)` y se acumula en `puntaje_confianza = round(sum(aportes), 2)`.
  4. **Regla 1 · Precedencia absoluta de señal de fraude activa (`# AC-2`):**
     - Si `len(caso.senales_fraude_activas) > 0`: retorna `decision = "RECHAZADO"`, `fraude_detectado = True` y `motivo` citando las señales de fraude activas que prevalecen sobre el puntaje.
  5. **Regla 2 · Verificación de señales obligatorias faltantes (`# AC-4`):**
     - Si falta alguna de las 4 claves de `PESOS_SENALES` (`DOC_AUT`, `BIO_ROSTRO`, `CRUCE_MONTO`, `CRUCE_FECHA`): retorna `decision = "DERIVADO_A_REVISION"`, indicando en `motivo` las señales faltantes (`POL-DEC v2 §6`).
  6. **Regla 3 · Verificación de mínimos individuales por señal (`# AC-3`):**
     - Verifica cada señal contra `MINIMOS_POR_SENAL` (`DOC_AUT >= 70`, `BIO_ROSTRO >= 75`, `CRUCE_MONTO >= 60`, `CRUCE_FECHA >= 60`).
     - Si `senales_bajo_minimo` no está vacía: retorna `decision = "DERIVADO_A_REVISION"` listando las señales bajo mínimo (`POL-DEC v2 §3`).
  7. **Regla 4 · Comparación contra los umbrales propios del cliente (`# AC-1`, `# AC-3`, `# AC-4`, `# AC-5`):**
     - Si `puntaje_confianza >= cfg.umbral_aprobacion` $\rightarrow$ `decision = "APROBADO"` (`# AC-1`).
     - Si `puntaje_confianza <= cfg.umbral_rechazo` $\rightarrow$ `decision = "RECHAZADO"` (`# AC-4`).
     - Si `cfg.umbral_rechazo < puntaje_confianza < cfg.umbral_aprobacion` $\rightarrow$ `decision = "DERIVADO_A_REVISION"` (`# AC-3`).

### 2.3. Contratos de Interfaz REST (`src/api.py`)
- `POST /api/casos/evaluar`: Recibe `CasoEntrada`, invoca `evaluar_caso(caso)` y devuelve `ResultadoDecision` (HTTP 200), o HTTP 404 si `org_id` no existe (`KeyError`), o HTTP 400 si hay datos inválidos (`ValueError`).
- `PUT /api/organizaciones/{org_id}/umbrales`: Recibe `ActualizacionUmbralesInput` (`umbral_aprobacion`, `umbral_rechazo`, `autor`), invoca `actualizar_umbrales_organizacion` y devuelve la nueva `ConfiguracionUmbrales` (HTTP 200), o HTTP 404/400 ante error.

---

## 3. Desglose de Tareas Ordenadas por Dependencia (`Tasks`)

| ID Tarea | Descripción de la Tarea Implementable | Archivos que Modifica / Crea | Criterios `AC-N` Referenciados | Dependencia |
| :--- | :--- | :--- | :---: | :---: |
| **`T-01`** |Escribir primero la suite de pruebas SDD (`Test-First`) en `tests/test_motor_decision.py` con al menos 12 tests que verifiquen cada criterio y caso de borde, incluyendo comentarios `# AC-1` a `# AC-6`. | `tests/test_motor_decision.py` | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-6` | `01_especificacion.md` |
| **`T-02`** | Agregar el modelo `ActualizacionUmbralesInput` en `src/models.py` e implementar `actualizar_umbrales_organizacion` en `src/repository.py` con validaciones de rango, invariante `umbral_rechazo < umbral_aprobacion` e incremento de versión. | `src/models.py`, `src/repository.py` | `AC-5`, `AC-6` | `T-01` |
| **`T-03`** | Implementar `calcular_puntaje_ponderado` y `evaluar_caso` en `src/engine.py` respetando el orden de precedencia (1. Fraude, 2. Señales faltantes, 3. Mínimos por señal, 4. Umbrales del cliente) y etiquetando cada bloque con `# AC-1` a `# AC-5`. | `src/engine.py` | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5` | `T-02` |
| **`T-04`** | Implementar los endpoints `POST /api/casos/evaluar` y `PUT /api/organizaciones/{org_id}/umbrales` en `src/api.py` con manejo tipado de errores HTTP 400 y 404 y comentarios `# AC-1` a `# AC-6`. | `src/api.py` | `AC-1`, `AC-2`, `AC-3`, `AC-4`, `AC-5`, `AC-6` | `T-03` |
| **`T-05`** | Ejecutar la skill `ejecutor-pruebas` (`ejecutar_suite.py`) y documentar los archivos modificados, el mapeo de criterios y la tabla de resultados en `docs/trabajo/03_implementacion.md`. | `docs/trabajo/03_implementacion.md` | `AC-1` a `AC-6` | `T-04` |
| **`T-06`** | Auditar la entrega con el agente `revisor` (sin herramienta `edit`) ejecutando el script Nivel 3 `verificar_trazabilidad.py --reporte docs/trabajo/04_revision.md`. | `docs/trabajo/04_revision.md` | `AC-1` a `AC-6` | `T-05` |

---

## 4. Matriz de Trazabilidad 1:1 (`AC-N` $\leftrightarrow$ Tarea $\leftrightarrow$ Pruebas $\leftrightarrow$ Código)

| Criterio SDD | Tarea(s) | Funciones de Prueba en `tests/test_motor_decision.py` | Módulos y Funciones en `src/` |
| :--- | :---: | :--- | :--- |
| **`AC-1`** | `T-01`, `T-03`, `T-04` | `test_ac1_aprobacion_puntaje_ponderado`, `test_ac1_endpoint_evaluar_aprobado` (`# AC-1`) | `src/engine.py::evaluar_caso`, `src/api.py::evaluar_caso_endpoint` (`# AC-1`) |
| **`AC-2`** | `T-01`, `T-03`, `T-04` | `test_ac2_precedencia_fraude_sobre_puntaje_alto`, `test_ac2_senal_fraude_desconocida_error` (`# AC-2`) | `src/engine.py::evaluar_caso`, `src/api.py::evaluar_caso_endpoint` (`# AC-2`) |
| **`AC-3`** | `T-01`, `T-03`, `T-04` | `test_ac3_derivacion_rango_intermedio`, `test_ac3_derivacion_senal_bajo_minimo_aunque_puntaje_alto` (`# AC-3`) | `src/engine.py::evaluar_caso` (`# AC-3`) |
| **`AC-4`** | `T-01`, `T-03`, `T-04` | `test_ac4_rechazo_puntaje_bajo_umbral`, `test_ac4_derivacion_obligatoria_senal_faltante` (`# AC-4`) | `src/engine.py::evaluar_caso` (`# AC-4`) |
| **`AC-5`** | `T-01`, `T-02`, `T-03`, `T-04` | `test_ac5_umbrales_propios_por_cliente_mismo_puntaje`, `test_ac5_organizacion_inexistente_404` (`# AC-5`) | `src/repository.py::obtener_umbrales_organizacion`, `src/engine.py::evaluar_caso` (`# AC-5`) |
| **`AC-6`** | `T-01`, `T-02`, `T-04` | `test_ac6_actualizar_umbrales_valido_incrementa_version`, `test_ac6_actualizar_umbrales_invalidos_400` (`# AC-6`) | `src/repository.py::actualizar_umbrales_organizacion`, `src/api.py::actualizar_umbrales_endpoint` (`# AC-6`) |

---

## 5. Punto de Control Humano #2 (`PCH-2`) · Revisión y Aprobación del Plan

- **Personas que revisan:** Max Latuz Zepeda (Arquitectura Backend) & Joaquín Aguilera Arellano (Representante del Cliente y Frontend).
- **Qué se revisó:**
  1. Que ninguna tarea del plan introduzca elementos declarados en *Fuera de alcance* en `01_especificacion.md`.
  2. Que los contratos JSON de `POST /api/casos/evaluar` y `PUT /api/organizaciones/{org_id}/umbrales` entreguen todos los campos requeridos (`puntaje_confianza`, `decision`, `motivo`, `senales_bajo_minimo`, `fraude_detectado`, `detalle_componentes`, `version_umbrales`) para que el Frontend de la Fase 5 los consuma directamente.
  3. Que los 6 criterios `AC-1` a `AC-6` tengan cobertura 1:1 en la matriz de tareas y pruebas.
- **Decisión tomada:** **`PLAN APROBADO`**. Se autoriza el traspaso (*handoff*) al agente `implementador`.
