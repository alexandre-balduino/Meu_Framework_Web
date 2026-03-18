
import asyncio
import re
from datetime import datetime

class MeuFramework:
    def __init__(self):
        self.rotas = []

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
        cor = "\033[94m" if "200" in status else "\033[93m"
        print(f"[{horario}] {metodo} {caminho} - {cor}{status}\033[0m")

    async def gerenciar_conexao(self, leitor, escritor):
        try:
            dados = await leitor.read(4096)
            requisicao = dados.decode()
            if not requisicao: return

            linhas = requisicao.split('\r\n')
            metodo, caminho, _ = linhas[0].split(' ')

            dados_corpo = {}
            if metodo != 'GET':
                corpo = linhas[-1]
                if corpo and '=' in corpo:
                    for par in corpo.split('&'):
                        if '=' in par:
                            k, v = par.split('=')
                            dados_corpo[k] = v

            funcao_rota = None
            params_url = {}
            for r in self.rotas:
                match = r['regex'].match(caminho)
                if match and r['metodo'] == metodo:
                    funcao_rota = r['funcao']
                    params_url = match.groupdict()
                    break

            if funcao_rota:
                try:
                    argumentos = {**params_url, **dados_corpo} if dados_corpo else params_url
                    corpo_res = await funcao_rota(**argumentos) if argumentos else await funcao_rota()
                    status = "200 OK"
                except Exception as e:
                    print(f"❌ Erro Async: {e}")
                    corpo_res = "<h1>500 Error</h1>"; status = "500 ERROR"
            else:
                corpo_res = "<h1>404 Not Found</h1>"; status = "404 NOT FOUND"

            self._log(metodo, caminho, status)
            corpo_bytes = corpo_res.encode()
            resposta = (f"HTTP/1.1 {status}\r\nContent-Length: {len(corpo_bytes)}\r\n"
                        f"Content-Type: text/html\r\n\r\n").encode() + corpo_bytes
            escritor.write(resposta)
            await escritor.drain()
        finally:
            escritor.close()
            await escritor.wait_closed()

    def servir(self, host='127.0.0.1', porta=9000):
        async def main():
            servidor = await asyncio.start_server(self.gerenciar_conexao, host, porta)
            print(f"🚀 Servidor Assíncrono em http://{host}:{porta}")
            async with servidor: await servidor.serve_forever()
        try: asyncio.run(main())
        except KeyboardInterrupt: print("\n🛑 Desligado.")
