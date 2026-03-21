
import asyncio
import os
from datetime import datetime
from .responses import Response, HTMLResponse

class BuiltInServer:
    def __init__(self, app):
        """
        O Servidor recebe a instância do framework para saber como processar as rotas.
        """
        self.app = app

    def _obter_tipo_mime(self, caminho_arquivo):
        """Mapeia extensões de arquivo para o Content-Type correto"""
        ext = os.path.splitext(caminho_arquivo)[1].lower()
        tipos = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.ico': 'image/x-icon',
            '.html': 'text/html'
        }
        return tipos.get(ext, 'application/octet-stream')

    def _log(self, metodo, caminho, status):
        """Log colorido para o terminal"""
        horario = datetime.now().strftime('%H:%M:%S')
        cor = "\033[92m" if "200" in status else "\033[93m" # Verde para OK, Amarelo para Erros
        print(f"[{horario}] {metodo} {caminho} - {cor}{status}\033[0m")

    async def gerenciar_conexao(self, leitor, escritor):
        """Lógica principal de cada conexão via Socket"""
        try:
            # 1. Ler a requisição bruta
            dados = await leitor.read(4096)
            if not dados:
                return
            
            requisicao = dados.decode(errors='ignore')
            linhas = requisicao.split('\r\n')
            if not linhas or len(linhas[0].split(' ')) < 2:
                return

            metodo, caminho, _ = linhas[0].split(' ')

            # 2. VERIFICAÇÃO DE ARQUIVOS ESTÁTICOS (CSS, JS, Imagens)
            if caminho.startswith(f'/{self.app.pasta_static}/'):
                nome_arquivo = caminho.replace(f'/{self.app.pasta_static}/', '', 1)
                caminho_disco = os.path.join(self.app.caminho_static_abs, nome_arquivo)

                if os.path.exists(caminho_disco) and os.path.isfile(caminho_disco):
                    with open(caminho_disco, 'rb') as f:
                        conteudo = f.read()
                    
                    mime = self._obter_tipo_mime(caminho_disco)
                    res = Response(conteudo, content_type=mime)
                    escritor.write(res.serialize())
                    await escritor.drain()
                    self._log(metodo, caminho, "200 OK (Static)")
                    return

            # 3. PROCESSAMENTO DE ROTAS DINÂMICAS
            # Parser simples de corpo para POST
            dados_corpo = {}
            if metodo == 'POST':
                corpo = linhas[-1]
                if corpo and '=' in corpo:
                    for par in corpo.split('&'):
                        if '=' in par:
                            k, v = par.split('=')
                            dados_corpo[k] = v

            # Chama o Core para processar a lógica
            corpo_res, status_str = await self.app.processar_rota(metodo, caminho, dados_corpo)
            
            # Encapsula em um objeto Response para serializar corretamente
            final_res = HTMLResponse(corpo_res, status=status_str)
            
            self._log(metodo, caminho, status_str)
            escritor.write(final_res.serialize())
            await escritor.drain()

        except Exception as e:
            print(f"❌ Erro no Servidor: {e}")
        finally:
            escritor.close()
            await escritor.wait_closed()

    def run(self, host='127.0.0.1', porta=9000):
        """Inicia o loop de eventos do asyncio"""
        async def main():
            server = await asyncio.start_server(self.gerenciar_conexao, host, porta)
            print(f"🚀 Servidor Nativo rodando em http://{host}:{porta}")
            print(f"📂 Servindo arquivos estáticos de: {self.app.caminho_static_abs}")
            async with server:
                await server.serve_forever()
        
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print("\n🛑 Servidor finalizado pelo usuário.")
