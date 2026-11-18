# MIRA · Entrega 4: Sistema Multiagente para Desarrollo Conducido por Especificación (SDD)

Repositorio oficial del **Entregable 4** del proyecto **MIRA** (*Plataforma de Inteligencia Multimodal para Decisiones Empresariales*, DPRIME SpA), desarrollado en el marco del *Taller de Desarrollo de Software Conducido por Agentes de IA* (Escuela de Ingeniería Informática, Universidad de Valparaíso).

---

## 1. Declaración Oficial de la Entrega

| Campo | Detalle |
| :--- | :--- |
| **Alternativa Elegida** | **Alternativa A · Desarrollo de Software Conducido por Especificación (SDD)** |
| **Caso de Negocio** | Cálculo de puntaje de confianza ponderado, precedencia absoluta de señales de fraude, validación de mínimos individuales por señal y decisión por umbrales propios de cada organización cliente (`POL-DEC v2`, `CAT-SEN v3`, `DOC-MIRA v1.4`). |
| **Herramienta y Versión** | Visual Studio Code v1.99+ con agentes personalizados (`.github/agents/*.agent.md`) y estándar abierto Agent Skills (`.github/skills/*/SKILL.md`). |
| **Modelos Utilizados** | Google Gemini 3.5 Flash Lite (operación e iteración SDD, 500 RPD) y Gemini 3.5 Flash (revisión). |
| **Integrantes del Equipo** | **Max Latuz Zepeda** (Arquitectura Multiagente, Skills, Backend y Pruebas) <br/> **Joaquín Aguilera Arellano** (**Representante del Cliente** — rol rotado respecto a la Entrega 2 — y Frontend / Testing en Vivo) |
| **Etiqueta Base para Demo en Vivo** | `entrega-3` (commit `33540ec`) |

---

## 2. Arquitectura del Sistema Multiagente (4 Agentes y 3 Skills)

### 2.1. Los Cuatro Agentes (`.github/agents/`)
1. **[`especificador.agent.md`](.github/agents/especificador.agent.md)** (`tools: ['read', 'search', 'edit']`): Traduce la necesidad del cliente en lenguaje natural a Historia de Usuario (`Given/When/Then`, `AC-1` a `AC-6`), Caso de Uso, Alcance Negativo y detecta ambigüedades `[NEEDS CLARIFICATION]` (`CL-01` a `CL-03`). Entrega [`docs/trabajo/01_especificacion.md`](docs/trabajo/01_especificacion.md).
2. **[`planificador.agent.md`](.github/agents/planificador.agent.md)** (`tools: ['read', 'search', 'edit']`): Diseña la arquitectura modular, los contratos de funciones/API y desglosa las tareas `T-01..T-06` con matriz de trazabilidad 1:1 hacia `AC-1..AC-6`. Entrega [`docs/trabajo/02_plan_tareas.md`](docs/trabajo/02_plan_tareas.md).
3. **[`implementador.agent.md`](.github/agents/implementador.agent.md)** (`tools: ['read', 'search', 'edit', 'execute']`): Único agente con permiso para editar `src/` y `tests/` incluyendo comentarios obligatorios `# AC-N`. Entrega código probado y [`docs/trabajo/03_implementacion.md`](docs/trabajo/03_implementacion.md).
4. **[`revisor.agent.md`](.github/agents/revisor.agent.md)** (`tools: ['read', 'search', 'execute']` — **SIN herramienta `edit`**): Audita en modo solo lectura que el código y las pruebas cumplan la especificación y la trazabilidad 1:1 mediante scripts de Nivel 3, emitiendo [`docs/trabajo/04_revision.md`](docs/trabajo/04_revision.md) (máximo 2 iteraciones con `implementador`).

### 2.2. Las Tres Skills (`.github/skills/`) con Recursos de Nivel 3
1. **[`sdd-spec-checklist`](.github/skills/sdd-spec-checklist/SKILL.md)**: Incluye recurso de Nivel 3 [`templates/plantilla_especificacion.md`](.github/skills/sdd-spec-checklist/templates/plantilla_especificacion.md).
2. **[`verificador-trazabilidad`](.github/skills/verificador-trazabilidad/SKILL.md)**: Incluye script ejecutable de Nivel 3 [`scripts/verificar_trazabilidad.py`](.github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py) que audita por expresiones regulares que cada `AC-1..AC-6` de la especificación esté citado en el plan, en `tests/*.py` (`# AC-N`) y en `src/*.py` (`# AC-N`), además de correr `pytest -q`.
3. **[`ejecutor-pruebas`](.github/skills/ejecutor-pruebas/SKILL.md)**: Incluye script ejecutable de Nivel 3 [`scripts/ejecutar_suite.py`](.github/skills/ejecutor-pruebas/scripts/ejecutar_suite.py) que ejecuta `pytest -v` y formatea la tabla resumen por criterio `AC-N`.

---

## 3. Estructura del Repositorio

```text
.github/
  agents/                   # Los 4 agentes: especificador, planificador, implementador, revisor
  skills/                   # Las 3 skills (SKILL.md + plantillas y scripts ejecutables Nivel 3)
  copilot-instructions.md   # Constitución SDD de MIRA y convenciones del repositorio
AGENTS.md                   # Espejo de instrucciones globales compatible con CLI agents
docs/
  decision.md               # Patrón de coordinación, agentes, herramientas, seguridad y justificación
  bitacora.md               # Registro de corridas, carga de skills, fallas MAST con diff y controles humanos
  trabajo/                  # Archivos de traspaso entre los 4 agentes (01 a 04)
  evidencia/                # Capturas, logs y salidas de la corrida entregada
  linea-base/               # Corrida comparativa con 1 solo agente y script evaluar_linea_base.py
src/                        # Código fuente del Backend de MIRA (models.py, repository.py, engine.py, api.py)
tests/                      # Suite de 16 pruebas automatizadas (test_base_mira.py, test_motor_decision.py)
requirements.txt            # Dependencias Python 3.12+ (FastAPI, Pydantic, Pytest, Streamlit)
README.md                   # Guía de ejecución rápida (< 15 minutos)
```

---

## 4. Guía de Ejecución Rápida y Reproducción (< 15 Minutos)

### 4.1. Instalación de Dependencias (< 1 min)
```bash
pip install -r requirements.txt
```

### 4.2. Ejecutar las Skills de Verificación y la Suite Completa de Pruebas (`16/16 PASSED`)
```bash
# 1. Ejecutar skill ejecutor-pruebas (tabla resumen de las 16 pruebas unitarias y de API)
python .github/skills/ejecutor-pruebas/scripts/ejecutar_suite.py

# 2. Ejecutar skill verificador-trazabilidad (auditoría 1:1 de AC-1..AC-6 en spec, plan, tests y código)
python .github/skills/verificador-trazabilidad/scripts/verificar_trazabilidad.py

# 3. Ejecutar evaluación empírica de la Línea Base (1 solo agente vs. los 6 criterios del cliente)
python docs/linea-base/evaluar_linea_base.py
```

### 4.3. Levantar el Servidor Backend API REST (FastAPI)
```bash
python -m uvicorn src.api:app --reload --port 8000
```
- Documentación interactiva Swagger UI disponible en: **`http://127.0.0.1:8000/docs`**
- Endpoints principales:
  - `GET /health`
  - `GET /api/organizaciones`
  - `GET /api/organizaciones/{org_id}/umbrales`
  - `PUT /api/organizaciones/{org_id}/umbrales`
  - `POST /api/casos/evaluar`

### 4.4. Cómo Reproducir la Demostración en Vivo desde la Etiqueta `entrega-3`
Para volver al punto de partida exacto previo a la corrida del caso (con los 4 agentes y 3 skills listos y solo las 4 pruebas base de MIRA):
```bash
git checkout entrega-3
python -m pytest -q
# Para volver al estado final entregado:
git checkout main
```
