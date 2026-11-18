"""Script Nivel 3 de la skill ejecutor-pruebas.

Ejecuta pytest -v y genera una tabla Markdown con el detalle de cada test
y un resumen final de pruebas aprobadas/fallidas.
"""

import pathlib
import re
import subprocess
import sys


ROOT = pathlib.Path(__file__).resolve().parents[4]


def main() -> int:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-v", "--tb=short"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    salida = proc.stdout + "\n" + proc.stderr
    lineas_test = []
    pasan = 0
    fallan = 0

    for linea in salida.splitlines():
        m = re.match(r"^(tests/\S+::\S+)\s+(PASSED|FAILED|ERROR)", linea.strip())
        if m:
            ruta_test, estado = m.group(1), m.group(2)
            archivo, func = ruta_test.split("::", 1)
            ac_match = re.search(r"ac(\d+)", func, re.IGNORECASE)
            criterio = f"AC-{ac_match.group(1)}" if ac_match else "Base MIRA"
            if estado == "PASSED":
                pasan += 1
            else:
                fallan += 1
            lineas_test.append((func, archivo, criterio, estado))

    print("### Tabla Resumen de Ejecución (`ejecutor-pruebas`)")
    print("")
    print("| Prueba Unitaria | Archivo | Criterio Cubierto | Resultado |")
    print("| :--- | :--- | :---: | :---: |")
    for func, archivo, criterio, estado in lineas_test:
        print(f"| `{func}` | `{archivo}` | `{criterio}` | **{estado}** |")
    print("")
    total = pasan + fallan
    estado_global = "OK" if fallan == 0 and proc.returncode == 0 else "FALLO"
    print(f"**Resultado Global:** `{estado_global} ({pasan}/{total} pruebas pasan, {fallan} fallan)`")

    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
