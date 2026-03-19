
import socket
import re
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class MeuFramework:
    def __init__(self, pasta_templates='templates', pasta_static='static'):
        self.rotas = []
        self.pasta_static = pasta_static
        self.jinja_env = Environment(loader=FileSystemLoader(pasta_templates))

    def _obter_tipo_conteudo(self, caminho_arquivo):
        """Retorna o MIME Type baseado na extensão"""
        extensoes = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml'
        }
        _, ext = os.path.splitext(caminho_arquivo)
        return extensoes.get(ext.lower(), 'text/plain')

    def render_template(self, nome_arquivo, **contexto):
        template = self.jinja_env.get_template(nome_arquivo)
        return template.render(**contexto)

    def rota(self, caminho, metodos=['GET']):
        def decorador(funcao):
            padrao_regex = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', caminho)
            regex_compilada = re.compile(f"^{padrao_regex}$")
            for metodo in metodos:
                self.rotas.append({'metodo': metodo.upper(), 'regex': regex_compilada, 'funcao': funcao})
            return funcao
        return decorador

    def _log(self, metodo, caminho, status):
        horario = datetime.now().strftime('%H:%M:%S')
        cor = "\033[92m" if "200" in status else "\033[91m"
        print(f"[{horario}] {metodo} {caminho} - {cor}{status}\033[0m")

    def _processar_requisicoes(self, servidor):
        while True:
            conexao, endereco = servidor.accept()
            try:
                requisicao = conexao.recv(4096).decode(errors='ignore')
                if not requisicao: continue

                linhas = requisicao.split('\r\n')
                metodo, caminho, _ = linhas[0].split(' ')

                # Lógica de Arquivos Estáticos
                if caminho.startswith('/static/'):
                    caminho_local = os.path.join(os.getcwd(), caminho.lstrip('/'))
                    if os.path.exists(caminho_local) and os.path.isfile(caminho_local):
                        with open(caminho_local, 'rb') as f:
                            conteudo = f.read()
                        tipo = self._obter_tipo_conteudo(caminho_local)
                        status = "200 OK"
                        self._log(metodo, caminho, status)
                        resposta = (f"HTTP/1.1 {status}\r\nContent-Type: {tipo}\r\n"
                                    f"Content-Length: {len(conteudo)}\r\n\r\n").encode() + conteudo
                        conexao.sendall(resposta)
                        continue

                # Lógica de Rotas Normais (igual antes)
                funcao_rota = None
                params_url = {}
                for r in self.rotas:
                    match = r['regex'].match(caminho)
                    if match and r['metodo'] == metodo:
                        funcao_rota = r['funcao']
                        params_url = match.groupdict()
                        break

                if funcao_rota:
                    # (Parsing de corpo omitido aqui para brevidade, mas deve ser mantido)
                    corpo_res = funcao_rota(**params_url) if params_url else funcao_rota()
                    status = "200 OK"
                    tipo = "text/html; charset=utf-8"
                else:
                    corpo_res = "<h1>404 Not Found</h1>"; status = "404 NOT FOUND"; tipo = "text/html"

                self._log(metodo, caminho, status)
                res_final = (f"HTTP/1.1 {status}\r\nContent-Type: {tipo}\r\n"
                             f"Content-Length: {len(corpo_res.encode())}\r\n\r\n{corpo_res}").encode()
                conexao.sendall(res_final)
            finally:
                conexao.close()

    def servir(self, host='127.0.0.1', porta=9000):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta)); servidor.listen(5)
        print(f"🚀 Servidor Síncrono em http://{host}:{porta}")
        self._processar_requisicoes(servidor)
