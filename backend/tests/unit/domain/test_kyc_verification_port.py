"""Tests unitarios para el mock del servicio KYC."""

import pytest

from app.adapters.outbound.kyc.kyc_client_impl import MockKycClient


@pytest.mark.asyncio
async def test_kyc_when_phone_ends_00_then_rejected() -> None:
    """Caso positivo: telefono terminado en 00 es rechazado."""
    # Arrange
    client = MockKycClient()

    # Act
    result = await client.verify("+573001234500")

    # Assert
    assert result == "rejected"


@pytest.mark.asyncio
async def test_kyc_when_phone_ends_99_then_approved() -> None:
    """Caso positivo: telefono terminado en 99 es aprobado."""
    # Arrange
    client = MockKycClient()

    # Act
    result = await client.verify("+573001234599")

    # Assert
    assert result == "approved"


@pytest.mark.asyncio
async def test_kyc_when_phone_ends_other_then_pending() -> None:
    """Caso positivo: telefono terminado en otro sufijo es pendiente."""
    # Arrange
    client = MockKycClient()

    # Act
    result = await client.verify("+573001234567")

    # Assert
    assert result == "pending"


@pytest.mark.asyncio
async def test_kyc_when_phone_ends_01_then_pending() -> None:
    """Edge case: telefono terminado en 01 es pendiente."""
    # Arrange
    client = MockKycClient()

    # Act
    result = await client.verify("+573001234501")

    # Assert
    assert result == "pending"


@pytest.mark.asyncio
async def test_kyc_when_phone_ends_100_then_rejected() -> None:
    """Edge case: telefono terminado en 100 (contiene 00) es rejected."""
    # Arrange
    client = MockKycClient()

    # Act
    result = await client.verify("+573001234100")

    # Assert
    assert result == "rejected"
