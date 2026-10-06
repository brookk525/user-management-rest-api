# Autor: Brooklyn Muñoz

from dataclasses import dataclass


@dataclass
class UpdateUserRequest:
    id: int
    name: str
    email: str
