
import asyncio

class MeuFramework:
    def __init__(self):
        self.rotas = {}

    def get(self, caminho):
        def decorador(funcao):
            self.rotas[caminho] = funcao
            return funcao
        return decorador

    async def gerenciar_conexao(self, leitor, escritor):
        dados = await leitor.read(1024)
        requisicao = dados.decode()
        
        if not requisicao:
            escritor.close()
            await escritor.wait_closed()
            return

        primeira_linha = requisicao.split('\n')[0]
        metodo, caminho, _ = primeira_linha.split(' ')

        funcao_rota = self.rotas.get(caminho)

        if funcao_rota:
            corpo = await funcao_rota()
            status = "200 OK"
        else:
            corpo = "<h1>404 Not Found</h1>"
            status = "404 NOT FOUND"

        corpo_bytes = corpo.encode('utf-8')
        resposta = (
            f"HTTP/1.1 {status}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(corpo_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8') + corpo_bytes

        escritor.write(resposta)
        await escritor.drain() 
        escritor.close()
        await escritor.wait_closed()

    def run(self, host='127.0.0.1', porta=9000):
        async def main():
            servidor = await asyncio.start_server(self.gerenciar_conexao, host, porta)
            print(f"🚀 Servidor rodando em http://{host}:{porta}")
            async with servidor:
                await servidor.serve_forever()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nServidor desligado.")
