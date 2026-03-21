
import asyncio
import os
from .logger import Logger
from .responses import Response, HTMLResponse

class BuiltInServer:
    """
    Servidor HTTP assíncrono embutido para o framework.
    Lida com sockets, parsing de cabeçalhos e entrega de arquivos estáticos.
    """
    def __init__(self, app):
        """
        Inicializa o servidor.
        :param app: Instância da classe MyFramework (o core).
        """
        self.app = app

    def _get_mime_type(self, file_path):
        """
        Retorna o tipo de conteúdo (MIME) baseado na extensão do arquivo.
        """
        ext = os.path.splitext(file_path)[1].lower()
        types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.ico': 'image/x-icon',
            '.html': 'text/html',
            '.json': 'application/json'
        }
        return types.get(ext, 'application/octet-stream')

    async def handle_connection(self, reader, writer):
        """
        Gerencia uma conexão individual de um cliente.
        Lê a requisição HTTP, processa cabeçalhos e envia a resposta.
        """
        method = "???"
        path = "???"
        
        try:
            # 1. Lê os dados brutos (buffer de 8KB para suportar headers grandes)
            data = await reader.read(8192)
            if not data:
                return
            
            # Decodifica e separa Cabeçalhos do Corpo (separados por \r\n\r\n no HTTP)
            raw_request = data.decode(errors='ignore')
            parts = raw_request.split('\r\n\r\n', 1)
            header_section = parts[0]
            body = parts[1] if len(parts) > 1 else ""

            lines = header_section.split('\r\n')
            if not lines or len(lines[0].split(' ')) < 2:
                return

            # Primeira linha da requisição (ex: GET /index HTTP/1.1)
            method, path, _ = lines[0].split(' ')

            # 2. Parsing de Headers (converte para dicionário)
            headers = {}
            for line in lines[1:]:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key] = value

            # 3. Gerenciamento de Arquivos Estáticos (CSS, JS, Imagens)
            if path.startswith(f'/{self.app.static_folder}/'):
                # Remove o prefixo da pasta estática para achar o arquivo real
                file_name = path.replace(f'/{self.app.static_folder}/', '', 1)
                full_path = os.path.join(self.app.static_abs_path, file_name)

                if os.path.exists(full_path) and os.path.isfile(full_path):
                    with open(full_path, 'rb') as f:
                        content = f.read()
                    
                    mime = self._get_mime_type(full_path)
                    res = Response(content, content_type=mime)
                    writer.write(res.serialize())
                    Logger.info(method, path, 200)
                    return
                else:
                    Logger.info(method, path, 404)
                    res = HTMLResponse("<h1>404 Static File Not Found</h1>", status="404 NOT FOUND")
                    writer.write(res.serialize())
                    return

            # 4. Envia para o Dispatcher do Framework (Core)
            # Retorna o conteúdo da página e a string de status (ex: "200 OK")
            response_body, status_str = await self.app.dispatch(method, path, headers, body)
            
            # Extrai o número do status para o Logger (ex: de "200 OK" pega 200)
            status_code = int(status_str.split(' ')[0])
            Logger.info(method, path, status_code)
            
            # Cria a resposta final e envia para o socket
            final_res = HTMLResponse(response_body, status=status_str)
            writer.write(final_res.serialize())

        except Exception as e:
            # Captura erros inesperados para o servidor não "morrer"
            Logger.error(f"Erro ao processar {method} {path}: {e}")
            res = HTMLResponse(
                f"<h1>500 Internal Server Error</h1><p>{e}</p>", 
                status="500 INTERNAL SERVER ERROR"
            )
            writer.write(res.serialize())

        finally:
            # Garante o fechamento limpo da conexão
            try:
                await writer.drain()
                writer.close()
                await writer.wait_closed()
            except:
                pass

    def run(self, host='127.0.0.1', port=9000):
        """
        Inicia o loop de eventos e coloca o servidor para rodar.
        """
        async def main():
            server = await asyncio.start_server(self.handle_connection, host, port)
            addr = server.sockets[0].getsockname()
            print(f"\n🚀 {Logger.BOLD}Server Running{Logger.RESET} at http://{addr[0]}:{addr[1]}")
            print(f"📂 Static folder: {self.app.static_abs_path}\n")
            
            async with server:
                await server.serve_forever()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print(f"\n🛑 {Logger.YELLOW}Server stopped by user.{Logger.RESET}")
