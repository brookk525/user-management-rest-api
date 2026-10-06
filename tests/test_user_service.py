from unittest.mock import Mock

import pytest

from adapters.interfaces.user_adapter import UserAdapter
from models.create_user_request import CreateUserRequest
from models.update_user_request import UpdateUserRequest
from services.implementations.user_service_impl import UserServiceImpl


@pytest.fixture
def service() -> UserServiceImpl:
    user_service = UserServiceImpl()
    user_service.user_adapter = Mock(spec=UserAdapter)
    return user_service


def test_create_valid_user_calls_adapter(service: UserServiceImpl):
    user = CreateUserRequest("Brooklyn", "brooklyn@example.com")
    service.user_adapter.create_user.return_value = 7

    user_id = service.create_user(user)

    assert user_id == 7
    service.user_adapter.create_user.assert_called_once_with(user)


def test_create_user_rejects_empty_name(service: UserServiceImpl):
    user = CreateUserRequest("", "brooklyn@example.com")

    with pytest.raises(ValueError, match="no pueden estar vacios"):
        service.create_user(user)

    service.user_adapter.create_user.assert_not_called()


def test_create_user_rejects_empty_email(service: UserServiceImpl):
    user = CreateUserRequest("Brooklyn", "")

    with pytest.raises(ValueError, match="no pueden estar vacios"):
        service.create_user(user)

    service.user_adapter.create_user.assert_not_called()


def test_get_missing_user_raises_value_error(service: UserServiceImpl):
    service.user_adapter.get_user.return_value = None

    with pytest.raises(ValueError, match="Usuario no encontrado"):
        service.get_user(999)

    service.user_adapter.get_user.assert_called_once_with(999)


def test_update_user_rejects_empty_name(service: UserServiceImpl):
    user = UpdateUserRequest(1, "", "brooklyn@example.com")

    with pytest.raises(ValueError, match="no pueden estar vacios"):
        service.update_user(user)

    service.user_adapter.update_user.assert_not_called()


def test_update_avatar_rejects_empty_url(service: UserServiceImpl):
    with pytest.raises(ValueError, match="no pueden estar vacios"):
        service.update_avatar_by_email("brooklyn@example.com", "")

    service.user_adapter.update_avatar_by_email.assert_not_called()
