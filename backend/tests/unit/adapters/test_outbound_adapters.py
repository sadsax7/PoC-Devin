"""
Tests unitarios para adaptadores outbound (sin infraestructura externa).

Cubre: PasswordHasherImpl, KycClientMock, InMemoryEventPublisher.
Referencia: BACKEND-GUIDELINES.md §5.3.2
"""

from __future__ import annotations

import pytest

from app.adapters.outbound.kyc.kyc_client_impl import KycClientMock
from app.adapters.outbound.messaging.event_publisher_memory import InMemoryEventPublisher
from app.adapters.outbound.security.password_hasher_impl import PasswordHasherImpl
from app.domain.entities.user import KycStatus

# ============================================================
# PasswordHasherImpl
# ============================================================


class TestPasswordHasherImpl:
    """Tests para el adapter Argon2."""

    def test_hash_password_when_valid_then_returns_hash(self) -> None:
        """hash_password retorna un hash diferente al input."""
        hasher = PasswordHasherImpl()
        result = hasher.hash_password("Str0ng!Pass")
        assert result != "Str0ng!Pass"
        assert len(result) > 0

    def test_verify_password_when_correct_then_true(self) -> None:
        """verify_password retorna True con password correcto."""
        hasher = PasswordHasherImpl()
        hashed = hasher.hash_password("TestPass1!")
        assert hasher.verify_password("TestPass1!", hashed) is True

    def test_verify_password_when_incorrect_then_false(self) -> None:
        """verify_password retorna False con password incorrecto."""
        hasher = PasswordHasherImpl()
        hashed = hasher.hash_password("TestPass1!")
        assert hasher.verify_password("WrongPass1!", hashed) is False

    def test_hash_password_produces_different_hashes(self) -> None:
        """Dos hashes del mismo password deben ser diferentes (salt)."""
        hasher = PasswordHasherImpl()
        h1 = hasher.hash_password("SamePass1!")
        h2 = hasher.hash_password("SamePass1!")
        assert h1 != h2


# ============================================================
# KycClientMock
# ============================================================


class TestKycClientMock:
    """Tests para el mock de KYC."""

    @pytest.mark.asyncio
    async def test_verify_when_phone_ends_00_then_rejected(self) -> None:
        """Teléfono terminado en 00 → REJECTED."""
        kyc = KycClientMock()
        result = await kyc.verify("+573001234500")
        assert result == KycStatus.REJECTED

    @pytest.mark.asyncio
    async def test_verify_when_phone_ends_99_then_approved(self) -> None:
        """Teléfono terminado en 99 → APPROVED."""
        kyc = KycClientMock()
        result = await kyc.verify("+573001234599")
        assert result == KycStatus.APPROVED

    @pytest.mark.asyncio
    async def test_verify_when_phone_ends_other_then_pending(self) -> None:
        """Teléfono con otro sufijo → PENDING."""
        kyc = KycClientMock()
        result = await kyc.verify("+573001234567")
        assert result == KycStatus.PENDING


# ============================================================
# InMemoryEventPublisher
# ============================================================


class TestInMemoryEventPublisher:
    """Tests para el publisher en memoria."""

    @pytest.mark.asyncio
    async def test_publish_when_called_then_stores_event(self) -> None:
        """publish() almacena el evento en la lista interna."""
        pub = InMemoryEventPublisher()
        await pub.publish("TestEvent", {"key": "value"})
        assert len(pub.events) == 1
        assert pub.events[0]["event"] == "TestEvent"
        assert pub.events[0]["payload"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_publish_when_called_twice_then_two_events(self) -> None:
        """Múltiples publicaciones se acumulan."""
        pub = InMemoryEventPublisher()
        await pub.publish("Event1", {"a": "1"})
        await pub.publish("Event2", {"b": "2"})
        assert len(pub.events) == 2

    @pytest.mark.asyncio
    async def test_publish_when_empty_payload_then_stores(self) -> None:
        """Payload vacío es válido."""
        pub = InMemoryEventPublisher()
        await pub.publish("EmptyEvent", {})
        assert pub.events[0]["payload"] == {}
