"""
Adapter: InMemoryEventPublisher.

Implementación en memoria del puerto EventPublisherPort.
Para el PoC registra eventos en una lista interna (testeable).

Referencia: BACKEND-GUIDELINES.md §2.4, §3.5
"""

from __future__ import annotations

import logging
from typing import Any

from app.domain.ports.event_publisher_port import EventPublisherPort

logger = logging.getLogger(__name__)


class InMemoryEventPublisher(EventPublisherPort):
    """Publicador de eventos en memoria.

    Almacena eventos para testing y logga para observabilidad.
    """

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def publish(self, event_name: str, payload: dict[str, object]) -> None:
        """Publica un evento almacenándolo en memoria.

        Args:
            event_name: Nombre del evento.
            payload: Datos del evento.
        """
        event: dict[str, Any] = {"event": event_name, "payload": payload}
        self.events.append(event)
        logger.info("Event published: %s", event_name)
