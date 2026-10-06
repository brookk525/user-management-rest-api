# Autor: Brooklyn Muñoz

from abc import ABC, abstractmethod

from models.auth_user import AuthUser
from models.token_response import TokenResponse


class AuthService(ABC):
    @abstractmethod
    def login(self, email: str, password: str) -> TokenResponse:
        pass

    @abstractmethod
    def register(self, name: str, email: str, password: str):
        pass

    @abstractmethod
    def validate_token(self, authorization: str) -> AuthUser:
        pass

    @abstractmethod
    def update_profile_avatar(self, user_id: str, avatar_url: str, authorization: str):
        pass

    @abstractmethod
    def delete_profile(self, user_id: str, authorization: str):
        pass
