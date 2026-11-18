"""Snapshot del código generado en la corrida de Línea Base con 1 solo agente generalista.

Este archivo conserva la implementación producida en un solo turno sin flujo SDD,
sin aclaraciones con el Representante del Cliente y sin verificación independiente,
para su evaluación empírica mediante docs/linea-base/evaluar_linea_base.py.
"""

from typing import Dict
from src.models import CasoEntrada, ConfiguracionUmbrales, ResultadoDecision
from src.repository import ORGANIZACIONES_UMBRALES


def actualizar_umbrales_linea_base(org_id: str, umbral_aprobacion: float, umbral_rechazo: float) -> ConfiguracionUmbrales:
    """Actualización generada por 1 solo agente: omite validación de invariantes (umbral_rechazo < umbral_aprobacion)."""
    cfg = ORGANIZACIONES_UMBRALES[org_id]
    cfg.umbral_aprobacion = umbral_aprobacion
    cfg.umbral_rechazo = umbral_rechazo
    return cfg


def evaluar_caso_linea_base(caso: CasoEntrada) -> ResultadoDecision:
    """Motor generado por 1 solo agente sin especificación SDD ni aclaraciones del cliente.

    Omisiones reales detectadas frente al dominio MIRA:
    1) Usa promedio aritmético simple en lugar de PESOS_SENALES.
    2) No valida MINIMOS_POR_SENAL (POL-DEC v2 §3).
    3) No deriva cuando faltan señales obligatorias (POL-DEC v2 §6).
    4) Sin comentarios de trazabilidad # AC-N.
    """
    cfg = ORGANIZACIONES_UMBRALES[caso.org_id]

    valores = list(caso.senales_numericas.values())
    puntaje = round(sum(valores) / len(valores), 2) if valores else 0.0

    if caso.senales_fraude_activas:
        decision = "RECHAZADO"
        motivo = "Señal de fraude detectada"
    elif puntaje >= cfg.umbral_aprobacion:
        decision = "APROBADO"
        motivo = "Puntaje supera umbral de aprobación"
    elif puntaje <= cfg.umbral_rechazo:
        decision = "RECHAZADO"
        motivo = "Puntaje bajo umbral de rechazo"
    else:
        decision = "DERIVADO_A_REVISION"
        motivo = "Puntaje en rango de revisión"

    return ResultadoDecision(
        caso_id=caso.caso_id,
        org_id=caso.org_id,
        puntaje_confianza=puntaje,
        decision=decision,
        motivo=motivo,
        umbral_aprobacion_aplicado=cfg.umbral_aprobacion,
        umbral_rechazo_aplicado=cfg.umbral_rechazo,
        version_umbrales=cfg.version,
        fraude_detectado=bool(caso.senales_fraude_activas),
    )
