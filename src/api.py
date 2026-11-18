"""API REST base de MIRA (FastAPI)."""

from fastapi import FastAPI, HTTPException
from src.engine import estado_base_motor
from src.repository import ORGANIZACIONES_UMBRALES, obtener_umbrales_organizacion

app = FastAPI(
    title="MIRA · Plataforma Inteligente Multimodal de Decisión",
    version="3.0.0-base",
    description="Servicio backend de MIRA para gestión de umbrales por cliente y decisión de casos.",
)


@app.get("/health")
def health_check() -> dict:
    """Endpoint de salud del servicio base."""
    return estado_base_motor()


@app.get("/api/organizaciones")
def listar_organizaciones() -> list:
    """Lista las organizaciones cliente y sus umbrales actuales."""
    return [cfg.model_dump() for cfg in ORGANIZACIONES_UMBRALES.values()]


@app.get("/api/organizaciones/{org_id}/umbrales")
def consultar_umbrales(org_id: str) -> dict:
    """Consulta los umbrales de una organización cliente específica."""
    try:
        return obtener_umbrales_organizacion(org_id).model_dump()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
