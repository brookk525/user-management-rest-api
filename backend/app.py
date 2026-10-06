# Autor: Brooklyn Muñoz

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.implementations.auth_service_impl import AuthServiceImpl
from services.implementations.storage_service_impl import StorageServiceImpl
from services.implementations.user_service_impl import UserServiceImpl


class App:
    __instance: App | None = None

    def __init__(self):
        self.app: FastAPI = FastAPI()
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins = ["*"],
            allow_credentials = True,
            allow_methods = ["*"],
            allow_headers = ["*"],
        )
        self.auth_service: AuthServiceImpl = AuthServiceImpl()
        self.storage_service: StorageServiceImpl = StorageServiceImpl()
        self.user_service: UserServiceImpl = UserServiceImpl()

    @staticmethod
    def get_instance() -> App:
        if App.__instance is None:
            App.__instance = App()
        return App.__instance
