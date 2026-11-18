"""Módulo base de evaluación de casos en MIRA (estado inicial previo a la corrida SDD)."""

from src.models import CasoEntrada, ResultadoDecision
from src.repository import obtener_umbrales_organizacion


def estado_base_motor() -> dict:
    """Informa el estado inicial del motor MIRA antes del desarrollo de la funcionalidad SDD."""
    return {
        "servicio": "MIRA-Decision-Engine",
        "estado": "BASE_ENTREGA_3",
        "mensaje": "Catálogo de señales y organizaciones cargado. Motor de decisión pendiente de implementación SDD.",
    }
