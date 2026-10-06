# Autor: Brooklyn Muñoz

import json
import os
from pathlib import Path
from urllib import request
from urllib.error import HTTPError

from dotenv import load_dotenv

from models.auth_user import AuthUser
from models.token_response import TokenResponse
from services.interfaces.auth_service import AuthService


class AuthServiceImpl(AuthService):
    def __init__(self):
        # aqui cargo el .env para no escribir las claves de Supabase dentro del codigo.
        env_path: Path = Path(__file__).parents[3] / ".env"
        load_dotenv(env_path)
        self.supabase_url: str | None = os.getenv("SUPABASE_URL")
        self.supabase_anon_key: str | None = os.getenv("SUPABASE_ANON_KEY")

    def login(self, email: str, password: str) -> TokenResponse:
        if self.supabase_url is None or self.supabase_anon_key is None:
            raise ValueError("Faltan las variables de entorno de Supabase")

        # aqui uso la URL de Supabase para iniciar sesion con email y contraseña.
        url: str = f"{self.supabase_url}/auth/v1/token?grant_type=password"
        body: dict[str, str] = {
            "email": email,
            "password": password,
        }

        try:
            response = self.send_request(url, body)
            return TokenResponse(response["access_token"], response["token_type"])
        except HTTPError:
            raise ValueError("Email o contraseña incorrectos")

    def register(self, name: str, email: str, password: str):
        if self.supabase_url is None or self.supabase_anon_key is None:
            raise ValueError("Faltan las variables de entorno de Supabase")

        # aqui uso la URL de Supabase para registrar un usuario en Authentication.
        url: str = f"{self.supabase_url}/auth/v1/signup"
        body: dict = {
            "email": email,
            "password": password,
            "data": {
                "name": name,
            },
        }

        try:
            self.send_request(url, body)
        except HTTPError as error:
            error_message: str = error.read().decode("utf-8")
            raise ValueError(error_message)

    def validate_token(self, authorization: str) -> AuthUser:
        if self.supabase_url is None or self.supabase_anon_key is None:
            raise ValueError("Faltan las variables de entorno de Supabase")

        if authorization is None or not authorization.startswith("Bearer "):
            raise ValueError("Token no valido")

        # aqui si el token es valido, Supabase devuelve los datos del usuario logeado.
        url: str = f"{self.supabase_url}/auth/v1/user"
        headers: dict[str, str] = {
            "apikey": self.supabase_anon_key,
            "Authorization": authorization,
        }

        supabase_request = request.Request(url, headers = headers, method = "GET")

        try:
            with request.urlopen(supabase_request) as response:
                response_data: str = response.read().decode("utf-8")
                user_data: dict = json.loads(response_data)
                return AuthUser(user_data["id"], user_data["email"])
        except HTTPError:
            raise ValueError("Token no valido")

    def update_profile_avatar(self, user_id: str, avatar_url: str, authorization: str):
        if self.supabase_url is None or self.supabase_anon_key is None:
            raise ValueError("Faltan las variables de entorno de Supabase")

        # aqui actualizo la tabla publica profiles con la URL del avatar.
        url: str = f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}"
        data: bytes = json.dumps({"avatar_url": avatar_url}).encode("utf-8")
        headers: dict[str, str] = {
            "apikey": self.supabase_anon_key,
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

        supabase_request = request.Request(url, data = data, headers = headers, method = "PATCH")

        try:
            with request.urlopen(supabase_request) as response:
                response.read()
        except HTTPError as error:
            error_message: str = error.read().decode("utf-8")
            raise ValueError(error_message)

    def delete_profile(self, user_id: str, authorization: str):
        if self.supabase_url is None or self.supabase_anon_key is None:
            raise ValueError("Faltan las variables de entorno de Supabase")

        # aqui borro solo el perfil publico. El usuario de Auth requiere clave admin.
        url: str = f"{self.supabase_url}/rest/v1/profiles?id=eq.{user_id}"
        headers: dict[str, str] = {
            "apikey": self.supabase_anon_key,
            "Authorization": authorization,
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

        supabase_request = request.Request(url, headers = headers, method = "DELETE")

        try:
            with request.urlopen(supabase_request) as response:
                response_data: str = response.read().decode("utf-8")
                deleted_profiles = json.loads(response_data)
                if len(deleted_profiles) == 0:
                    raise ValueError("No se ha podido borrar el perfil de Supabase")
        except HTTPError as error:
            error_message: str = error.read().decode("utf-8")
            raise ValueError(error_message)

    def send_request(self, url: str, body: dict):
        # aqui preparo una peticion comun para mandar JSON a Supabase.
        data: bytes = json.dumps(body).encode("utf-8")
        headers: dict[str, str] = {
            "apikey": self.supabase_anon_key,
            "Authorization": f"Bearer {self.supabase_anon_key}",
            "Content-Type": "application/json",
        }

        supabase_request = request.Request(url, data = data, headers = headers, method = "POST")

        with request.urlopen(supabase_request) as response:
            response_data: str = response.read().decode("utf-8")
            return json.loads(response_data)
