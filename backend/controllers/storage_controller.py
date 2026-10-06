# Autor: Brooklyn Muñoz

from fastapi import File, Header, HTTPException, UploadFile

from app import App
from models.auth_user import AuthUser
from models.avatar_response import AvatarResponse

app_instance: App = App.get_instance()
app = app_instance.app


def check_token(authorization: str | None) -> AuthUser:
    if authorization is None:
        raise HTTPException(status_code = 401, detail = "Falta el token")
    try:
        return app_instance.auth_service.validate_token(authorization)
    except Exception:
        raise HTTPException(status_code = 401, detail = "Token no valido")


# aqui los ... indican que el archivo es obligatorio.
@app.post("/storage/avatar")
def upload_avatar(file: UploadFile = File(...), authorization: str | None = Header(None)) -> AvatarResponse:
    try:
        auth_user: AuthUser = check_token(authorization)
        if file is None:
            raise HTTPException(status_code = 400, detail = "Introduce un archivo valido")

        content: bytes = file.file.read()
        avatar_url: str = app_instance.storage_service.upload_avatar(file.filename, content, file.content_type)
        user_email: str = auth_user.email
        supabase_user_id: str = auth_user.id
        app_instance.user_service.update_avatar_by_email(user_email, avatar_url)
        app_instance.auth_service.update_profile_avatar(supabase_user_id, avatar_url, authorization)

        return AvatarResponse(avatar_url)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code = 400, detail = "No se ha podido subir el avatar")
