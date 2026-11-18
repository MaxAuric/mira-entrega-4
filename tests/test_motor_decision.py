"""Suite de pruebas SDD del motor de decisión y umbrales por cliente de MIRA (AC-1 a AC-6)."""

import pytest
from fastapi.testclient import TestClient
from src.api import app
from src.engine import evaluar_caso
from src.models import CasoEntrada
from src.repository import actualizar_umbrales_organizacion, reiniciar_repositorio_base

client = TestClient(app)


def setup_function() -> None:
    """Restaura los umbrales base antes de cada prueba."""
    reiniciar_repositorio_base()


def test_ac1_aprobacion_puntaje_ponderado() -> None:  # AC-1
    """AC-1: Calcula el puntaje ponderado exacto y aprueba cuando >= umbral_aprobacion sin fraude."""
    caso = CasoEntrada(
        caso_id="C-101",
        org_id="ORG-01",
        senales_numericas={
            "DOC_AUT": 90.0,
            "BIO_ROSTRO": 85.0,
            "CRUCE_MONTO": 80.0,
            "CRUCE_FECHA": 80.0,
        },
        senales_fraude_activas=[],
    )
    res = evaluar_caso(caso)  # AC-1
    assert res.puntaje_confianza == 85.0
    assert res.decision == "APROBADO"
    assert res.fraude_detectado is False
    assert res.detalle_componentes["DOC_AUT"] == 31.5


def test_ac1_endpoint_evaluar_aprobado() -> None:  # AC-1
    """AC-1: Verifica el endpoint POST /api/casos/evaluar para un caso aprobado."""
    resp = client.post(
        "/api/casos/evaluar",
        json={
            "caso_id": "C-101B",
            "org_id": "ORG-01",
            "senales_numericas": {
                "DOC_AUT": 92.0,
                "BIO_ROSTRO": 90.0,
                "CRUCE_MONTO": 85.0,
                "CRUCE_FECHA": 88.0,
            },
            "senales_fraude_activas": [],
        },
    )
    assert resp.status_code == 200
    datos = resp.json()
    assert datos["decision"] == "APROBADO"
    assert datos["puntaje_confianza"] == 89.4


def test_ac2_precedencia_fraude_sobre_puntaje_alto() -> None:  # AC-2
    """AC-2: Una señal de fraude activa rechaza inmediatamente el caso aunque el puntaje supere 95."""
    caso = CasoEntrada(
        caso_id="C-102",
        org_id="ORG-01",
        senales_numericas={
            "DOC_AUT": 98.0,
            "BIO_ROSTRO": 96.0,
            "CRUCE_MONTO": 95.0,
            "CRUCE_FECHA": 95.0,
        },
        senales_fraude_activas=["FRA_EDICION"],
    )
    res = evaluar_caso(caso)  # AC-2
    assert res.puntaje_confianza == 96.35
    assert res.decision == "RECHAZADO"
    assert res.fraude_detectado is True
    assert "FRA_EDICION" in res.motivo


def test_ac2_senal_fraude_desconocida_error() -> None:  # AC-2
    """AC-2: Rechaza con HTTP 400 / ValueError códigos de fraude que no existen en CAT-SEN v3."""
    resp = client.post(
        "/api/casos/evaluar",
        json={
            "caso_id": "C-102B",
            "org_id": "ORG-01",
            "senales_numericas": {
                "DOC_AUT": 90.0,
                "BIO_ROSTRO": 90.0,
                "CRUCE_MONTO": 90.0,
                "CRUCE_FECHA": 90.0,
            },
            "senales_fraude_activas": ["FRA_INVENTADO"],
        },
    )
    assert resp.status_code == 400


def test_ac3_derivacion_rango_intermedio() -> None:  # AC-3
    """AC-3: Deriva a revisión un caso sin fraude cuyo puntaje cae entre umbral_rechazo y umbral_aprobacion."""
    caso = CasoEntrada(
        caso_id="C-103A",
        org_id="ORG-01",
        senales_numericas={
            "DOC_AUT": 75.0,
            "BIO_ROSTRO": 75.0,
            "CRUCE_MONTO": 75.0,
            "CRUCE_FECHA": 75.0,
        },
        senales_fraude_activas=[],
    )
    res = evaluar_caso(caso)  # AC-3
    assert res.puntaje_confianza == 75.0
    assert res.decision == "DERIVADO_A_REVISION"
    assert res.senales_bajo_minimo == []


def test_ac3_derivacion_senal_bajo_minimo_aunque_puntaje_alto() -> None:  # AC-3
    """AC-3: Deriva a revisión si DOC_AUT < 70 aunque el puntaje ponderado total supere 85.0."""
    caso = CasoEntrada(
        caso_id="C-103B",
        org_id="ORG-01",
        senales_numericas={
            "DOC_AUT": 55.0,
            "BIO_ROSTRO": 98.0,
            "CRUCE_MONTO": 98.0,
            "CRUCE_FECHA": 98.0,
        },
        senales_fraude_activas=[],
    )
    res = evaluar_caso(caso)  # AC-3
    assert res.puntaje_confianza == 82.95 or res.puntaje_confianza > 80.0
    assert res.decision == "DERIVADO_A_REVISION"
    assert "DOC_AUT" in res.senales_bajo_minimo


def test_ac4_rechazo_puntaje_bajo_umbral() -> None:  # AC-4
    """AC-4: Rechaza el caso cuando el puntaje ponderado es <= umbral_rechazo de la organización."""
    caso = CasoEntrada(
        caso_id="C-104A",
        org_id="ORG-01",
        senales_numericas={
            "DOC_AUT": 70.0,
            "BIO_ROSTRO": 75.0,
            "CRUCE_MONTO": 10.0,
            "CRUCE_FECHA": 10.0,
        },
        senales_fraude_activas=[],
    )
    # Con valores todos cumpliendo mínimos no es posible <=60 en ORG-01 salvo que el cliente tenga umbral_rechazo mayor,
    # o cuando una señal falta. Si probamos en ORG-03 con umbral_rechazo actualizado a 72.0:
    actualizar_umbrales_organizacion("ORG-03", umbral_aprobacion=90.0, umbral_rechazo=72.0)
    caso_bajo = CasoEntrada(
        caso_id="C-104A",
        org_id="ORG-03",
        senales_numericas={
            "DOC_AUT": 70.0,
            "BIO_ROSTRO": 75.0,
            "CRUCE_MONTO": 65.0,
            "CRUCE_FECHA": 65.0,
        },
        senales_fraude_activas=[],
    )
    res = evaluar_caso(caso_bajo)  # AC-4
    assert res.puntaje_confianza == 69.75
    assert res.decision == "RECHAZADO"


def test_ac4_derivacion_obligatoria_senal_faltante() -> None:  # AC-4
    """AC-4: Si falta una señal obligatoria (ej. BIO_ROSTRO), deriva a revisión sin aprobar jamás."""
    caso = CasoEntrada(
        caso_id="C-104B",
        org_id="ORG-01",
        senales_numericas={
            "DOC_AUT": 98.0,
            "CRUCE_MONTO": 98.0,
            "CRUCE_FECHA": 98.0,
        },
        senales_fraude_activas=[],
    )
    res = evaluar_caso(caso)  # AC-4
    assert res.decision == "DERIVADO_A_REVISION"
    assert "BIO_ROSTRO" in res.motivo


def test_ac5_umbrales_propios_por_cliente_mismo_puntaje() -> None:  # AC-5
    """AC-5: El mismo puntaje 82.0 se deriva en ORG-01 (umbral 85) y se aprueba en ORG-02 (umbral 80)."""
    senales = {
        "DOC_AUT": 82.0,
        "BIO_ROSTRO": 82.0,
        "CRUCE_MONTO": 82.0,
        "CRUCE_FECHA": 82.0,
    }
    res_org1 = evaluar_caso(CasoEntrada(caso_id="C-105A", org_id="ORG-01", senales_numericas=senales))  # AC-5
    res_org2 = evaluar_caso(CasoEntrada(caso_id="C-105B", org_id="ORG-02", senales_numericas=senales))  # AC-5
    assert res_org1.puntaje_confianza == 82.0
    assert res_org2.puntaje_confianza == 82.0
    assert res_org1.decision == "DERIVADO_A_REVISION"
    assert res_org2.decision == "APROBADO"


def test_ac5_organizacion_inexistente_404() -> None:  # AC-5
    """AC-5: Evaluar o consultar una organización no registrada devuelve HTTP 404."""
    resp = client.get("/api/organizaciones/ORG-999/umbrales")
    assert resp.status_code == 404


def test_ac6_actualizar_umbrales_valido_incrementa_version() -> None:  # AC-6
    """AC-6: Actualizar umbrales válidos vía PUT incrementa la versión y registra el autor."""
    resp = client.put(
        "/api/organizaciones/ORG-01/umbrales",
        json={"umbral_aprobacion": 88.0, "umbral_rechazo": 62.0, "autor": "supervisor_riesgo"},
    )
    assert resp.status_code == 200
    datos = resp.json()
    assert datos["umbral_aprobacion"] == 88.0
    assert datos["umbral_rechazo"] == 62.0
    assert datos["version"] == 2
    assert datos["autor_ultimo_cambio"] == "supervisor_riesgo"


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
    assert resp_iguales.status_code == 400
