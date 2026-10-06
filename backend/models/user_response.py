# Autor: Brooklyn Muñoz

from dataclasses import dataclass


@dataclass
class UserResponse:
    id: int
    name: str
    email: str
    created_at: str | None = None
    avatar_url: str | None = None
