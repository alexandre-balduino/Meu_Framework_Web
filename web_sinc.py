
import socket

class MeuFramework:
    def __init__(self):
        self.rotas = {}

    def get(self, caminho):
        def decorador(funcao):
            self.rotas[caminho] = funcao
            return funcao
        return decorador

    def run(self, host='127.0.0.1', porta=9000):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Evita erro de porta ocupada
        servidor.bind((host, porta))
        servidor.listen(5)
        
        print(f"🚀 Servidor rodando em http://{host}:{porta}")

        while True:
            conexao, endereco = servidor.accept()
            requisicao = conexao.recv(1024).decode()
            
            if not requisicao:
                continue
                
            primeira_linha = requisicao.split('\n')[0]
            metodo, caminho, _ = primeira_linha.split(' ')

            funcao_rota = self.rotas.get(caminho)
            
            if funcao_rota:
                corpo = funcao_rota()
                status = "200 OK"
            else:
                corpo = "<h1>404 Not Found</h1>"
                status = "404 NOT FOUND"

            resposta = (
                f"HTTP/1.1 {status}\r\n"
                "Content-Type: text/html; charset=utf-8\r\n"
                f"Content-Length: {len(corpo.encode('utf-8'))}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{corpo}"
            )

            conexao.sendall(resposta.encode('utf-8'))
            conexao.close()
