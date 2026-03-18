
import socket
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
        """Imprime o log formatado no terminal"""
        horario = datetime.now().strftime('%H:%M:%S')
        cor = "\033[92m" if "200" in status else "\033[91m" # Verde para OK, Vermelho para Erro
        print(f"[{horario}] {metodo} {caminho} - {cor}{status}\033[0m")

    def _processar_requisicoes(self, servidor):
        while True:
            conexao, endereco = servidor.accept()
            try:
                requisicao = conexao.recv(4096).decode()
                if not requisicao: continue

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
                        corpo_res = funcao_rota(dados_corpo) if metodo != 'GET' else funcao_rota()
                        status = "200 OK"
                    except Exception as e:
                        print(f"❌ Erro na execução da rota: {e}")
                        corpo_res = "<h1>500 Internal Server Error</h1>"
                        status = "500 ERROR"
                else:
                    corpo_res = "<h1>404 Not Found</h1>"
                    status = "404 NOT FOUND"

                self._log(metodo, caminho, status)

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

    def servir(self, host='127.0.0.1', porta=9000):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen(5)
        print(f"🚀 Servidor Síncrono em http://{host}:{porta}")
        try:
            self._processar_requisicoes(servidor)
        except KeyboardInterrupt:
            print("\n🛑 Servidor desligado.")
        finally:
            servidor.close()
