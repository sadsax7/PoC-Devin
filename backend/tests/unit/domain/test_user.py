"""
Tests unitarios para la entidad User y el enum KycStatus.

Cubre: positivos, negativos, edge cases, transiciones de estado.
Referencia: HU-BE-01 AC#1, BACKEND-GUIDELINES.md §5.3.2
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.domain.entities.user import KycStatus, User

# ============================================================
# KycStatus Enum
# ============================================================


class TestKycStatus:
    """Tests para el enum KycStatus."""

    def test_kyc_status_values_exist(self) -> None:
        """Verifica que existen los tres valores definidos en AC#1."""
        assert KycStatus.PENDING.value == "pending"
        assert KycStatus.APPROVED.value == "approved"
        assert KycStatus.REJECTED.value == "rejected"

    def test_kyc_status_is_string_enum(self) -> None:
        """El enum hereda de str para serialización JSON directa."""
        assert isinstance(KycStatus.PENDING, str)
        assert KycStatus.PENDING.value == "pending"


# ============================================================
# User entity — positivos
# ============================================================


class TestUserCreation:
    """Tests positivos de creación de User."""

    def test_user_when_minimal_fields_then_created(self) -> None:
        """Crea usuario solo con campos requeridos."""
        user = User(
            phone="+573001234567",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.PENDING,
        )
        assert user.phone == "+573001234567"
        assert user.password_hash == "$argon2id$hash"
        assert user.kyc_status == KycStatus.PENDING
        assert user.id is None
        assert user.email is None
        assert user.name is None
        assert user.mfa_enabled is False

    def test_user_when_all_fields_then_created(self) -> None:
        """Crea usuario con todos los campos opcionales."""
        user = User(
            phone="+573001234567",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.APPROVED,
            id="507f1f77bcf86cd799439011",
            email="test@example.com",
            name="Test User",
            mfa_enabled=True,
        )
        assert user.id == "507f1f77bcf86cd799439011"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.mfa_enabled is True

    def test_user_created_at_is_auto_set(self) -> None:
        """created_at se asigna automáticamente al crear el usuario."""
        before = datetime.now(tz=timezone.utc)
        user = User(
            phone="+573001234567",
            password_hash="$argon2id$hash",
            kyc_status=KycStatus.PENDING,
        )
        after = datetime.now(tz=timezone.utc)
        # created_at puede ser naive o aware — solo comprobamos cercanía
        assert before.timestamp() <= user.created_at.timestamp() + 1
        assert user.created_at.timestamp() <= after.timestamp() + 1


# ============================================================
# User.is_kyc_rejected — transiciones de estado
# ============================================================


class TestUserKycRejected:
    """Tests de transición de estado KYC."""

    def test_is_kyc_rejected_when_rejected_then_true(self) -> None:
        user = User(
            phone="+573001234500",
            password_hash="hash",
            kyc_status=KycStatus.REJECTED,
        )
        assert user.is_kyc_rejected() is True

    def test_is_kyc_rejected_when_approved_then_false(self) -> None:
        user = User(
            phone="+573001234599",
            password_hash="hash",
            kyc_status=KycStatus.APPROVED,
        )
        assert user.is_kyc_rejected() is False

    def test_is_kyc_rejected_when_pending_then_false(self) -> None:
        user = User(
            phone="+573001234567",
            password_hash="hash",
            kyc_status=KycStatus.PENDING,
        )
        assert user.is_kyc_rejected() is False


# ============================================================
# User.to_dict
# ============================================================


class TestUserToDict:
    """Tests del método to_dict para serialización a MongoDB."""

    def test_to_dict_when_minimal_then_excludes_id_email_name(self) -> None:
        """to_dict excluye id, y excluye email/name cuando son None."""
        user = User(
            phone="+573001234567",
            password_hash="hash",
            kyc_status=KycStatus.PENDING,
        )
        d = user.to_dict()
        assert "id" not in d
        assert "email" not in d
        assert "name" not in d
        assert d["phone"] == "+573001234567"
        assert d["password_hash"] == "hash"
        assert d["kyc_status"] == "pending"
        assert d["mfa_enabled"] is False
        assert "created_at" in d

    def test_to_dict_when_optional_fields_then_includes_them(self) -> None:
        """to_dict incluye email y name cuando tienen valor."""
        user = User(
            phone="+573001234567",
            password_hash="hash",
            kyc_status=KycStatus.APPROVED,
            email="a@b.com",
            name="Alice",
        )
        d = user.to_dict()
        assert d["email"] == "a@b.com"
        assert d["name"] == "Alice"


# ============================================================
# Edge cases
# ============================================================


class TestUserEdgeCases:
    """Edge cases para la entidad User."""

    def test_user_when_empty_string_email_then_stored(self) -> None:
        """Un email vacío se almacena (la validación se hace en use case)."""
        user = User(
            phone="+573001234567",
            password_hash="hash",
            kyc_status=KycStatus.PENDING,
            email="",
        )
        assert user.email == ""

    def test_user_when_kyc_status_string_then_valid(self) -> None:
        """KycStatus acepta comparación con strings por ser str enum."""
        user = User(
            phone="+573001234567",
            password_hash="hash",
            kyc_status=KycStatus.PENDING,
        )
        assert user.kyc_status == "pending"
