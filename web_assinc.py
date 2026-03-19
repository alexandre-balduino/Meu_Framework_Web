
import asyncio
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
        extensoes = {'.css': 'text/css', '.js': 'application/javascript', '.png': 'image/png', '.jpg': 'image/jpeg'}
        _, ext = os.path.splitext(caminho_arquivo)
        return extensoes.get(ext.lower(), 'text/plain')

    def render_template(self, nome_arquivo, **contexto):
        return self.jinja_env.get_template(nome_arquivo).render(**contexto)

    def rota(self, caminho, metodos=['GET']):
        def decorador(funcao):
            padrao = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', caminho)
            self.rotas.append({'metodo': metodos[0].upper(), 'regex': re.compile(f"^{padrao}$"), 'funcao': funcao})
            return funcao
        return decorador

    def _log(self, metodo, caminho, status):
        horario = datetime.now().strftime('%H:%M:%S')
        cor = "\033[94m" if "200" in status else "\033[93m"
        print(f"[{horario}] {metodo} {caminho} - {cor}{status}\033[0m")

    async def gerenciar_conexao(self, leitor, escritor):
        try:
            dados = await leitor.read(4096)
            requisicao = dados.decode(errors='ignore')
            if not requisicao: return
            metodo, caminho, _ = requisicao.split('\r\n')[0].split(' ')

            # Suporte a arquivos estáticos
            if caminho.startswith('/static/'):
                caminho_local = os.path.join(os.getcwd(), caminho.lstrip('/'))
                if os.path.exists(caminho_local) and os.path.isfile(caminho_local):
                    with open(caminho_local, 'rb') as f:
                        conteudo = f.read()
                    tipo = self._obter_tipo_conteudo(caminho_local)
                    status = "200 OK"
                    self._log(metodo, caminho, status)
                    header = (f"HTTP/1.1 {status}\r\nContent-Type: {tipo}\r\n"
                              f"Content-Length: {len(conteudo)}\r\n\r\n").encode()
                    escritor.write(header + conteudo)
                    await escritor.drain()
                    return

            # Lógica de rotas (simplificada para o exemplo)
            funcao_rota = None
            params = {}
            for r in self.rotas:
                match = r['regex'].match(caminho)
                if match: funcao_rota = r['funcao']; params = match.groupdict(); break

            if funcao_rota:
                corpo = await funcao_rota(**params) if params else await funcao_rota()
                status = "200 OK"
            else:
                corpo = "<h1>404</h1>"; status = "404 NOT FOUND"

            self._log(metodo, caminho, status)
            res = (f"HTTP/1.1 {status}\r\nContent-Type: text/html\r\n"
                   f"Content-Length: {len(corpo.encode())}\r\n\r\n{corpo}").encode()
            escritor.write(res)
            await escritor.drain()
        finally:
            escritor.close()
            await escritor.wait_closed()

    def servir(self, host='127.0.0.1', porta=9000):
        async def main():
            server = await asyncio.start_server(self.gerenciar_conexao, host, porta)
            print(f"🚀 Servidor Assíncrono em http://{host}:{porta}")
            async with server: await server.serve_forever()
        try: asyncio.run(main())
        except KeyboardInterrupt: print("\n🛑 Desligado.")
