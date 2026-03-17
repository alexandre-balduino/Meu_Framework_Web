
import socket

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

    def _processar_requisicoes(self, servidor):
        while True:
            conexao, endereco = servidor.accept()
            try:
                requisicao = conexao.recv(4096).decode()
                if not requisicao:
                    continue

                linhas = requisicao.split('\r\n')
                metodo, caminho, _ = linhas[0].split(' ')

                dados_formulario = {}
                if metodo == 'POST':
                    corpo = linhas[-1]
                    if corpo:
                        for par in corpo.split('&'):
                            # Adicionada a verificação para garantir simetria com o async
                            if '=' in par:
                                chave, valor = par.split('=')
                                dados_formulario[chave] = valor

                funcao_rota = self.rotas.get((caminho, metodo))
                
                if funcao_rota:
                    corpo_res = funcao_rota(dados_formulario) if metodo == 'POST' else funcao_rota()
                    status = "200 OK"
                else:
                    corpo_res = "<h1>404 Not Found</h1>"
                    status = "404 NOT FOUND"

                resposta = (
                    f"HTTP/1.1 {status}\r\n"
                    "Content-Type: text/html; charset=utf-8\r\n"
                    f"Content-Length: {len(corpo_res.encode('utf-8'))}\r\n"
                    "Connection: close\r\n\r\n"
                    f"{corpo_res}"
                )
                conexao.sendall(resposta.encode('utf-8'))
            finally:
                conexao.close()

    def run(self, host='127.0.0.1', porta=9000):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen(5)
        
        print(f"🚀 Servidor Síncrono em http://{host}:{porta}")
        
        try:
            self._processar_requisicoes(servidor)
        except KeyboardInterrupt:
            print("\nServidor desligado.")
        finally:
            servidor.close()
