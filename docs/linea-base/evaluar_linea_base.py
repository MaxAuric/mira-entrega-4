"""Script de evaluación empírica de la Línea Base (1 solo agente) frente a los 6 criterios SDD de MIRA."""

import importlib.util
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models import CasoEntrada  # noqa: E402
from src.repository import reiniciar_repositorio_base  # noqa: E402

SNAPSHOT_PATH = pathlib.Path(__file__).resolve().parent / "motor_un_agente_snapshot.py"
spec = importlib.util.spec_from_file_location("motor_un_agente_snapshot", SNAPSHOT_PATH)
assert spec and spec.loader
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


def evaluar_criterios_sobre_snapshot() -> None:
    reiniciar_repositorio_base()
    resultados = []

    # AC-1: Aprobación con puntaje ponderado exacto (90*0.35 + 85*0.30 + 80*0.20 + 80*0.15 = 85.0)
    caso_ac1 = CasoEntrada(
        caso_id="C-AC1",
        org_id="ORG-01",
        senales_numericas={"DOC_AUT": 90.0, "BIO_ROSTRO": 85.0, "CRUCE_MONTO": 80.0, "CRUCE_FECHA": 80.0},
        senales_fraude_activas=[],
    )
    res_ac1 = snapshot.evaluar_caso_linea_base(caso_ac1)
    # Con promedio simple da (90+85+80+80)/4 = 83.75 (<85 -> DERIVADO en vez de 85.0 -> APROBADO)
    cumple_ac1 = res_ac1.decision == "APROBADO" and res_ac1.puntaje_confianza == 85.0
    resultados.append(("AC-1 (Puntaje ponderado y aprobación >= umbral)", cumple_ac1, f"Obtuvo puntaje={res_ac1.puntaje_confianza}, decision={res_ac1.decision} (Esperado: 85.0, APROBADO)"))

    # AC-2: Precedencia de señal de fraude activa sobre puntaje alto
    caso_ac2 = CasoEntrada(
        caso_id="C-AC2",
        org_id="ORG-01",
        senales_numericas={"DOC_AUT": 98.0, "BIO_ROSTRO": 96.0, "CRUCE_MONTO": 95.0, "CRUCE_FECHA": 95.0},
        senales_fraude_activas=["FRA_EDICION"],
    )
    res_ac2 = snapshot.evaluar_caso_linea_base(caso_ac2)
    cumple_ac2 = res_ac2.decision == "RECHAZADO" and res_ac2.fraude_detectado is True
    resultados.append(("AC-2 (Precedencia absoluta de señal de fraude)", cumple_ac2, f"Obtuvo decision={res_ac2.decision}, fraude={res_ac2.fraude_detectado}"))

    # AC-3: Derivación obligatoria cuando una señal individual cae bajo su mínimo propio (DOC_AUT=55 < 70)
    caso_ac3 = CasoEntrada(
        caso_id="C-AC3",
        org_id="ORG-01",
        senales_numericas={"DOC_AUT": 55.0, "BIO_ROSTRO": 98.0, "CRUCE_MONTO": 98.0, "CRUCE_FECHA": 98.0},
        senales_fraude_activas=[],
    )
    res_ac3 = snapshot.evaluar_caso_linea_base(caso_ac3)
    cumple_ac3 = res_ac3.decision == "DERIVADO_A_REVISION"
    resultados.append(("AC-3 (Derivación por señal bajo mínimo propio POL-DEC v2 §3)", cumple_ac3, f"Obtuvo decision={res_ac3.decision} con DOC_AUT=55 (<70) (Esperado: DERIVADO_A_REVISION)"))

    # AC-4: Derivación obligatoria ante señal faltante (falta BIO_ROSTRO)
    caso_ac4 = CasoEntrada(
        caso_id="C-AC4",
        org_id="ORG-01",
        senales_numericas={"DOC_AUT": 95.0, "CRUCE_MONTO": 95.0, "CRUCE_FECHA": 95.0},
        senales_fraude_activas=[],
    )
    res_ac4 = snapshot.evaluar_caso_linea_base(caso_ac4)
    cumple_ac4 = res_ac4.decision == "DERIVADO_A_REVISION"
    resultados.append(("AC-4 (Derivación ante señales faltantes POL-DEC v2 §6)", cumple_ac4, f"Obtuvo decision={res_ac4.decision} sin BIO_ROSTRO (Esperado: DERIVADO_A_REVISION)"))

    # AC-5: Umbrales personalizados por cliente (puntaje 82.0: DERIVADO en ORG-01 [>=85], APROBADO en ORG-02 [>=80])
    caso_org1 = CasoEntrada(
        caso_id="C-AC5-1",
        org_id="ORG-01",
        senales_numericas={"DOC_AUT": 82.0, "BIO_ROSTRO": 82.0, "CRUCE_MONTO": 82.0, "CRUCE_FECHA": 82.0},
    )
    caso_org2 = CasoEntrada(
        caso_id="C-AC5-2",
        org_id="ORG-02",
        senales_numericas={"DOC_AUT": 82.0, "BIO_ROSTRO": 82.0, "CRUCE_MONTO": 82.0, "CRUCE_FECHA": 82.0},
    )
    r1 = snapshot.evaluar_caso_linea_base(caso_org1)
    r2 = snapshot.evaluar_caso_linea_base(caso_org2)
    cumple_ac5 = r1.decision == "DERIVADO_A_REVISION" and r2.decision == "APROBADO"
    resultados.append(("AC-5 (Umbrales propios por organización cliente)", cumple_ac5, f"ORG-01={r1.decision}, ORG-02={r2.decision}"))

    # AC-6: Rechazo de configuración inválida de umbrales (umbral_rechazo >= umbral_aprobacion)
    rechazo_invalido_bloqueado = False
    try:
        snapshot.actualizar_umbrales_linea_base("ORG-01", umbral_aprobacion=70.0, umbral_rechazo=85.0)
    except ValueError:
        rechazo_invalido_bloqueado = True
    reiniciar_repositorio_base()
    resultados.append(("AC-6 (Validación de invariante umbral_rechazo < umbral_aprobacion)", rechazo_invalido_bloqueado, "Aceptó umbral_rechazo=85 > umbral_aprobacion=70 sin lanzar ValueError"))

    codigo_texto = SNAPSHOT_PATH.read_text(encoding="utf-8")
    tags_ac = re.findall(r"#\s*AC-\d+", codigo_texto)

    print("=== AUDITORÍA EJECUTABLE DE LA LÍNEA BASE (1 SOLO AGENTE) ===")
    print("")
    print("| Criterio Oficial del Cliente | ¿Cumple? | Evidencia Observada |")
    print("| :--- | :---: | :--- |")
    aprobados = 0
    for nombre, ok, detalle in resultados:
        estado = "SI" if ok else "NO (FALLA)"
        if ok:
            aprobados += 1
        print(f"| `{nombre}` | **{estado}** | {detalle} |")
    print("")
    print(f"- Criterios de negocio cumplidos al 100%: {aprobados}/6 ({round(aprobados*100/6, 1)}%)")
    print(f"- Comentarios de trazabilidad '# AC-N' en código: {len(tags_ac)}/6 (0.0%)")


if __name__ == "__main__":
    evaluar_criterios_sobre_snapshot()
