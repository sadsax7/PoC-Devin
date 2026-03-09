"""
Servicio de dominio: MfaAttemptTracker.

Rastrea intentos fallidos de verificación MFA por usuario
para protección contra fuerza bruta.

Referencia: HU-BE-02 AC#2 (protección contra fuerza bruta).
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class _AttemptRecord:
    """Registro interno de intentos MFA para un usuario."""

    count: int = 0
    last_attempt: float = 0.0


class MfaAttemptTracker:
    """Rastrea intentos fallidos de MFA en memoria.

    Limita a ``max_attempts`` intentos por usuario dentro de una
    ventana de ``window_seconds`` segundos.

    Attributes:
        max_attempts: Máximo de intentos antes de bloqueo.
        window_seconds: Ventana de tiempo para el conteo.
    """

    def __init__(
        self,
        max_attempts: int = 3,
        window_seconds: float = 300.0,
    ) -> None:
        """Inicializa el tracker.

        Args:
            max_attempts: Intentos máximos permitidos.
            window_seconds: Segundos antes de resetear el conteo.
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, _AttemptRecord] = {}

    def is_blocked(self, user_id: str) -> bool:
        """Verifica si un usuario está bloqueado por exceso de intentos.

        Args:
            user_id: Identificador del usuario.

        Returns:
            True si el usuario superó el límite dentro de la ventana.
        """
        record = self._attempts.get(user_id)
        if record is None:
            return False
        if time.monotonic() - record.last_attempt > self.window_seconds:
            del self._attempts[user_id]
            return False
        return record.count >= self.max_attempts

    def record_failure(self, user_id: str) -> int:
        """Registra un intento fallido de MFA.

        Args:
            user_id: Identificador del usuario.

        Returns:
            Número de intentos restantes antes del bloqueo.
        """
        now = time.monotonic()
        record = self._attempts.get(user_id)
        if record is None or now - record.last_attempt > self.window_seconds:
            record = _AttemptRecord(count=0, last_attempt=now)
            self._attempts[user_id] = record
        record.count += 1
        record.last_attempt = now
        remaining = max(0, self.max_attempts - record.count)
        return remaining

    def clear(self, user_id: str) -> None:
        """Limpia el contador de intentos tras verificación exitosa.

        Args:
            user_id: Identificador del usuario.
        """
        self._attempts.pop(user_id, None)
