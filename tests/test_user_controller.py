import importlib
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from models.auth_user import AuthUser
from models.update_user_request import UpdateUserRequest
from models.user import User


class FakeApi:
    def __getattr__(self, name):
        return lambda *args, **kwargs: lambda function: function


fake_app_instance = SimpleNamespace(
    app=FakeApi(),
    auth_service=Mock(),
    user_service=Mock(),
)


class FakeApp:
    @staticmethod
    def get_instance():
        return fake_app_instance


fake_app_module = ModuleType("app")
fake_app_module.App = FakeApp
original_app_module = sys.modules.get("app")
sys.modules["app"] = fake_app_module
user_controller = importlib.import_module("controllers.user_controller")

if original_app_module is None:
    del sys.modules["app"]
else:
    sys.modules["app"] = original_app_module


@pytest.fixture
def services(monkeypatch):
    auth_service = Mock()
    user_service = Mock()
    monkeypatch.setattr(user_controller.app_instance, "auth_service", auth_service)
    monkeypatch.setattr(user_controller.app_instance, "user_service", user_service)
    return auth_service, user_service


def test_check_token_without_header_returns_401(services):
    auth_service, _ = services

    with pytest.raises(HTTPException) as error:
        user_controller.check_token(None)

    assert error.value.status_code == 401
    auth_service.validate_token.assert_not_called()


def test_check_token_rejected_by_supabase_returns_401(services):
    auth_service, _ = services
    auth_service.validate_token.side_effect = ValueError("Token no valido")

    with pytest.raises(HTTPException) as error:
        user_controller.check_token("Bearer invalid")

    assert error.value.status_code == 401
    auth_service.validate_token.assert_called_once_with("Bearer invalid")


def test_owner_is_allowed(services):
    _, user_service = services
    auth_user = AuthUser("supabase-id", "owner@example.com")
    stored_user = User(5, "Owner", "owner@example.com")
    user_service.get_user.return_value = stored_user

    result = user_controller.check_user_ownership(5, auth_user)

    assert result is stored_user
    user_service.get_user.assert_called_once_with(5)


def test_different_owner_returns_403(services):
    _, user_service = services
    auth_user = AuthUser("attacker-id", "attacker@example.com")
    user_service.get_user.return_value = User(5, "Owner", "owner@example.com")

    with pytest.raises(HTTPException) as error:
        user_controller.check_user_ownership(5, auth_user)

    assert error.value.status_code == 403


def test_missing_user_returns_404(services):
    _, user_service = services
    auth_user = AuthUser("supabase-id", "owner@example.com")
    user_service.get_user.side_effect = ValueError("Usuario no encontrado")

    with pytest.raises(HTTPException) as error:
        user_controller.check_user_ownership(999, auth_user)

    assert error.value.status_code == 404


def test_update_rejects_local_email_change(services):
    auth_service, user_service = services
    auth_user = AuthUser("supabase-id", "owner@example.com")
    auth_service.validate_token.return_value = auth_user
    user_service.get_user.return_value = User(5, "Owner", "owner@example.com")
    update_request = UpdateUserRequest(5, "Owner", "changed@example.com")

    with pytest.raises(HTTPException) as error:
        user_controller.update_user(update_request, "Bearer valid")

    assert error.value.status_code == 400
    user_service.update_user.assert_not_called()


def test_delete_other_user_stops_before_external_changes(services):
    auth_service, user_service = services
    auth_user = AuthUser("attacker-id", "attacker@example.com")
    auth_service.validate_token.return_value = auth_user
    user_service.get_user.return_value = User(5, "Owner", "owner@example.com")

    with pytest.raises(HTTPException) as error:
        user_controller.delete_user(5, "Bearer valid")

    assert error.value.status_code == 403
    auth_service.delete_profile.assert_not_called()
    user_service.delete_user.assert_not_called()
