# Autor: Brooklyn Muñoz

import sqlite3
from pathlib import Path

from adapters.interfaces.user_adapter import UserAdapter
from models.create_user_request import CreateUserRequest
from models.update_user_request import UpdateUserRequest
from models.user import User


class UserNoOrmAdapter(UserAdapter):
    def __init__(self):
        # esta es la ruta del archivo SQLite del proyecto.
        self.database_path: Path = Path(__file__).parents[2] / "database" / "database.db"

    def create_table(self):
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    avatar_url TEXT
                )
                """
            )
            connection.commit()

    def create_user(self, user: CreateUserRequest) -> int:
        self.create_table()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (name, email)
                VALUES (?, ?)
                """,
                (user.name, user.email),
            )
            connection.commit()
            return cursor.lastrowid

    def get_user(self, user_id: int) -> User | None:
        self.create_table()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, name, email, created_at, avatar_url FROM users WHERE id = ?",
                (user_id,),
            )
            row = cursor.fetchone()

        if row is None:
            return None

        return User(row[0], row[1], row[2], row[3], row[4])

    def update_user(self, user: UpdateUserRequest):
        self.create_table()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (user.name, user.email, user.id),
            )
            connection.commit()
            updated_rows: int = cursor.rowcount

        if updated_rows == 0:
            raise ValueError("Usuario no encontrado con la id proporcionada")

    def update_avatar_by_email(self, email: str, avatar_url: str):
        self.create_table()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE users SET avatar_url = ? WHERE email = ?",
                (avatar_url, email),
            )
            connection.commit()
            updated_rows: int = cursor.rowcount

        if updated_rows == 0:
            raise ValueError("Usuario no encontrado con el email proporcionado")

    def delete_user(self, user_id: int):
        self.create_table()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,),
            )
            connection.commit()
            deleted_rows: int = cursor.rowcount

        if deleted_rows == 0:
            raise ValueError("Usuario no encontrado con la id proporcionada")

    def list_users(self) -> list[int]:
        self.create_table()
        with sqlite3.connect(self.database_path) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id FROM users")
            rows = cursor.fetchall()

        user_ids: list[int] = []
        for row in rows:
            user_ids.append(row[0])
        return user_ids
