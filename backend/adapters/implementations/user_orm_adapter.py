# Autor: Brooklyn Muñoz

from datetime import datetime
from pathlib import Path

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from adapters.interfaces.user_adapter import UserAdapter
from models.create_user_request import CreateUserRequest
from models.update_user_request import UpdateUserRequest
from models.user import User


# aqui Base es lo que usa SQLAlchemy para crear tablas usando clases.
Base = declarative_base()


# aqui esta clase representa la tabla users_orm de la base de datos.
class UserOrmTable(Base):
    __tablename__ = "users_orm"

    id = Column(Integer, primary_key = True, autoincrement = True)
    name = Column(String, nullable = False)
    email = Column(String, nullable = False)
    created_at = Column(String)
    avatar_url = Column(String)


class UserOrmAdapter(UserAdapter):
    def __init__(self):
        # esta es la misma base de datos SQLite, pero usando SQLAlchemy.
        database_path: Path = Path(__file__).parents[2] / "database" / "database.db"
        # SQLAlchemy necesita la ruta en formato sqlite:///.
        database_url: str = "sqlite:///" + str(database_path).replace("\\", "/")
        self.engine = create_engine(database_url)
        # con esto puedo crear sesiones para hacer consultas con ORM.
        self.session_maker = sessionmaker(bind = self.engine)
        # si la tabla ORM no existe, SQLAlchemy la crea.
        Base.metadata.create_all(self.engine)

    def create_user(self, user: CreateUserRequest) -> int:
        session = self.session_maker()
        # guardo la fecha como texto para que sea facil de mostrar despues.
        created_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        user_table: UserOrmTable = UserOrmTable(name = user.name, email = user.email, created_at = created_at)

        session.add(user_table)
        session.commit()

        user_id: int = user_table.id
        session.close()
        return user_id

    def get_user(self, user_id: int) -> User | None:
        session = self.session_maker()
        user_table: UserOrmTable | None = session.get(UserOrmTable, user_id)

        if user_table is None:
            session.close()
            return None

        user: User = User(user_table.id, user_table.name, user_table.email, user_table.created_at, user_table.avatar_url)
        session.close()
        return user

    def update_user(self, user: UpdateUserRequest):
        session = self.session_maker()
        user_table: UserOrmTable | None = session.get(UserOrmTable, user.id)

        if user_table is None:
            session.close()
            raise ValueError("Usuario no encontrado con la id proporcionada")

        user_table.name = user.name
        user_table.email = user.email
        session.commit()
        session.close()

    def update_avatar_by_email(self, email: str, avatar_url: str):
        session = self.session_maker()
        user_table: UserOrmTable | None = session.query(UserOrmTable).filter_by(email = email).first()

        if user_table is None:
            session.close()
            raise ValueError("Usuario no encontrado con el email proporcionado")

        user_table.avatar_url = avatar_url
        session.commit()
        session.close()

    def delete_user(self, user_id: int):
        session = self.session_maker()
        user_table: UserOrmTable | None = session.get(UserOrmTable, user_id)

        if user_table is None:
            session.close()
            raise ValueError("Usuario no encontrado con la id proporcionada")

        session.delete(user_table)
        session.commit()
        session.close()

    def list_users(self) -> list[int]:
        session = self.session_maker()
        rows: list[UserOrmTable] = session.query(UserOrmTable).all()
        user_ids: list[int] = []

        for row in rows:
            user_ids.append(row.id)

        session.close()
        return user_ids
