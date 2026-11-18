"""Modelos de dominio base de MIRA (CAT-SEN v3 y POL-DEC v2)."""

from typing import Dict, List
from pydantic import BaseModel, Field


class ConfiguracionUmbrales(BaseModel):
    """Umbrales configurables por organización cliente en MIRA."""

    org_id: str = Field(..., description="Identificador único de la organización cliente")
    nombre_org: str = Field(..., description="Nombre oficial de la organización")
    umbral_aprobacion: float = Field(
        default=85.0,
        ge=0.0,
        le=100.0,
        description="Puntaje mínimo para aprobar automáticamente el caso",
    )
    umbral_rechazo: float = Field(
        default=60.0,
        ge=0.0,
        le=100.0,
        description="Puntaje bajo el cual el caso se rechaza o escala según política del cliente",
    )
    version: int = Field(default=1, ge=1, description="Versión de la configuración de umbrales")
    autor_ultimo_cambio: str = Field(default="sistema_inicial")


class ActualizacionUmbralesInput(BaseModel):
    """Datos de entrada para actualizar los umbrales propios de una organización cliente."""

    umbral_aprobacion: float = Field(..., description="Nuevo umbral de aprobación (0 a 100)")
    umbral_rechazo: float = Field(..., description="Nuevo umbral de rechazo (0 a 100)")
    autor: str = Field(default="admin_cliente", description="Usuario que realiza la modificación")


class CasoEntrada(BaseModel):
    """Datos de entrada de un caso analizado por los módulos multimodales de MIRA."""

    caso_id: str = Field(..., description="Identificador único del caso (ej. C-101)")
    org_id: str = Field(..., description="Organización cliente propietaria del caso (ej. ORG-01)")
    senales_numericas: Dict[str, float] = Field(
        default_factory=dict,
        description="Mapa de código de señal numérica (0 a 100) a su valor medido",
    )
    senales_fraude_activas: List[str] = Field(
        default_factory=list,
        description="Lista de códigos de señales de fraude activas (ej. FRA_EDICION)",
    )


class ResultadoDecision(BaseModel):
    """Contrato de salida del motor de decisión de MIRA."""

    caso_id: str
    org_id: str
    puntaje_confianza: float
    decision: str  # "APROBADO", "DERIVADO_A_REVISION", "RECHAZADO"
    motivo: str
    umbral_aprobacion_aplicado: float
    umbral_rechazo_aplicado: float
    version_umbrales: int
    senales_bajo_minimo: List[str] = Field(default_factory=list)
    fraude_detectado: bool = False
    detalle_componentes: Dict[str, float] = Field(default_factory=dict)
