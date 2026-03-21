
import json
from urllib.parse import parse_qs

class Request:
    """
    Representa uma requisição HTTP enviada pelo cliente (navegador).
    Transforma dados brutos em atributos fáceis de usar.
    """
    def __init__(self, method, path, headers, raw_body=None):
        """
        Inicializa o objeto Request.
        :param method: Método HTTP (GET, POST, etc.)
        :param path: URL acessada (ex: /perfil?id=1)
        :param headers: Dicionário com os cabeçalhos da requisição
        :param raw_body: Conteúdo bruto enviado (corpo da requisição)
        """
        self.method = method.upper()
        self.headers = headers
        self.raw_body = raw_body
        
        # Atributos para armazenar dados processados
        self.path = path
        self.query_params = {}
        self.form = {}

        # 1. Processa Query Params (Ex: /search?q=python -> {'q': 'python'})
        if "?" in path:
            self.path, query_string = path.split("?", 1)
            # parse_qs retorna uma lista para cada chave; pegamos apenas o primeiro valor [0]
            parsed_query = parse_qs(query_string)
            self.query_params = {k: v[0] for k, v in parsed_query.items()}

        # 2. Processa o Corpo da Requisição (Formulários ou JSON)
        if self.raw_body:
            content_type = self.headers.get("Content-Type", "")
            
            # Se for um formulário padrão de HTML (POST)
            if "application/x-www-form-urlencoded" in content_type:
                parsed_form = parse_qs(self.raw_body)
                self.form = {k: v[0] for k, v in parsed_form.items()}
            
            # Se for um envio de dados via JSON (APIs ou JavaScript)
            elif "application/json" in content_type:
                try:
                    self.form = json.loads(self.raw_body)
                except json.JSONDecodeError:
                    self.form = {}

    def get(self, key, default=None):
        """
        Busca um valor primeiro nos parâmetros da URL, depois no formulário.
        :param key: Nome da chave (ex: 'id' ou 'nome')
        :param default: Valor retornado caso a chave não exista
        """
        return self.query_params.get(key) or self.form.get(key) or default

    def __repr__(self):
        """Representação visual do objeto no log ou terminal."""
        return f"<Request {self.method} {self.path}>"
