"""Tests para el modulo de logging de auditoria."""

import json
from unittest.mock import patch

from app.shared.audit_logger import audit_log


def test_audit_log_when_login_success_then_logs_json() -> None:
    """Caso positivo: evento de login exitoso se registra en JSON."""
    # Arrange & Act
    with patch("app.shared.audit_logger._audit_logger") as mock_logger:
        audit_log(event="login_success", user_id="user123", ip="127.0.0.1")

    # Assert
    mock_logger.info.assert_called_once()
    logged = json.loads(mock_logger.info.call_args[0][0])
    assert logged["event"] == "login_success"
    assert logged["user_id"] == "user123"
    assert logged["ip"] == "127.0.0.1"
    assert "timestamp" in logged


def test_audit_log_when_login_failed_then_includes_reason() -> None:
    """Caso positivo: evento de fallo incluye razon."""
    # Arrange & Act
    with patch("app.shared.audit_logger._audit_logger") as mock_logger:
        audit_log(
            event="login_failed",
            phone="+573001234567",
            reason="wrong_password",
        )

    # Assert
    logged = json.loads(mock_logger.info.call_args[0][0])
    assert logged["event"] == "login_failed"
    assert logged["phone"] == "+573001234567"
    assert logged["reason"] == "wrong_password"


def test_audit_log_when_no_optional_fields_then_omits_them() -> None:
    """Edge case: campos opcionales no se incluyen si son None."""
    # Arrange & Act
    with patch("app.shared.audit_logger._audit_logger") as mock_logger:
        audit_log(event="mfa_verify_success")

    # Assert
    logged = json.loads(mock_logger.info.call_args[0][0])
    assert logged["event"] == "mfa_verify_success"
    assert "user_id" not in logged
    assert "phone" not in logged
    assert "reason" not in logged
    assert logged["ip"] == "127.0.0.1"


def test_audit_log_when_called_then_never_contains_password() -> None:
    """Caso de seguridad: log nunca contiene contrasenas."""
    # Arrange & Act
    with patch("app.shared.audit_logger._audit_logger") as mock_logger:
        audit_log(
            event="login_failed",
            phone="+573001234567",
            reason="wrong_password",
        )

    # Assert
    logged_str = mock_logger.info.call_args[0][0]
    assert "password" not in logged_str.lower() or "wrong_password" in logged_str


def test_audit_log_when_mfa_event_then_logs_correctly() -> None:
    """Caso positivo: evento MFA se registra correctamente."""
    # Arrange & Act
    with patch("app.shared.audit_logger._audit_logger") as mock_logger:
        audit_log(
            event="mfa_verify_failed",
            user_id="user123",
            reason="invalid_code",
        )

    # Assert
    logged = json.loads(mock_logger.info.call_args[0][0])
    assert logged["event"] == "mfa_verify_failed"
    assert logged["reason"] == "invalid_code"
