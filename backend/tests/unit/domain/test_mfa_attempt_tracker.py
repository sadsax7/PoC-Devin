"""
Tests unitarios para MfaAttemptTracker (servicio de dominio).

Cubre: tracking, bloqueo, limpieza, ventana de tiempo.
Referencia: HU-BE-02 AC#2, BACKEND-GUIDELINES.md §5.1.7.1
"""

from __future__ import annotations

import time

from app.domain.services.mfa_attempt_tracker import MfaAttemptTracker

# ============================================================
# Positivos (happy path)
# ============================================================


class TestMfaAttemptTrackerBasic:
    """Tests básicos del tracker."""

    def test_is_blocked_when_no_failures_then_false(self) -> None:
        """Usuario sin fallos no está bloqueado."""
        tracker = MfaAttemptTracker()
        assert tracker.is_blocked("user1") is False

    def test_record_failure_when_first_then_returns_remaining(self) -> None:
        """Primer fallo retorna max_attempts - 1."""
        tracker = MfaAttemptTracker(max_attempts=3)
        remaining = tracker.record_failure("user1")
        assert remaining == 2

    def test_clear_when_called_then_resets(self) -> None:
        """clear() elimina el registro del usuario."""
        tracker = MfaAttemptTracker()
        tracker.record_failure("user1")
        tracker.clear("user1")
        assert tracker.is_blocked("user1") is False

    def test_clear_when_user_not_tracked_then_no_error(self) -> None:
        """clear() de usuario no rastreado no lanza error."""
        tracker = MfaAttemptTracker()
        tracker.clear("nonexistent")  # Should not raise


# ============================================================
# Brute-force blocking
# ============================================================


class TestMfaAttemptTrackerBlocking:
    """Tests de bloqueo por fuerza bruta."""

    def test_is_blocked_when_max_attempts_reached_then_true(self) -> None:
        """Bloqueo tras max_attempts fallos."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user1")
        tracker.record_failure("user1")
        tracker.record_failure("user1")
        assert tracker.is_blocked("user1") is True

    def test_record_failure_when_last_attempt_then_returns_zero(self) -> None:
        """Último intento retorna 0 restantes."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user1")
        tracker.record_failure("user1")
        remaining = tracker.record_failure("user1")
        assert remaining == 0

    def test_is_blocked_when_one_less_than_max_then_false(self) -> None:
        """Con max_attempts-1 fallos, aún no bloqueado."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user1")
        tracker.record_failure("user1")
        assert tracker.is_blocked("user1") is False


# ============================================================
# Ventana de tiempo
# ============================================================


class TestMfaAttemptTrackerWindow:
    """Tests de ventana temporal."""

    def test_is_blocked_when_window_expired_then_false(self) -> None:
        """Bloqueo expira tras la ventana de tiempo."""
        tracker = MfaAttemptTracker(max_attempts=3, window_seconds=1.0)
        tracker.record_failure("user1")
        tracker.record_failure("user1")
        tracker.record_failure("user1")

        # Simular que la ventana expiró
        record = tracker._attempts["user1"]
        record.last_attempt = time.monotonic() - 2.0

        assert tracker.is_blocked("user1") is False

    def test_record_failure_when_window_expired_then_resets(self) -> None:
        """Fallo tras ventana expirada reinicia conteo."""
        tracker = MfaAttemptTracker(max_attempts=3, window_seconds=1.0)
        tracker.record_failure("user1")
        tracker.record_failure("user1")

        # Simular ventana expirada
        record = tracker._attempts["user1"]
        record.last_attempt = time.monotonic() - 2.0

        remaining = tracker.record_failure("user1")
        # Should have reset: max_attempts(3) - new_count(1) = 2
        assert remaining == 2


# ============================================================
# Aislamiento entre usuarios
# ============================================================


class TestMfaAttemptTrackerIsolation:
    """Tests de aislamiento entre distintos usuarios."""

    def test_block_one_user_does_not_affect_another(self) -> None:
        """Bloqueo de un usuario no afecta a otro."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user_a")
        tracker.record_failure("user_a")
        tracker.record_failure("user_a")

        assert tracker.is_blocked("user_a") is True
        assert tracker.is_blocked("user_b") is False

    def test_clear_one_user_does_not_affect_another(self) -> None:
        """Clear de un usuario preserva estado de otro."""
        tracker = MfaAttemptTracker(max_attempts=3)
        tracker.record_failure("user_a")
        tracker.record_failure("user_b")
        tracker.clear("user_a")

        assert tracker.is_blocked("user_a") is False
        # user_b still has 1 failure
        remaining = tracker.record_failure("user_b")
        assert remaining == 1


# ============================================================
# Edge cases
# ============================================================


class TestMfaAttemptTrackerEdgeCases:
    """Edge cases."""

    def test_max_attempts_one_blocks_immediately(self) -> None:
        """max_attempts=1 bloquea al primer fallo."""
        tracker = MfaAttemptTracker(max_attempts=1)
        remaining = tracker.record_failure("user1")
        assert remaining == 0
        assert tracker.is_blocked("user1") is True

    def test_record_failure_returns_zero_minimum(self) -> None:
        """Intentos restantes nunca negativos."""
        tracker = MfaAttemptTracker(max_attempts=2)
        tracker.record_failure("user1")
        remaining = tracker.record_failure("user1")
        assert remaining == 0
