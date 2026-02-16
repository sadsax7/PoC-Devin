"""Modulo de logging de auditoria estructurado.

Provee funciones para registrar eventos de seguridad
en formato JSON estructurado sin exponer datos sensibles.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

_audit_logger = logging.getLogger("audit")


def audit_log(
    event: str,
    user_id: Optional[str] = None,
    phone: Optional[str] = None,
    reason: Optional[str] = None,
    ip: str = "127.0.0.1",
) -> None:
    """Registra un evento de auditoria en formato JSON estructurado.

    PROHIBIDO: No registrar contrasenas, hashes ni tokens completos.

    Args:
        event: Tipo de evento (login_success, login_failed, etc).
        user_id: Identificador del usuario (opcional).
        phone: Numero de telefono (opcional).
        reason: Razon del evento (opcional).
        ip: Direccion IP del cliente.
    """
    log_entry = {
        "event": event,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ip": ip,
    }

    if user_id is not None:
        log_entry["user_id"] = user_id

    if phone is not None:
        log_entry["phone"] = phone

    if reason is not None:
        log_entry["reason"] = reason

    _audit_logger.info(json.dumps(log_entry))
