
import sqlite3
import os
import inspect
from .logger import Logger

class Database:
    """
    Gerencia a conexão física com o arquivo do banco de dados SQLite.
    Garante que o arquivo seja criado na mesma pasta do app.py do usuário.
    """
    def __init__(self, db_name="data.db"):
        """
        Inicializa a conexão detectando o caminho absoluto do projeto.
        """
        # Detecta onde o script principal (app.py) está rodando
        stack = inspect.stack()
        # O último frame da pilha geralmente é o ponto de entrada do usuário
        caller_frame = stack[-1]
        caller_path = os.path.abspath(caller_frame.filename)
        self.base_dir = os.path.dirname(caller_path)
        
        # Define o caminho completo para o arquivo .db
        self.db_path = os.path.join(self.base_dir, db_name)
        
        # Conecta ao SQLite (check_same_thread=False é vital para o servidor assíncrono)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        
        # Log informativo para depuração no terminal
        Logger.debug(f"Database iniciado em: {self.db_path}")

    def execute(self, sql, params=()):
        """
        Executa comandos SQL com proteção contra SQL Injection.
        """
        try:
            result = self.cursor.execute(sql, params)
            self.connection.commit()
            return result
        except Exception as e:
            Logger.error(f"Erro no Banco de Dados: {e} | Query: {sql}")
            return None

class Model:
    """
    Classe base ORM (Object-Relational Mapping).
    Suas tabelas no app.py devem herdar desta classe.
    """
    db = Database() # Instância compartilhada da conexão
    table_name = "" # Deve ser definido na subclasse
    fields = {}     # Ex: {"name": "TEXT", "age": "INTEGER"}

    @classmethod
    def create_table(cls):
        """
        Gera e executa o comando CREATE TABLE automaticamente com base em 'fields'.
        """
        if not cls.table_name:
            Logger.error(f"Erro: 'table_name' não definido no Model {cls.__name__}")
            return

        # Monta as colunas. O ID é sempre autoincremento.
        columns = ", ".join([f"{name} {dtype}" for name, dtype in cls.fields.items()])
        sql = f"CREATE TABLE IF NOT EXISTS {cls.table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})"
        cls.db.execute(sql)

    @classmethod
    def create(cls, **data):
        """
        Insere um novo registro no banco.
        Ex: User.create(name="Leo", email="leo@test.com")
        """
        keys = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = tuple(data.values())
        
        sql = f"INSERT INTO {cls.table_name} ({keys}) VALUES ({placeholders})"
        cls.db.execute(sql, values)

    @classmethod
    def all(cls):
        """
        Retorna todos os registros da tabela como uma lista de dicionários.
        """
        sql = f"SELECT * FROM {cls.table_name}"
        cls.db.cursor.execute(sql)
        return [dict(row) for row in cls.db.cursor.fetchall()]

    @classmethod
    def get(cls, **filters):
        """
        Busca um único registro baseado em filtros (Ex: id=1).
        """
        conditions = " AND ".join([f"{k} = ?" for k in filters.keys()])
        sql = f"SELECT * FROM {cls.table_name} WHERE {conditions} LIMIT 1"
        
        cls.db.cursor.execute(sql, tuple(filters.values()))
        row = cls.db.cursor.fetchone()
        return dict(row) if row else None

    @classmethod
    def filter(cls, **filters):
        """
        Busca múltiplos registros que atendam aos critérios.
        """
        conditions = " AND ".join([f"{k} = ?" for k in filters.keys()])
        sql = f"SELECT * FROM {cls.table_name} WHERE {conditions}"
        
        cls.db.cursor.execute(sql, tuple(filters.values()))
        return [dict(row) for row in cls.db.cursor.fetchall()]

    @classmethod
    def update(cls, record_id, **new_data):
        """
        Atualiza campos de um registro específico pelo ID.
        """
        if not new_data: return
        
        set_clause = ", ".join([f"{k} = ?" for k in new_data.keys()])
        values = tuple(new_data.values()) + (record_id,)
        
        sql = f"UPDATE {cls.table_name} SET {set_clause} WHERE id = ?"
        cls.db.execute(sql, values)

    @classmethod
    def delete(cls, record_id):
        """
        Remove um registro permanentemente pelo ID.
        """
        sql = f"DELETE FROM {cls.table_name} WHERE id = ?"
        cls.db.execute(sql, (record_id,))
