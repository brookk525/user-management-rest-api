# Autor: Brooklyn Muñoz

from dataclasses import dataclass


@dataclass
class TokenResponse:
    access_token: str
    token_type: str
