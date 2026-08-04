import logging
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import os
from dotenv import load_dotenv
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DatabaseManager")

class SaldoInsuficiente(Exception):
    pass

class SemEstoque(Exception):
    pass

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
        query_pontuacao = text("""
            INSERT INTO pontuacoes (visitante_id, loja_id, pontos)
            VALUES (:visitante_id, :loja_id, :pontos)
        """)
        query_saldo = text("""
            UPDATE users SET pontos_atuais = pontos_atuais + :pontos WHERE id = :visitante_id
        """)
        try:
            with self.engine.begin() as conn:
                conn.execute(query_pontuacao, {"visitante_id": visitante_id, "loja_id": loja_id, "pontos": pontos})
                conn.execute(query_saldo, {"visitante_id": visitante_id, "pontos": pontos})
            logger.info(f"Pontuação registrada: visitante {visitante_id} na loja {loja_id}.")
            return "ok"
        except IntegrityError:
            logger.warning(f"Tentativa de pontuação duplicada: visitante {visitante_id} na loja {loja_id}.")
            return "duplicado"
        except SQLAlchemyError as e:
            logger.error(f"Erro ao registrar pontuação: {e}")
            return "erro"

    def registrar_entrada_juquita(self, visitante_id: int, item_ritmo: str, faixa_etaria: str, ficou_sabendo_onde: str) -> str:
        """Retorna 'ok', 'duplicado' ou 'erro'."""
        query = text("""
            INSERT INTO interacoes_entrada_juquita (visitante_id, item_ritmo, faixa_etaria, ficou_sabendo_onde)
            VALUES (:visitante_id, :item_ritmo, :faixa_etaria, :ficou_sabendo_onde)
        """)
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "visitante_id": visitante_id,
                    "item_ritmo": item_ritmo,
                    "faixa_etaria": faixa_etaria,
                    "ficou_sabendo_onde": ficou_sabendo_onde
                })
            logger.info(f"Entrada Juquita registrado para visitante {visitante_id}.")
            return "ok"
        except IntegrityError:
            logger.warning(f"Visitante {visitante_id} já respondeu à Entrada Juquita.")
            return "duplicado"
        except SQLAlchemyError as e:
            logger.error(f"Erro ao registrar Entrada Juquita: {e}")
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

    def registrar_acao_guerrilha(self, visitante_id: int, oque_trouxe: str, regiao: str) -> str:
        """Retorna 'ok', 'duplicado' ou 'erro'."""
        query = text("""
            INSERT INTO interacoes_acao_guerrilha (visitante_id, oque_trouxe, regiao)
            VALUES (:visitante_id, :oque_trouxe, :regiao)
        """)
        try:
            with self.engine.begin() as conn:
                conn.execute(query, {
                    "visitante_id": visitante_id,
                    "oque_trouxe": oque_trouxe,
                    "regiao": regiao
                })
            logger.info(f"Ação Guerrilha registrada para visitante {visitante_id}.")
            return "ok"
        except IntegrityError:
            logger.warning(f"Visitante {visitante_id} já respondeu a Ação Guerrilha.")
            return "duplicado"
        except SQLAlchemyError as e:
            logger.error(f"Erro ao registrar Ação Guerrilha: {e}")
            return "erro"

    def registrar_boas_vindas(self, visitante_id: int, quem_eh_voce: str, qual_foco: str, regiao: str) -> str:
            """Retorna 'ok', 'duplicado' ou 'erro'."""
            query = text("""
                INSERT INTO interacoes_boas_vindas (visitante_id, quem_eh_voce, qual_foco, regiao)
                VALUES (:visitante_id, :quem_eh_voce, :qual_foco, :regiao)
            """)
            try:
                with self.engine.begin() as conn:
                    conn.execute(query, {
                        "visitante_id": visitante_id,
                        "quem_eh_voce": quem_eh_voce,
                        "qual_foco": qual_foco,
                        "regiao": regiao
                    })
                logger.info(f"Boas Vindas registrada para visitante {visitante_id}.")
                return "ok"
            except IntegrityError:
                logger.warning(f"Visitante {visitante_id} já respondeu às Boas Vindas.")
                return "duplicado"
            except SQLAlchemyError as e:
                logger.error(f"Erro ao registrar Boas Vindas: {e}")
                return "erro"

    def registrar_estacionamento(self, visitante_id: int, como_veio: str, quanto_tempo: str) -> str:
                """Retorna 'ok', 'duplicado' ou 'erro'."""
                query = text("""
                    INSERT INTO interacoes_estacionamento (visitante_id, como_veio, quanto_tempo)
                    VALUES (:visitante_id, :como_veio, :quanto_tempo)
                """)
                try:
                    with self.engine.begin() as conn:
                        conn.execute(query, {
                            "visitante_id": visitante_id,
                            "como_veio": como_veio,
                            "quanto_tempo": quanto_tempo
                        })
                    logger.info(f"Estacionamento registrada para visitante {visitante_id}.")
                    return "ok"
                except IntegrityError:
                    logger.warning(f"Visitante {visitante_id} já respondeu ao Estacionamento.")
                    return "duplicado"
                except SQLAlchemyError as e:
                    logger.error(f"Erro ao registrar Estacionamento: {e}")
                    return "erro"

    def registrar_cenografia(self, visitante_id: int, oque_mais_garimpou: str, qual_marca_deixou_louco: str) -> str:
                    """Retorna 'ok', 'duplicado' ou 'erro'."""
                    query = text("""
                        INSERT INTO interacoes_cenografia (visitante_id, oque_mais_garimpou, qual_marca_deixou_louco)
                        VALUES (:visitante_id, :oque_mais_garimpou, :qual_marca_deixou_louco)
                    """)
                    try:
                        with self.engine.begin() as conn:
                            conn.execute(query, {
                                "visitante_id": visitante_id,
                                "oque_mais_garimpou": oque_mais_garimpou,
                                "qual_marca_deixou_louco": qual_marca_deixou_louco
                            })
                        logger.info(f"Cenografia registrada para visitante {visitante_id}.")
                        return "ok"
                    except IntegrityError:
                        logger.warning(f"Visitante {visitante_id} já respondeu ao Cenografia.")
                        return "duplicado"
                    except SQLAlchemyError as e:
                        logger.error(f"Erro ao registrar Cenografia: {e}")
                        return "erro"

    def buscar_resumo_pontuacao_usuario(self, id_public: str) -> dict | None:
        query_usuario = text("""
            SELECT
                id,
                nome,
                pontos_atuais
            FROM users
            WHERE id_public = :id_public
        """)

        query_lojas = text("""
            SELECT
                l.nome AS loja_nome,
                SUM(p.pontos) AS pontos
            FROM pontuacoes p
            JOIN lojas l
                ON l.id = p.loja_id
            JOIN users u
                ON u.id = p.visitante_id
            WHERE u.id_public = :id_public
            GROUP BY l.id, l.nome
            ORDER BY l.nome
        """)

        query_resgates = text("""
            SELECT
                b.nome AS brinde_nome,
                r.pontos_debitados
            FROM resgates r
            JOIN brindes b
                ON b.id = r.brinde_id
            JOIN users u
                ON u.id = r.visitante_id
            WHERE u.id_public = :id_public
            ORDER BY r.id DESC
        """)

        with self.engine.connect() as conn:
            usuario = conn.execute(
                query_usuario,
                {"id_public": id_public}
            ).mappings().fetchone()

            if usuario is None:
                return None

            lojas = conn.execute(
                query_lojas,
                {"id_public": id_public}
            ).mappings().fetchall()

            resgates = conn.execute(
                query_resgates,
                {"id_public": id_public}
            ).mappings().fetchall()

        return {
            "usuario_id": usuario["id"],
            "usuario_nome": usuario["nome"],
            "pontos_atuais": usuario["pontos_atuais"],
            "lojas": [
                {
                    "loja": loja["loja_nome"],
                    "pontos": loja["pontos"],
                }
                for loja in lojas
            ],
            "resgates": [
                {
                    "brinde": resgate["brinde_nome"],
                    "pontos": resgate["pontos_debitados"],
                }
                for resgate in resgates
            ],
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

    def buscar_brindes_disponiveis(self) -> list[dict]:
        query = text("SELECT * FROM brindes WHERE estoque > 0 ORDER BY custo_pontos")
        with self.engine.connect() as conn:
            resultados = conn.execute(query).mappings().fetchall()
        return [dict(row) for row in resultados]

    def buscar_brinde(self, brinde_id: int) -> dict | None:
        query = text("SELECT * FROM brindes WHERE id = :id")
        with self.engine.connect() as conn:
            resultado = conn.execute(query, {"id": brinde_id}).mappings().fetchone()
        return dict(resultado) if resultado else None

    def resgatar_brinde(self, visitante_id: int, brinde_id: int, custo_pontos: int) -> str:
        """Retorna 'ok', 'saldo_insuficiente', 'sem_estoque' ou 'erro'."""
        query_debita_saldo = text("""
            UPDATE users SET pontos_atuais = pontos_atuais - :custo
            WHERE id = :visitante_id AND pontos_atuais >= :custo
            RETURNING id
        """)
        query_debita_estoque = text("""
            UPDATE brindes SET estoque = estoque - 1
            WHERE id = :brinde_id AND estoque > 0
            RETURNING id
        """)
        query_log = text("""
            INSERT INTO resgates (visitante_id, brinde_id, pontos_debitados)
            VALUES (:visitante_id, :brinde_id, :custo)
        """)
        try:
            with self.engine.begin() as conn:
                if conn.execute(query_debita_saldo, {"visitante_id": visitante_id, "custo": custo_pontos}).fetchone() is None:
                    raise SaldoInsuficiente()
                if conn.execute(query_debita_estoque, {"brinde_id": brinde_id}).fetchone() is None:
                    raise SemEstoque()
                conn.execute(query_log, {"visitante_id": visitante_id, "brinde_id": brinde_id, "custo": custo_pontos})
            return "ok"
        except SaldoInsuficiente:
            return "saldo_insuficiente"
        except SemEstoque:
            return "sem_estoque"
        except SQLAlchemyError as e:
            logger.error(f"Erro ao resgatar brinde: {e}")
            return "erro"

load_dotenv()
db = DatabaseManager(connection_string=os.getenv("db_uri"))
