# Autor: Brooklyn Muñoz

from fastapi import Header, HTTPException

from app import App
from models.auth_user import AuthUser
from models.create_user_request import CreateUserRequest
from models.message_response import MessageResponse
from models.update_user_request import UpdateUserRequest
from models.user import User
from models.user_response import UserResponse

app_instance: App = App.get_instance()
app = app_instance.app


def check_token(authorization: str | None) -> AuthUser:
    if authorization is None:
        raise HTTPException(status_code = 401, detail = "Falta el token")
    try:
        return app_instance.auth_service.validate_token(authorization)
    except Exception:
        raise HTTPException(status_code = 401, detail = "Token no valido")


def check_user_ownership(user_id: int, auth_user: AuthUser) -> User:
    try:
        user: User = app_instance.user_service.get_user(user_id)
    except ValueError:
        raise HTTPException(status_code = 404, detail = "Usuario no encontrado")

    if user.email != auth_user.email:
        raise HTTPException(status_code = 403, detail = "No tienes permiso para modificar este usuario")

    return user


@app.post("/users")
def create_user(user: CreateUserRequest) -> int:
    try:
        if user is None:
            raise HTTPException(status_code = 400, detail = "Introduce un usuario valido")
        return app_instance.user_service.create_user(user)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code = 400, detail = "No se ha podido crear el usuario")


@app.get("/user_info")
def get_user_by_query(id: int) -> UserResponse:
    try:
        user = app_instance.user_service.get_user(id)
        return UserResponse(user.id, user.name, user.email, user.created_at, user.avatar_url)
    except Exception:
        raise HTTPException(status_code = 404, detail = "No se ha podido encontrar el usuario con esa id")


@app.get("/users/{id}")
def get_user_by_path(id: int) -> UserResponse:
    try:
        user = app_instance.user_service.get_user(id)
        return UserResponse(user.id, user.name, user.email, user.created_at, user.avatar_url)
    except Exception:
        raise HTTPException(status_code = 404, detail = "No se ha podido encontrar el usuario con esa id")


@app.get("/list_users")
def list_users() -> list[int]:
    try:
        return app_instance.user_service.list_users()
    except Exception:
        raise HTTPException(status_code = 500, detail = "No se ha podido obtener la lista de usuarios")


@app.put("/update_user")
def update_user(user: UpdateUserRequest, authorization: str | None = Header(None)) -> MessageResponse:
    try:
        if user is None:
            raise HTTPException(status_code = 400, detail = "Introduce un usuario valido")

        auth_user: AuthUser = check_token(authorization)
        current_user: User = check_user_ownership(user.id, auth_user)

        if user.email != current_user.email:
            raise HTTPException(
                status_code = 400,
                detail = "El correo se gestiona mediante Supabase Auth y no se puede modificar aqui",
            )

        app_instance.user_service.update_user(user)
        return MessageResponse("Usuario actualizado")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code = 404, detail = "No se ha podido encontrar el usuario con esa id")


@app.delete("/delete_user")
def delete_user(id: int, authorization: str | None = Header(None)) -> MessageResponse:
    try:
        auth_user: AuthUser = check_token(authorization)
        check_user_ownership(id, auth_user)
        supabase_user_id: str = auth_user.id
        app_instance.auth_service.delete_profile(supabase_user_id, authorization)
        app_instance.user_service.delete_user(id)
        return MessageResponse("Usuario eliminado")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code = 404, detail = "No se ha podido encontrar el usuario con esa id")
