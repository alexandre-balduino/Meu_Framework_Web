
import asyncio
from datetime import datetime

class MeuFramework:
    def __init__(self):
        self.rotas = {}

    def rota(self, caminho, metodos=['GET']):
        def decorador(funcao):
            for metodo in metodos:
                self.rotas[(caminho, metodo.upper())] = funcao
            return funcao
        return decorador

    def _log(self, metodo, caminho, status):
        horario = datetime.now().strftime('%H:%M:%S')
        cor = "\033[94m" if "200" in status else "\033[93m" # Azul para OK, Amarelo para Erro no Async
        print(f"[{horario}] {metodo} {caminho} - {cor}{status}\033[0m")

    async def gerenciar_conexao(self, leitor, escritor):
        metodo, caminho = "???", "???" # Prevenção para erro no log se o parse falhar
        try:
            dados = await leitor.read(4096)
            requisicao = dados.decode()
            if not requisicao:
                escritor.close()
                return

            linhas = requisicao.split('\r\n')
            metodo, caminho, _ = linhas[0].split(' ')

            dados_corpo = {}
            if metodo != 'GET':
                corpo = linhas[-1]
                if corpo:
                    for par in corpo.split('&'):
                        if '=' in par:
                            chave, valor = par.split('=')
                            dados_corpo[chave] = valor

            funcao_rota = self.rotas.get((caminho, metodo))

            if funcao_rota:
                try:
                    corpo_resposta = await funcao_rota(dados_corpo) if metodo != 'GET' else await funcao_rota()
                    status = "200 OK"
                except Exception as e:
                    print(f"❌ Erro na rota async: {e}")
                    corpo_resposta = "<h1>500 Internal Server Error</h1>"
                    status = "500 ERROR"
            else:
                corpo_resposta = "<h1>404 Not Found</h1>"
                status = "404 NOT FOUND"

            self._log(metodo, caminho, status)

            corpo_bytes = corpo_resposta.encode('utf-8')
            resposta = (
                f"HTTP/1.1 {status}\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(corpo_bytes)}\r\n"
                "Connection: close\r\n\r\n"
            ).encode('utf-8') + corpo_bytes

            escritor.write(resposta)
            await escritor.drain()
        except Exception as e:
            print(f"⚠️ Erro de Conexão: {e}")
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
