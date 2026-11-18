"""Motor de evaluación de puntaje ponderado, precedencia de fraude y decisión por umbrales en MIRA."""

from typing import Dict, List
from src.models import CasoEntrada, ResultadoDecision
from src.repository import (
    CATALOGO_SENALES_FRAUDE,
    MINIMOS_POR_SENAL,
    PESOS_SENALES,
    obtener_umbrales_organizacion,
)


def estado_base_motor() -> dict:
    """Informa el estado operativo del motor de decisión de MIRA."""
    return {
        "servicio": "MIRA-Decision-Engine",
        "estado": "OPERATIVO_SDD",
        "mensaje": "Motor de puntaje ponderado, precedencia de fraude y umbrales por cliente activo.",
    }


def evaluar_caso(caso: CasoEntrada) -> ResultadoDecision:
    """Evalúa un caso analizado aplicando precedencia de fraude, mínimos por señal y umbrales del cliente."""
    # 1. Obtener umbrales propios y aislados de la organización cliente (# AC-5)
    cfg = obtener_umbrales_organizacion(caso.org_id)  # AC-5

    # 2. Validar catálogo oficial de señales de fraude (# AC-2)
    for cod_fraude in caso.senales_fraude_activas:
        if cod_fraude not in CATALOGO_SENALES_FRAUDE:  # AC-2
            raise ValueError(f"Señal de fraude '{cod_fraude}' no pertenece al catálogo CAT-SEN v3.")

    # 3. Validar rango de señales numéricas y calcular aporte ponderado por componente (# AC-1)
    detalle_componentes: Dict[str, float] = {}
    for cod_senal, valor in caso.senales_numericas.items():
        if not (0.0 <= float(valor) <= 100.0):
            raise ValueError(f"El valor de la señal '{cod_senal}' ({valor}) debe estar entre 0 y 100.")

    for cod_oficial, peso in PESOS_SENALES.items():
        if cod_oficial in caso.senales_numericas:
            detalle_componentes[cod_oficial] = round(float(caso.senales_numericas[cod_oficial]) * peso, 4)  # AC-1

    puntaje_confianza = round(sum(detalle_componentes.values()), 2)  # AC-1

    # 4. Verificar señales obligatorias faltantes (POL-DEC v2 §6) y mínimos por señal (POL-DEC v2 §3)
    senales_faltantes: List[str] = [
        cod for cod in PESOS_SENALES if cod not in caso.senales_numericas
    ]  # AC-4
    senales_bajo_minimo: List[str] = [
        cod
        for cod, minimo in MINIMOS_POR_SENAL.items()
        if cod in caso.senales_numericas and float(caso.senales_numericas[cod]) < minimo
    ]  # AC-3

    # 5. Regla de Precedencia 1: Señal de fraude activa manda por sobre todo lo demás (# AC-2)
    if caso.senales_fraude_activas:  # AC-2
        codigos_str = ", ".join(caso.senales_fraude_activas)
        return ResultadoDecision(
            caso_id=caso.caso_id,
            org_id=caso.org_id,
            puntaje_confianza=puntaje_confianza,
            decision="RECHAZADO",  # AC-2
            motivo=f"Precedencia absoluta de señal de fraude activa ({codigos_str}) por sobre el puntaje ({puntaje_confianza}).",
            umbral_aprobacion_aplicado=cfg.umbral_aprobacion,
            umbral_rechazo_aplicado=cfg.umbral_rechazo,
            version_umbrales=cfg.version,
            senales_bajo_minimo=senales_bajo_minimo,
            fraude_detectado=True,
            detalle_componentes=detalle_componentes,
        )

    # 6. Regla de Precedencia 2: Señales faltantes derivan obligatoriamente a revisión (# AC-4)
    if senales_faltantes:  # AC-4
        faltantes_str = ", ".join(senales_faltantes)
        return ResultadoDecision(
            caso_id=caso.caso_id,
            org_id=caso.org_id,
            puntaje_confianza=puntaje_confianza,
            decision="DERIVADO_A_REVISION",  # AC-4
            motivo=f"Derivado a revisión por información incompleta; señales faltantes: {faltantes_str} (POL-DEC v2 §6).",
            umbral_aprobacion_aplicado=cfg.umbral_aprobacion,
            umbral_rechazo_aplicado=cfg.umbral_rechazo,
            version_umbrales=cfg.version,
            senales_bajo_minimo=senales_bajo_minimo,
            fraude_detectado=False,
            detalle_componentes=detalle_componentes,
        )

    # 7. Regla de Precedencia 3: Señal individual bajo mínimo propio deriva a revisión (# AC-3)
    if senales_bajo_minimo:  # AC-3
        bajo_str = ", ".join(senales_bajo_minimo)
        return ResultadoDecision(
            caso_id=caso.caso_id,
            org_id=caso.org_id,
            puntaje_confianza=puntaje_confianza,
            decision="DERIVADO_A_REVISION",  # AC-3
            motivo=f"Derivado a revisión por incumplimiento de mínimo individual en: {bajo_str} (POL-DEC v2 §3).",
            umbral_aprobacion_aplicado=cfg.umbral_aprobacion,
            umbral_rechazo_aplicado=cfg.umbral_rechazo,
            version_umbrales=cfg.version,
            senales_bajo_minimo=senales_bajo_minimo,
            fraude_detectado=False,
            detalle_componentes=detalle_componentes,
        )

    # 8. Regla 4: Decisión según umbrales propios de la organización cliente (# AC-1, # AC-3, # AC-4, # AC-5)
    if puntaje_confianza >= cfg.umbral_aprobacion:  # AC-1
        decision = "APROBADO"
        motivo = (
            f"Puntaje ponderado ({puntaje_confianza}) alcanza o supera el umbral de aprobación "
            f"de {cfg.nombre_org} ({cfg.umbral_aprobacion}) sin señales de fraude y cumpliendo mínimos."
        )
    elif puntaje_confianza <= cfg.umbral_rechazo:  # AC-4
        decision = "RECHAZADO"
        motivo = (
            f"Puntaje ponderado ({puntaje_confianza}) es igual o inferior al umbral de rechazo "
            f"de {cfg.nombre_org} ({cfg.umbral_rechazo})."
        )
    else:  # AC-3
        decision = "DERIVADO_A_REVISION"
        motivo = (
            f"Puntaje ponderado ({puntaje_confianza}) se encuentra en el rango intermedio de revisión "
            f"de {cfg.nombre_org} ({cfg.umbral_rechazo} < puntaje < {cfg.umbral_aprobacion})."
        )

    return ResultadoDecision(
        caso_id=caso.caso_id,
        org_id=caso.org_id,
        puntaje_confianza=puntaje_confianza,
        decision=decision,
        motivo=motivo,
        umbral_aprobacion_aplicado=cfg.umbral_aprobacion,
        umbral_rechazo_aplicado=cfg.umbral_rechazo,
        version_umbrales=cfg.version,
        senales_bajo_minimo=senales_bajo_minimo,
        fraude_detectado=False,
        detalle_componentes=detalle_componentes,
    )
