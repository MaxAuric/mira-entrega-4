"""Script Nivel 3 de la skill verificador-trazabilidad.

Audita automáticamente que cada criterio AC-1..AC-N definido en
docs/trabajo/01_especificacion.md esté referenciado en:
1) docs/trabajo/02_plan_tareas.md
2) tests/*.py (como comentario o referencia AC-N)
3) src/*.py (como comentario # AC-N)
Además ejecuta pytest -q y puede escribir el reporte auditable en
docs/trabajo/04_revision.md para que el agente revisor no necesite la tool 'edit'.
"""

import argparse
import pathlib
import re
import subprocess
import sys
from typing import Dict, List, Set


ROOT = pathlib.Path(__file__).resolve().parents[4]
SPEC_PATH = ROOT / "docs" / "trabajo" / "01_especificacion.md"
PLAN_PATH = ROOT / "docs" / "trabajo" / "02_plan_tareas.md"
SRC_DIR = ROOT / "src"
TESTS_DIR = ROOT / "tests"


def extraer_criterios_spec(spec_text: str) -> List[str]:
    """Extrae todos los identificadores AC-N presentes en la especificación."""
    encontrados = re.findall(r"\bAC-\d+\b", spec_text)
    vistos: Set[str] = set()
    ordenados: List[str] = []
    for ac in encontrados:
        if ac not in vistos:
            vistos.add(ac)
            ordenados.append(ac)
    return sorted(ordenados, key=lambda x: int(x.split("-")[1]))


def buscar_ac_en_directorio(directorio: pathlib.Path, ac: str, exigir_comentario: bool = True) -> List[str]:
    """Devuelve lista de archivos:línea donde aparece el criterio AC-N."""
    coincidencias: List[str] = []
    patron = re.compile(rf"#.*\b{re.escape(ac)}\b" if exigir_comentario else rf"\b{re.escape(ac)}\b")
    for archivo in sorted(directorio.glob("*.py")):
        lineas = archivo.read_text(encoding="utf-8").splitlines()
        for idx, linea in enumerate(lineas, start=1):
            if patron.search(linea):
                coincidencias.append(f"{archivo.relative_to(ROOT).as_posix()}:{idx}")
    return coincidencias


def ejecutar_pytest() -> tuple[bool, str]:
    """Ejecuta python -m pytest -q y devuelve (exito, salida)."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    salida = (proc.stdout + "\n" + proc.stderr).strip()
    return proc.returncode == 0, salida


def auditar_trazabilidad() -> Dict:
    """Realiza la auditoría completa SDD y retorna el diccionario de resultados."""
    if not SPEC_PATH.exists():
        return {
            "aprobado": False,
            "error": f"No existe el archivo de especificación: {SPEC_PATH}",
            "criterios": [],
        }

    spec_text = SPEC_PATH.read_text(encoding="utf-8")
    plan_text = PLAN_PATH.read_text(encoding="utf-8") if PLAN_PATH.exists() else ""
    criterios = extraer_criterios_spec(spec_text)

    if not criterios:
        return {
            "aprobado": False,
            "error": "No se encontraron criterios AC-N en docs/trabajo/01_especificacion.md",
            "criterios": [],
        }

    filas = []
    hallazgos = []

    for ac in criterios:
        en_plan = bool(re.search(rf"\b{re.escape(ac)}\b", plan_text))
        en_tests = buscar_ac_en_directorio(TESTS_DIR, ac, exigir_comentario=True)
        en_src = buscar_ac_en_directorio(SRC_DIR, ac, exigir_comentario=True)

        cumple_ac = en_plan and bool(en_tests) and bool(en_src)
        filas.append(
            {
                "ac": ac,
                "en_plan": "SI" if en_plan else "NO",
                "en_tests": ", ".join(en_tests) if en_tests else "FALTA",
                "en_src": ", ".join(en_src) if en_src else "FALTA",
                "estado": "OK" if cumple_ac else "INCUMPLE",
            }
        )
        if not en_plan:
            hallazgos.append(f"El criterio `{ac}` no está referenciado en `docs/trabajo/02_plan_tareas.md`.")
        if not en_tests:
            hallazgos.append(f"El criterio `{ac}` no tiene comentario de trazabilidad `# {ac}` en `tests/*.py`.")
        if not en_src:
            hallazgos.append(f"El criterio `{ac}` no tiene comentario de trazabilidad `# {ac}` en `src/*.py`.")

    pytest_ok, pytest_out = ejecutar_pytest()
    if not pytest_ok:
        hallazgos.append("La ejecución de `python -m pytest -q` reportó fallas en la suite de pruebas.")

    aprobado = len(hallazgos) == 0
    return {
        "aprobado": aprobado,
        "criterios": filas,
        "hallazgos": hallazgos,
        "pytest_ok": pytest_ok,
        "pytest_out": pytest_out,
    }


def formatear_reporte_markdown(resultado: Dict, iteracion: int, nota_adicional: str = "") -> str:
    """Genera el reporte Markdown estandarizado para docs/trabajo/04_revision.md."""
    veredicto = "APROBADO" if resultado.get("aprobado") else "RECHAZADO"
    lineas = [
        f"# Reporte de Revisión y Auditoría SDD · Iteración {iteracion} de 2",
        "",
        "| Campo | Valor |",
        "| :--- | :--- |",
        "| **Agente Auditor** | `revisor` (`.github/agents/revisor.agent.md`) |",
        "| **Skill Ejecutada** | `verificador-trazabilidad` (Recurso Nivel 3: `verificar_trazabilidad.py`) |",
        f"| **Iteración del Ciclo** | `{iteracion} / 2` (Máximo declarado: 2 iteraciones) |",
        f"| **Veredicto Oficial** | **`{veredicto}`** |",
        "",
        "---",
        "",
        "## 1. Matriz de Trazabilidad 1:1 (`AC-N`)",
        "",
        "| Criterio | En Especificación | En Plan (`02_plan_tareas.md`) | En Pruebas (`tests/`) | En Código (`src/`) | Estado |",
        "| :--- | :---: | :---: | :--- | :--- | :---: |",
    ]

    for f in resultado.get("criterios", []):
        lineas.append(
            f"| **`{f['ac']}`** | SI | {f['en_plan']} | `{f['en_tests']}` | `{f['en_src']}` | **{f['estado']}** |"
        )

    lineas.extend(
        [
            "",
            "---",
            "",
            "## 2. Resultado de Verificación Ejecutable (`pytest -q`)",
            "",
            "```text",
            resultado.get("pytest_out", "Sin salida"),
            "```",
            "",
            "---",
            "",
            "## 3. Hallazgos y Observaciones del Revisor",
            "",
        ]
    )

    hallazgos = resultado.get("hallazgos", [])
    if hallazgos:
        for idx, h in enumerate(hallazgos, start=1):
            lineas.append(f"{idx}. **[HALLAZGO-0{idx}]** {h}")
    else:
        lineas.append(
            "- **Sin hallazgos pendientes:** El 100% de los criterios de aceptación (`AC-1` a `AC-6`) cuenta con trazabilidad explícita en la especificación, el plan de tareas, las pruebas unitarias y el código fuente, y la suite completa de `pytest` pasa en verde."
        )

    if nota_adicional:
        lineas.extend(["", "### Nota de Auditoría del Revisor", nota_adicional])

    lineas.extend(
        [
            "",
            "---",
            "",
            "## 4. Decisión de Traspaso",
            (
                "- **Acción:** Se devuelve el trabajo al agente `implementador` para corregir los hallazgos listados (Iteración 2 de 2)."
                if veredicto == "RECHAZADO"
                else "- **Acción:** Criterio de término cumplido. La implementación queda aprobada y lista para su integración y demostración."
            ),
            "",
        ]
    )
    return "\n".join(lineas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audita trazabilidad SDD AC-N en MIRA.")
    parser.add_argument("--reporte", type=str, default="", help="Ruta donde guardar el reporte Markdown")
    parser.add_argument("--iteracion", type=int, default=1, help="Número de iteración de revisión (1 o 2)")
    parser.add_argument("--nota", type=str, default="", help="Nota adicional del revisor")
    args = parser.parse_args()

    resultado = auditar_trazabilidad()
    if "error" in resultado:
        print(f"[ERROR TRAZABILIDAD] {resultado['error']}")
        return 1

    md = formatear_reporte_markdown(resultado, iteracion=args.iteracion, nota_adicional=args.nota)
    print(md)

    if args.reporte:
        out_path = ROOT / args.reporte
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")

    return 0 if resultado["aprobado"] else 1


if __name__ == "__main__":
    sys.exit(main())
