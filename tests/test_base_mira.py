"""Pruebas base del estado inicial (etiqueta entrega-3) de MIRA."""

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.repository import (
    CATALOGO_SENALES_FRAUDE,
    MINIMOS_POR_SENAL,
    PESOS_SENALES,
    obtener_umbrales_organizacion,
    reiniciar_repositorio_base,
)

client = TestClient(app)


def setup_function() -> None:
    reiniciar_repositorio_base()


def test_pesos_senales_suman_uno() -> None:
    """Verifica que las ponderaciones del catálogo de señales sumen 1.0."""
    assert round(sum(PESOS_SENALES.values()), 5) == 1.0


def test_minimos_y_catalogo_fraude_definidos() -> None:
    """Verifica que los mínimos de POL-DEC v2 y señales de CAT-SEN v3 estén presentes."""
    assert MINIMOS_POR_SENAL["DOC_AUT"] == 70.0
    assert MINIMOS_POR_SENAL["BIO_ROSTRO"] == 75.0
    assert "FRA_EDICION" in CATALOGO_SENALES_FRAUDE
    assert "FRA_SINTETICO" in CATALOGO_SENALES_FRAUDE


def test_obtener_umbrales_organizacion_existente() -> None:
    """Verifica que cada organización cliente tenga sus propios umbrales iniciales."""
    cfg_org1 = obtener_umbrales_organizacion("ORG-01")
    cfg_org2 = obtener_umbrales_organizacion("ORG-02")
    assert cfg_org1.umbral_aprobacion == 85.0
    assert cfg_org2.umbral_aprobacion == 80.0


def test_endpoint_health_y_organizaciones() -> None:
    """Verifica que la API base responda correctamente en /health y /api/organizaciones."""
    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    assert resp_health.json()["servicio"] == "MIRA-Decision-Engine"

    resp_orgs = client.get("/api/organizaciones")
    assert resp_orgs.status_code == 200
    assert len(resp_orgs.json()) == 3
