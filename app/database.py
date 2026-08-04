import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
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

    def buscar_por_email(self, email: str) -> dict | None:
        query = text("SELECT * FROM users WHERE email = :email")
        with self.engine.connect() as conn:
            resultado = conn.execute(query, {"email": email}).mappings().fetchone()
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

    def buscar_por_id_public(self, id_public: str) -> dict | None:
        query = text("SELECT * FROM users WHERE id_public = :id_public")
        with self.engine.connect() as conn:
            resultado = conn.execute(query, {"id_public": id_public}).mappings().fetchone()
        return dict(resultado) if resultado else None


    def buscar_loja_por_codigo(self, codigo_publico: str) -> dict | None:
        query = text("SELECT * FROM lojas WHERE codigo_publico = :codigo_publico")
        with self.engine.connect() as conn:
            resultado = conn.execute(query, {"codigo_publico": codigo_publico}).mappings().fetchone()
        return dict(resultado) if resultado else None

    
    def codigo_loja_existe(self, codigo: str) -> bool:
        query = text("SELECT 1 FROM lojas WHERE codigo_publico = :codigo")
        with self.engine.connect() as conn:
            resultado = conn.execute(query, {"codigo": codigo}).fetchone()
        return resultado is not None

    def inserir_loja(self, codigo_publico: str, nome: str, pontos_base: int) -> dict | None:
        query = text("""
            INSERT INTO lojas (codigo_publico, nome, pontos_base)
            VALUES (:codigo_publico, :nome, :pontos_base)
            RETURNING *
        """)
        try:
            with self.engine.begin() as conn:
                resultado = conn.execute(
                    query,
                    {"codigo_publico": codigo_publico, "nome": nome, "pontos_base": pontos_base},
                ).mappings().fetchone()
            logger.info(f"Loja {nome} inserida com sucesso.")
            return dict(resultado)
        except SQLAlchemyError as e:
            logger.error(f"Erro ao inserir loja: {e}")
            return None

    def registrar_pontuacao(self, visitante_id: int, loja_id: int, pontos: int) -> str:
        """Retorna 'ok', 'duplicado' ou 'erro' — pra rota decidir qual tela mostrar."""
        query = text("""
            INSERT INTO pontuacoes (visitante_id, loja_id, pontos)
            VALUES (:visitante_id, :loja_id, :pontos)
        """)
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {"visitante_id": visitante_id, "loja_id": loja_id, "pontos": pontos})
            logger.info(f"Pontuação registrada: visitante {visitante_id} na loja {loja_id}.")
            return "ok"
        except IntegrityError:
            logger.warning(f"Tentativa de pontuação duplicada: visitante {visitante_id} na loja {loja_id}.")
            return "duplicado"
        except SQLAlchemyError as e:
            logger.error(f"Erro ao registrar pontuação: {e}")
            return "erro"

    def registrar_hub_juquita(self, visitante_id: int, composicao: str, faixa_etaria: str, local_origem: str) -> str:
        """Retorna 'ok', 'duplicado' ou 'erro'."""
        query = text("""
            INSERT INTO interacoes_hub_juquita (visitante_id, composicao, faixa_etaria, local_origem)
            VALUES (:visitante_id, :composicao, :faixa_etaria, :local_origem)
        """)
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "visitante_id": visitante_id,
                    "composicao": composicao,
                    "faixa_etaria": faixa_etaria,
                    "local_origem": local_origem
                })
            logger.info(f"Hub Juquita registrado para visitante {visitante_id}.")
            return "ok"
        except IntegrityError:
            logger.warning(f"Visitante {visitante_id} já respondeu o Hub Juquita.")
            return "duplicado"
        except SQLAlchemyError as e:
            logger.error(f"Erro ao registrar Hub Juquita: {e}")
            return "erro"

    def registrar_vip_lounge(self, visitante_id: int, perfil_consumo: str, intencao_compra: str) -> str:
            """Retorna 'ok', 'duplicado' ou 'erro'."""
            query = text("""
                INSERT INTO interacoes_lounge_vip (visitante_id, perfil_consumo, intencao_compra)
                VALUES (:visitante_id, :perfil_consumo, :intencao_compra)
            """)
            try:
                with self.engine.begin() as conn:
                    conn.execute(query, {
                        "visitante_id": visitante_id,
                        "perfil_consumo": perfil_consumo,
                        "intencao_compra": intencao_compra,
                    })
                logger.info(f"Vip Lounge registrado para visitante {visitante_id}.")
                return "ok"
            except IntegrityError:
                logger.warning(f"Visitante {visitante_id} já respondeu o Vip Lounge.")
                return "duplicado"
            except SQLAlchemyError as e:
                logger.error(f"Erro ao registrar Vip Lounge: {e}")
                return "erro"

    def buscar_resumo_pontuacao_usuario(self, id_public: str) -> dict:
        query = text("""
            SELECT 
                users.id,
                users.nome AS usuario_nome,
                lojas.nome AS loja_nome,
                SUM(pontuacoes.pontos) AS total_pontos_loja
            FROM users
            LEFT JOIN pontuacoes 
                ON users.id = pontuacoes.visitante_id
            LEFT JOIN lojas 
                ON pontuacoes.loja_id = lojas.id
            WHERE users.id_public = :id_public
            GROUP BY users.id, users.nome, lojas.id, lojas.nome
        """)
        
        with self.engine.connect() as conn:
            resultados = conn.execute(query, {"id_public": id_public}).mappings().fetchall()
        
        if not resultados:
            return None

        linhas = [dict(row) for row in resultados]
        
        total_geral = sum(row["total_pontos_loja"] or 0 for row in linhas)
        
        return {
            "usuario_id": linhas[0]["id"],
            "usuario_nome": linhas[0]["usuario_nome"],
            "total_geral_pontos": total_geral,
            "lojas": [
                {"loja": row["loja_nome"], "pontos": row["total_pontos_loja"]} 
                for row in linhas if row["loja_nome"] is not None
            ]
        }

    def inserir_brinde(self, nome: str, custo_pontos: int, estoque: int) -> dict | None:
        query = text("""
            INSERT INTO brindes (nome, custo_pontos, estoque)
            VALUES (:nome, :custo_pontos, :estoque)
            RETURNING *
        """)
        try:
            with self.engine.begin() as conn:
                resultado = conn.execute(query, {
                    "nome": nome,
                    "custo_pontos": custo_pontos,
                    "estoque": estoque,
                }).mappings().fetchone()
            return dict(resultado)
        except SQLAlchemyError as e:
            logger.error(f"Erro ao inserir brinde: {e}")
            return None

load_dotenv()
db = DatabaseManager(connection_string=os.getenv("db_uri"))
