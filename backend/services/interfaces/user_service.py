# Autor: Brooklyn Muñoz

from abc import ABC, abstractmethod

from models.create_user_request import CreateUserRequest
from models.update_user_request import UpdateUserRequest
from models.user import User


class UserService(ABC):
    @abstractmethod
    def create_user(self, user: CreateUserRequest) -> int:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        pass

    @abstractmethod
    def update_user(self, user: UpdateUserRequest):
        pass

    @abstractmethod
    def update_avatar_by_email(self, email: str, avatar_url: str):
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def list_users(self) -> list[int]:
        pass
