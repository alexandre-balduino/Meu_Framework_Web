
import asyncio

class MeuFramework:
    def __init__(self):
        self.rotas = {}

    def get(self, caminho):
        def decorador(funcao):
            self.rotas[(caminho, 'GET')] = funcao
            return funcao
        return decorador

    def post(self, caminho):
        def decorador(funcao):
            self.rotas[(caminho, 'POST')] = funcao
            return funcao
        return decorador

    async def gerenciar_conexao(self, leitor, escritor):
        try:
            dados = await leitor.read(4096)
            requisicao = dados.decode()
            
            if not requisicao:
                escritor.close()
                return

            linhas = requisicao.split('\r\n')
            primeira_linha = linhas[0]
            metodo, caminho, _ = primeira_linha.split(' ')

            dados_formulario = {}
            if metodo == 'POST':
                corpo = linhas[-1]
                if corpo:
                    for par in corpo.split('&'):
                        if '=' in par:
                            chave, valor = par.split('=')
                            dados_formulario[chave] = valor

            funcao_rota = self.rotas.get((caminho, metodo))

            if funcao_rota:
                if metodo == 'POST':
                    corpo_resposta = await funcao_rota(dados_formulario)
                else:
                    corpo_resposta = await funcao_rota()
                status = "200 OK"
            else:
                corpo_resposta = "<h1>404 Not Found</h1>"
                status = "404 NOT FOUND"

            corpo_bytes = corpo_resposta.encode('utf-8')
            resposta = (
                f"HTTP/1.1 {status}\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(corpo_bytes)}\r\n"
                "Connection: close\r\n"
                "\r\n"
            ).encode('utf-8') + corpo_bytes

            escritor.write(resposta)
            await escritor.drain()
        except Exception as e:
            print(f"Erro ao processar requisição: {e}")
        finally:
            escritor.close()
            await escritor.wait_closed()

    def run(self, host='127.0.0.1', porta=9000):
        async def main():
            servidor = await asyncio.start_server(self.gerenciar_conexao, host, porta)
            print(f"🚀 Servidor Assíncrono em http://{host}:{porta}")
            async with servidor:
                await servidor.serve_forever()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nServidor desligado.")
