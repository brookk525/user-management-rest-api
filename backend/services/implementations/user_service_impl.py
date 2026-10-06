# Autor: Brooklyn Muñoz

from adapters.implementations.user_no_orm_adapter import UserNoOrmAdapter
from adapters.interfaces.user_adapter import UserAdapter
from models.create_user_request import CreateUserRequest
from models.update_user_request import UpdateUserRequest
from models.user import User
from services.interfaces.user_service import UserService


class UserServiceImpl(UserService):
    def __init__(self):
        self.user_adapter: UserAdapter = UserNoOrmAdapter()

    def create_user(self, user: CreateUserRequest) -> int:
        if user.name == "" or user.email == "":
            raise ValueError("Los datos del usuario no pueden estar vacios")

        return self.user_adapter.create_user(user)

    def get_user(self, user_id: int) -> User:
        user: User | None = self.user_adapter.get_user(user_id)
        if user is None:
            raise ValueError("Usuario no encontrado con la id proporcionada")

        return user

    def update_user(self, user: UpdateUserRequest):
        if user.name == "" or user.email == "":
            raise ValueError("Los datos del usuario no pueden estar vacios")

        self.user_adapter.update_user(user)

    def update_avatar_by_email(self, email: str, avatar_url: str):
        if email == "" or avatar_url == "":
            raise ValueError("Los datos del avatar no pueden estar vacios")

        self.user_adapter.update_avatar_by_email(email, avatar_url)

    def delete_user(self, user_id: int):
        self.user_adapter.delete_user(user_id)

    def list_users(self) -> list[int]:
        return self.user_adapter.list_users()
