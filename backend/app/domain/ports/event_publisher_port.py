"""
Puerto: EventPublisherPort.

Abstracción para publicación de eventos de dominio.
Para el PoC se implementa en memoria (log).

Referencia: BACKEND-GUIDELINES.md §2.1, §3.5
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class EventPublisherPort(ABC):
    """Contrato para publicación de eventos de dominio."""

    @abstractmethod
    async def publish(self, event_name: str, payload: dict[str, object]) -> None:
        """Publica un evento de dominio.

        Args:
            event_name: Nombre del evento (ej: 'UserRegistered').
            payload: Datos del evento.
        """
        ...
