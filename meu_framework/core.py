
import re
import os
import sys
import inspect
from datetime import datetime
from .templating import TemplateEngine

class MeuFramework:
    def __init__(self, templates='templates', static='static'):
        self.rotas = []
        
        # --- LÓGICA DE CAMINHOS BLINDADOS (ANDROID/TERMUX) ---
        # sys.argv[0] pega o caminho real do app.py que você executou
        caminho_execucao = os.path.abspath(sys.argv[0])
        self.diretorio_base = os.path.dirname(caminho_execucao)
        
        # Montagem dos caminhos absolutos para evitar Erro 500
        self.caminho_templates_abs = os.path.join(self.diretorio_base, templates)
        self.caminho_static_abs = os.path.join(self.diretorio_base, static)
        self.pasta_static = static

        # Inicializa o motor de templates (Jinja2)
        self.tpl_engine = TemplateEngine(self.caminho_templates_abs)
        
        print(f"📂 Framework ativo em: {self.diretorio_base}")

    def rota(self, caminho, metodos=['GET']):
        """Decorador para registrar rotas com Regex e múltiplos métodos"""
        def decorador(funcao):
            # Transforma <parametro> em Regex nomeado (?P<parametro>[^/]+)
            padrao = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', caminho)
            regex = re.compile(f"^{padrao}$")
            for m in metodos:
                self.rotas.append({
                    'metodo': m.upper(), 
                    'regex': regex, 
                    'funcao': funcao
                })
            return funcao
        return decorador

    def render_template(self, name, **ctx):
        """Atalho para renderizar HTML via Jinja2"""
        return self.tpl_engine.render(name, **ctx)

    async def processar_rota(self, metodo, caminho, dados_corpo):
        """O Cérebro: decide qual função chamar e injeta os parâmetros certos"""
        funcao_rota = None
        params_url = {}

        # 1. Busca a rota correta
        for r in self.rotas:
            match = r['regex'].match(caminho)
            if match and r['metodo'] == metodo:
                funcao_rota = r['funcao']
                params_url = match.groupdict()
                break

        if funcao_rota:
            try:
                # 2. INJEÇÃO DE DEPENDÊNCIA (Professional Feature)
                # Mistura dados da URL com dados do formulário (POST)
                todos_dados = {**params_url, **dados_corpo}
                
                # Descobre o que a função realmente pede como argumento
                sig = inspect.signature(funcao_rota)
                args_filtrados = {
                    k: v for k, v in todos_dados.items() if k in sig.parameters
                }

                # 3. Executa a função (assíncrona ou não)
                if inspect.iscoroutinefunction(funcao_rota):
                    corpo = await funcao_rota(**args_filtrados)
                else:
                    corpo = funcao_rota(**args_filtrados)
                
                return corpo, "200 OK"
            except Exception as e:
                return f"<h1>500 Erro Interno</h1><p>{e}</p>", "500 ERROR"
        
        return "<h1>404 Not Found</h1>", "404 NOT FOUND"

    # --- MÉTODO PARA O SERVIDOR NATIVO (SOCKETS) ---
    def servir(self, host='127.0.0.1', porta=9000):
        """Inicia o servidor embutido (BuiltInServer)"""
        from .server import BuiltInServer
        server = BuiltInServer(self)
        server.run(host, porta)

    # --- MÉTODO PARA O UVICORN (ASGI INTERFACE) ---
    async def __call__(self, scope, receive, send):
        """Interface que permite rodar com: uvicorn app:app"""
        if scope['type'] != 'http':
            return

        caminho = scope['path']
        metodo = scope['method']

        # Parsing de corpo simplificado para ASGI
        dados_corpo = {}
        if metodo == 'POST':
            message = await receive()
            body = message.get('body', b'').decode()
            if body:
                for par in body.split('&'):
                    if '=' in par:
                        k, v = par.split('=')
                        dados_corpo[k] = v

        # Processa a lógica
        corpo_res, status_str = await self.processar_rota(metodo, caminho, dados_corpo)
        status_code = int(status_str.split(' '))
