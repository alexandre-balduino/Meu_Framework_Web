
import os
import inspect
from jinja2 import Environment, FileSystemLoader
from .requests import Request
from .logger import Logger

class MyFramework:
    """
    Classe principal do framework que gerencia roteamento e templates.
    Identifica automaticamente os caminhos base do projeto do usuário.
    """
    def __init__(self, static_folder='static', template_folder='templates'):
        """
        Inicializa o MyFramework com detecção automática de caminho.
        """
        # INICIALIZAÇÃO CRITICAL: O dicionário de rotas deve existir antes de qualquer decorator!
        self.routes = {}
        
        # Detecta o diretório do arquivo que instanciou a classe (o app.py do usuário)
        stack = inspect.stack()
        caller_frame = stack[1]
        caller_path = os.path.abspath(caller_frame.filename)
        self.base_dir = os.path.dirname(caller_path)

        # Configura os caminhos absolutos
        self.static_folder = static_folder
        self.template_folder = template_folder
        self.static_abs_path = os.path.join(self.base_dir, self.static_folder)
        self.template_abs_path = os.path.join(self.base_dir, self.template_folder)
        
        # Inicializa o motor Jinja2 apontando para o caminho absoluto detectado
        if os.path.exists(self.template_abs_path):
            self.env = Environment(loader=FileSystemLoader(self.template_abs_path))
        else:
            self.env = None
            Logger.error(f"Pasta de templates não encontrada em: {self.template_abs_path}")

    def route(self, path, methods=['GET']):
        """
        Decorator para registrar funções como manipuladores de rotas.
        """
        def wrapper(handler):
            # Agora self.routes existe e não dará mais AttributeError
            self.routes[path] = {
                'handler': handler, 
                'methods': [m.upper() for m in methods]
            }
            return handler
        return wrapper

    def render_template(self, template_name, **context):
        """
        Renderiza um arquivo HTML usando Jinja2.
        """
        if not self.env:
            return "<h1>Template Error</h1><p>Pasta 'templates' não detectada no seu projeto.</p>"
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            Logger.error(f"Erro ao renderizar {template_name}: {e}")
            return f"<h1>Template Error</h1><p>{e}</p>"

    async def dispatch(self, method, path, headers, body=None):
        """
        Despacha a requisição para a função de rota correta.
        """
        request = Request(method, path, headers, body)
        
        if request.path not in self.routes:
            return "<h1>404 Not Found</h1>", "404 NOT FOUND"

        route_data = self.routes[request.path]

        if request.method not in route_data['methods']:
            return "<h1>405 Method Not Allowed</h1>", "405 METHOD NOT ALLOWED"

        try:
            handler = route_data['handler']
            response_content = await handler(request)
            return response_content, "200 OK"
            
        except Exception as e:
            Logger.error(f"Erro na rota {path}: {e}")
            raise e
