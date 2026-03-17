import asyncio

class MeuFramework:
    def __init__(self):
        self.rotas = {}

    def get(self, caminho):
        """Decorador para registrar rotas GET."""
        def decorador(funcao):
            self.rotas[caminho] = funcao
            return funcao
        return decorador

    async def ler_request(self, reader, writer):
        dados = await reader.read(1024)
        requisicao = dados.decode()
        
        if not requisicao:
            writer.close()
            return

        linha_inicial = requisicao.split('\n')[0]
        metodo, path, _ = linha_inicial.split()

        if path in self.rotas:
            corpo = await self.rotas[path]()
            status = "200 OK"
        else:
            corpo = "<h1>404</h1><p>Página não encontrada</p>"
            status = "404 Not Found"

        corpo_bytes = corpo.encode('utf-8')
        resposta = (
            f"HTTP/1.1 {status}\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(corpo_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8') + corpo_bytes

        writer.write(resposta)
        await writer.drain()
        writer.close()

    def run(self, host='127.0.0.1', port=9000):
        async def main():
            server = await asyncio.start_server(self.ler_request, host, port)
            print(f"🚀 Framework rodando em http://{host}:{port}")
            async with server:
                await server.serve_forever()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\nServidor desligado.")
