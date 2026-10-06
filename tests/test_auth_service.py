from unittest.mock import Mock

from services.implementations.auth_service_impl import AuthServiceImpl


def test_successful_supabase_login_returns_token(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")
    service = AuthServiceImpl()
    service.send_request = Mock(
        return_value={
            "access_token": "test-access-token",
            "token_type": "bearer",
        }
    )

    token = service.login("brooklyn@example.com", "test-password")

    assert token.access_token == "test-access-token"
    assert token.token_type == "bearer"
    service.send_request.assert_called_once_with(
        "https://project.supabase.co/auth/v1/token?grant_type=password",
        {
            "email": "brooklyn@example.com",
            "password": "test-password",
        },
    )
