"""Repositorio en memoria de catálogo de señales (CAT-SEN v3) y organizaciones cliente de MIRA."""

from typing import Dict
from src.models import ConfiguracionUmbrales

# Pesos oficiales de las señales numéricas para el cálculo del puntaje de confianza (suman 1.0)
PESOS_SENALES: Dict[str, float] = {
    "DOC_AUT": 0.35,      # Autenticidad documental
    "BIO_ROSTRO": 0.30,   # Coincidencia biométrica de rostro
    "CRUCE_MONTO": 0.20,  # Cruce de montos entre fuentes
    "CRUCE_FECHA": 0.15,  # Cruce de fechas entre fuentes
}

# Mínimos obligatorios por señal individual según POL-DEC v2 §3
MINIMOS_POR_SENAL: Dict[str, float] = {
    "DOC_AUT": 70.0,
    "BIO_ROSTRO": 75.0,
    "CRUCE_MONTO": 60.0,
    "CRUCE_FECHA": 60.0,
}

# Catálogo oficial de señales de fraude según CAT-SEN v3 §6
CATALOGO_SENALES_FRAUDE = {
    "FRA_EDICION",
    "FRA_MEMORIA",
    "FRA_SINTETICO",
}

# Organizaciones cliente registradas en MIRA (DOC-MIRA v1.4)
ORGANIZACIONES_UMBRALES: Dict[str, ConfiguracionUmbrales] = {
    "ORG-01": ConfiguracionUmbrales(
        org_id="ORG-01",
        nombre_org="Seguros Cordillera Austral",
        umbral_aprobacion=85.0,
        umbral_rechazo=60.0,
        version=1,
        autor_ultimo_cambio="admin_org01",
    ),
    "ORG-02": ConfiguracionUmbrales(
        org_id="ORG-02",
        nombre_org="Clínica Bahía Serena",
        umbral_aprobacion=80.0,
        umbral_rechazo=50.0,
        version=1,
        autor_ultimo_cambio="admin_org02",
    ),
    "ORG-03": ConfiguracionUmbrales(
        org_id="ORG-03",
        nombre_org="Banco Mirador del Sur",
        umbral_aprobacion=90.0,
        umbral_rechazo=65.0,
        version=1,
        autor_ultimo_cambio="admin_org03",
    ),
}


def obtener_umbrales_organizacion(org_id: str) -> ConfiguracionUmbrales:
    """Devuelve la configuración vigente de umbrales para una organización cliente."""
    if org_id not in ORGANIZACIONES_UMBRALES:  # AC-5
        raise KeyError(f"La organización '{org_id}' no existe en MIRA.")
    return ORGANIZACIONES_UMBRALES[org_id]  # AC-5


def actualizar_umbrales_organizacion(
    org_id: str,
    umbral_aprobacion: float,
    umbral_rechazo: float,
    autor: str = "admin_cliente",
) -> ConfiguracionUmbrales:
    """Actualiza los umbrales propios de una organización cliente e incrementa su versión (# AC-6)."""
    actual = obtener_umbrales_organizacion(org_id)  # AC-5

    if not (0.0 <= umbral_aprobacion <= 100.0) or not (0.0 <= umbral_rechazo <= 100.0):  # AC-6
        raise ValueError("Los umbrales deben estar dentro del rango [0.0, 100.0].")

    if umbral_rechazo >= umbral_aprobacion:  # AC-6
        raise ValueError("El umbral de rechazo debe ser estrictamente menor al umbral de aprobación.")

    nueva_cfg = ConfiguracionUmbrales(
        org_id=actual.org_id,
        nombre_org=actual.nombre_org,
        umbral_aprobacion=round(float(umbral_aprobacion), 2),
        umbral_rechazo=round(float(umbral_rechazo), 2),
        version=actual.version + 1,  # AC-6
        autor_ultimo_cambio=autor.strip() or "admin_cliente",
    )
    ORGANIZACIONES_UMBRALES[org_id] = nueva_cfg
    return nueva_cfg


def reiniciar_repositorio_base() -> None:
    """Restaura los valores iniciales por defecto para pruebas deterministas."""
    ORGANIZACIONES_UMBRALES["ORG-01"] = ConfiguracionUmbrales(
        org_id="ORG-01",
        nombre_org="Seguros Cordillera Austral",
        umbral_aprobacion=85.0,
        umbral_rechazo=60.0,
        version=1,
        autor_ultimo_cambio="admin_org01",
    )
    ORGANIZACIONES_UMBRALES["ORG-02"] = ConfiguracionUmbrales(
        org_id="ORG-02",
        nombre_org="Clínica Bahía Serena",
        umbral_aprobacion=80.0,
        umbral_rechazo=50.0,
        version=1,
        autor_ultimo_cambio="admin_org02",
    )
    ORGANIZACIONES_UMBRALES["ORG-03"] = ConfiguracionUmbrales(
        org_id="ORG-03",
        nombre_org="Banco Mirador del Sur",
        umbral_aprobacion=90.0,
        umbral_rechazo=65.0,
        version=1,
        autor_ultimo_cambio="admin_org03",
    )
