import sqlite3

import pytest

from adapters.implementations.user_no_orm_adapter import UserNoOrmAdapter
from models.create_user_request import CreateUserRequest
from models.update_user_request import UpdateUserRequest


@pytest.fixture
def adapter(tmp_path) -> UserNoOrmAdapter:
    user_adapter = UserNoOrmAdapter()
    user_adapter.database_path = tmp_path / "test.db"
    return user_adapter


def create_user(
    adapter: UserNoOrmAdapter,
    name: str = "Brooklyn",
    email: str = "brooklyn@example.com",
) -> int:
    return adapter.create_user(CreateUserRequest(name, email))


def test_create_table_when_database_is_empty(adapter: UserNoOrmAdapter):
    adapter.create_table()

    with sqlite3.connect(adapter.database_path) as connection:
        table = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'users'"
        ).fetchone()

    assert table == ("users",)


def test_create_user_returns_numeric_id(adapter: UserNoOrmAdapter):
    user_id = create_user(adapter)

    assert isinstance(user_id, int)
    assert user_id > 0


def test_get_existing_user_by_id(adapter: UserNoOrmAdapter):
    user_id = create_user(adapter)

    user = adapter.get_user(user_id)

    assert user is not None
    assert user.id == user_id
    assert user.name == "Brooklyn"
    assert user.email == "brooklyn@example.com"
    assert user.created_at is not None
    assert user.avatar_url is None


def test_get_missing_user_returns_none(adapter: UserNoOrmAdapter):
    user = adapter.get_user(999)

    assert user is None


def test_update_user_name(adapter: UserNoOrmAdapter):
    user_id = create_user(adapter)

    adapter.update_user(
        UpdateUserRequest(user_id, "Brooklyn actualizado", "brooklyn@example.com")
    )

    user = adapter.get_user(user_id)
    assert user is not None
    assert user.name == "Brooklyn actualizado"


def test_update_user_email(adapter: UserNoOrmAdapter):
    user_id = create_user(adapter)

    adapter.update_user(
        UpdateUserRequest(user_id, "Brooklyn", "nuevo@example.com")
    )

    user = adapter.get_user(user_id)
    assert user is not None
    assert user.email == "nuevo@example.com"


def test_update_missing_user_raises_value_error(adapter: UserNoOrmAdapter):
    with pytest.raises(ValueError, match="Usuario no encontrado"):
        adapter.update_user(
            UpdateUserRequest(999, "Inexistente", "missing@example.com")
        )


def test_update_avatar_by_email(adapter: UserNoOrmAdapter):
    user_id = create_user(adapter)
    avatar_url = "https://example.com/avatar.png"

    adapter.update_avatar_by_email("brooklyn@example.com", avatar_url)

    user = adapter.get_user(user_id)
    assert user is not None
    assert user.avatar_url == avatar_url


def test_update_avatar_for_missing_email_raises_value_error(
    adapter: UserNoOrmAdapter,
):
    with pytest.raises(ValueError, match="Usuario no encontrado"):
        adapter.update_avatar_by_email(
            "missing@example.com",
            "https://example.com/avatar.png",
        )


def test_delete_existing_user(adapter: UserNoOrmAdapter):
    user_id = create_user(adapter)

    adapter.delete_user(user_id)

    assert adapter.get_user(user_id) is None


def test_delete_missing_user_raises_value_error(adapter: UserNoOrmAdapter):
    with pytest.raises(ValueError, match="Usuario no encontrado"):
        adapter.delete_user(999)


def test_list_users_returns_all_ids(adapter: UserNoOrmAdapter):
    first_id = create_user(adapter, "Primero", "first@example.com")
    second_id = create_user(adapter, "Segundo", "second@example.com")

    user_ids = adapter.list_users()

    assert set(user_ids) == {first_id, second_id}


def test_list_users_returns_empty_list(adapter: UserNoOrmAdapter):
    user_ids = adapter.list_users()

    assert user_ids == []


def test_updating_one_user_keeps_other_users_unchanged(
    adapter: UserNoOrmAdapter,
):
    first_id = create_user(adapter, "Primero", "first@example.com")
    second_id = create_user(adapter, "Segundo", "second@example.com")

    adapter.update_user(
        UpdateUserRequest(first_id, "Primero actualizado", "first@example.com")
    )

    second_user = adapter.get_user(second_id)
    assert second_user is not None
    assert second_user.name == "Segundo"
    assert second_user.email == "second@example.com"


def test_deleting_one_user_keeps_other_users_unchanged(
    adapter: UserNoOrmAdapter,
):
    first_id = create_user(adapter, "Primero", "first@example.com")
    second_id = create_user(adapter, "Segundo", "second@example.com")

    adapter.delete_user(first_id)

    assert adapter.get_user(first_id) is None
    second_user = adapter.get_user(second_id)
    assert second_user is not None
    assert second_user.name == "Segundo"
