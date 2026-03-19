
import asyncio
import re
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class MeuFramework:
    def __init__(self, pasta_templates='templates', pasta_static='static'):
        self.rotas = []
        self.pasta_static = pasta_static
        # Configuração do Jinja2
        self.jinja_env = Environment(loader=FileSystemLoader(pasta_templates))

    def render_template(self, nome_arquivo, **contexto):
        """Renderiza um arquivo HTML usando Jinja2"""
        template = self.jinja_env.get_template(nome_arquivo)
        return template.render(**contexto)

    def _obter_tipo_conteudo(self, caminho_arquivo):
        """Identifica o MIME Type para arquivos estáticos"""
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

    def rota(self, caminho, metodos=['GET']):
        """Decorador para registrar rotas com Regex e múltiplos métodos"""
        def decorador(funcao):
            padrao_regex = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', caminho)
            regex_compilada = re.compile(f"^{padrao_regex}$")
            for metodo in metodos:
                self.rotas.append({
                    'metodo': metodo.upper(),
                    'regex': regex_compilada,
                    'funcao': funcao
                })
            return funcao
        return decorador

    def _log(self, metodo, caminho, status):
        """Logger para o terminal"""
        horario = datetime.now().strftime('%H:%M:%S')
        cor = "\033[94m" if "200" in status else "\033[93m"
        print(f"[{horario}] {metodo} {caminho} - {cor}{status}\033[0m")

    async def gerenciar_conexao(self, leitor, escritor):
        metodo, caminho = "???", "???"
        try:
            dados = await leitor.read(4096)
            requisicao = dados.decode(errors='ignore')
            if not requisicao:
                escritor.close()
                return

            linhas = requisicao.split('\r\n')
            primeira_linha = linhas[0]
            metodo, caminho, _ = primeira_linha.split(' ')

            # 1. Tentar servir arquivo estático
            if caminho.startswith(f'/{self.pasta_static}/'):
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

            # 2. Processar corpo da requisição (POST, PUT, etc)
            dados_corpo = {}
            if metodo != 'GET':
                corpo = linhas[-1]
                if corpo and '=' in corpo:
                    for par in corpo.split('&'):
                        if '=' in par:
                            k, v = par.split('=')
                            dados_corpo[k] = v

            # 3. Buscar rota por Regex
            funcao_rota = None
            params_url = {}
            for r in self.rotas:
                match = r['regex'].match(caminho)
                if match and r['metodo'] == metodo:
                    funcao_rota = r['funcao']
                    params_url = match.groupdict()
                    break

            # 4. Executar e Responder
            if funcao_rota:
                try:
                    argumentos = {**params_url, **dados_corpo}
                    corpo_res = await funcao_rota(**argumentos) if argumentos else await funcao_rota()
                    status = "200 OK"
                except Exception as e:
                    print(f"❌ Erro na rota: {e}")
                    corpo_res = "<h1>500 Internal Server Error</h1>"
                    status = "500 ERROR"
            else:
                corpo_res = "<h1>404 Not Found</h1>"
                status = "404 NOT FOUND"

            self._log(metodo, caminho, status)
            corpo_bytes = corpo_res.encode('utf-8')
            resposta = (f"HTTP/1.1 {status}\r\n"
                        f"Content-Type: text/html; charset=utf-8\r\n"
                        f"Content-Length: {len(corpo_bytes)}\r\n"
                        "Connection: close\r\n\r\n").encode() + corpo_bytes
            escritor.write(resposta)
            await escritor.drain()
        except Exception as e:
            print(f"⚠️ Erro de rede: {e}")
        finally:
            escritor.close()
            await escritor.wait_closed()

    def servir(self, host='127.0.0.1', porta=9000):
        async def main():
            servidor = await asyncio.start_server(self.gerenciar_conexao, host, porta)
            print(f"🚀 Servidor Assíncrono em http://{host}:{porta}")
            async with servidor:
                await servidor.serve_forever()
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n🛑 Servidor desligado.")
