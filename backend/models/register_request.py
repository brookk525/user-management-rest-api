# Autor: Brooklyn Muñoz

from dataclasses import dataclass


@dataclass
class RegisterRequest:
    name: str
    email: str
    password: str
