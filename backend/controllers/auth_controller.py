# Autor: Brooklyn Muñoz

from fastapi import HTTPException

from app import App
from models.create_user_request import CreateUserRequest
from models.login_request import LoginRequest
from models.register_request import RegisterRequest
from models.register_response import RegisterResponse
from models.token_response import TokenResponse

app_instance: App = App.get_instance()
app = app_instance.app


@app.post("/auth/login")
def login(login_request: LoginRequest) -> TokenResponse:
    try:
        if login_request is None:
            raise HTTPException(status_code = 400, detail = "Introduce datos de login validos")
        return app_instance.auth_service.login(login_request.email, login_request.password)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code = 401, detail = "No se ha podido iniciar sesion")


@app.post("/auth/register")
def register(register_request: RegisterRequest) -> RegisterResponse:
    try:
        if register_request is None:
            raise HTTPException(status_code = 400, detail = "Introduce datos de registro validos")

        app_instance.auth_service.register(register_request.name, register_request.email, register_request.password)

        create_user_request: CreateUserRequest = CreateUserRequest(register_request.name, register_request.email)
        user_id: int = app_instance.user_service.create_user(create_user_request)
        return RegisterResponse(user_id)
    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(status_code = 400, detail = str(error))
