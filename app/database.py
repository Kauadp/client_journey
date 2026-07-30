import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.types import DateTime, Float, String
import os
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseManager")


class DatabaseManager:

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
            )
            logger.info("Engine do Banco de Dados inicializado com sucesso.")
        except Exception as e:
            logger.error(f"Erro ao criar o Engine do Banco de Dados: {str(e)}")
            raise e

    def id_public_existe(self, id_public: str) -> bool:
        query = text("SELECT 1 FROM users WHERE id_public = :id_public")
        with self.engine.connect() as conn:
            resultado = conn.execute(query, {"id_public": id_public}).fetchone()
        return resultado is not None

    def buscar_por_telefone(self, numero_cel: str) -> dict | None:
        query = text("SELECT * FROM users WHERE numero_cel = :numero_cel")
        with self.engine.connect() as conn:
            resultado = conn.execute(query, {"numero_cel": numero_cel}).mappings().fetchone()
        return dict(resultado) if resultado else None

    def inserir_usuario(self, nome: str, numero_cel: str, email: str, id_public: str) -> dict | None:
        query = text("""
            INSERT INTO users (nome, numero_cel, email, id_public)
            VALUES (:nome, :numero_cel, :email, :id_public)
            RETURNING *
        """)
        try:
            with self.engine.begin() as conn:
                resultado = conn.execute(
                    query,
                    {"nome": nome, "numero_cel": numero_cel, "email": email, "id_public": id_public},
                ).mappings().fetchone()
            logger.info(f"Usuário {id_public} inserido com sucesso.")
            return dict(resultado)
        except SQLAlchemyError as e:
            logger.error(f"Erro ao inserir usuário: {e}")
            return None


load_dotenv()
db = DatabaseManager(connection_string=os.getenv("db_uri"))
