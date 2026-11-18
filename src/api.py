"""API REST de MIRA (FastAPI) para evaluación de casos y configuración de umbrales por cliente."""

from fastapi import FastAPI, HTTPException
from src.engine import estado_base_motor, evaluar_caso
from src.models import ActualizacionUmbralesInput, CasoEntrada
from src.repository import (
    ORGANIZACIONES_UMBRALES,
    actualizar_umbrales_organizacion,
    obtener_umbrales_organizacion,
)

app = FastAPI(
    title="MIRA · Plataforma Inteligente Multimodal de Decisión",
    version="4.0.0-sdd",
    description="Servicio backend de MIRA para gestión de umbrales por cliente y decisión automatizada de casos.",
)


@app.get("/health")
def health_check() -> dict:
    """Endpoint de salud del servicio."""
    return estado_base_motor()


@app.get("/api/organizaciones")
def listar_organizaciones() -> list:
    """Lista las organizaciones cliente y sus umbrales actuales."""
    return [cfg.model_dump() for cfg in ORGANIZACIONES_UMBRALES.values()]


@app.get("/api/organizaciones/{org_id}/umbrales")
def consultar_umbrales(org_id: str) -> dict:
    """Consulta los umbrales de una organización cliente específica (# AC-5)."""
    try:
        return obtener_umbrales_organizacion(org_id).model_dump()  # AC-5
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.put("/api/organizaciones/{org_id}/umbrales")
def actualizar_umbrales_endpoint(org_id: str, payload: ActualizacionUmbralesInput) -> dict:
    """Actualiza los umbrales propios de una organización cliente con validación de invariantes."""
    try:
        actualizado = actualizar_umbrales_organizacion(
            org_id=org_id,
            umbral_aprobacion=payload.umbral_aprobacion,
            umbral_rechazo=payload.umbral_rechazo,
            autor=payload.autor,
        )
        return actualizado.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/casos/evaluar")
def evaluar_caso_endpoint(caso: CasoEntrada) -> dict:
    """Evalúa un caso analizado y retorna su puntaje ponderado y decisión (# AC-1 a # AC-5)."""
    try:
        resultado = evaluar_caso(caso)  # AC-1, AC-2, AC-3, AC-4, AC-5
        return resultado.model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
