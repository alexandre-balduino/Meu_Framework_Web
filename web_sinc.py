
import socket
import re
from datetime import datetime

class MeuFramework:
    def __init__(self):
        self.rotas = [] # Mudamos para lista para manter a ordem e iterar

    def rota(self, caminho, metodos=['GET']):
        def decorador(funcao):
            # Converte <parametro> para um grupo de captura regex
            # Ex: /perfil/<nome> -> ^/perfil/(?P<nome>[^/]+)$
            padrao_regex = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', caminho)
            regex_compilada = re.compile(f"^{padrao_regex}$")
            
            for metodo in metodos:
                self.rotas.append({
                    'metodo': metodo.upper(),
                    'regex': regex_compilada,
                    'funcao': funcao
                })
            return funcao
        return decorador

    def _log(self, metodo, caminho, status):
        horario = datetime.now().strftime('%H:%M:%S')
        cor = "\033[92m" if "200" in status else "\033[91m"
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
                    if corpo and '=' in corpo:
                        for par in corpo.split('&'):
                            if '=' in par:
                                k, v = par.split('=')
                                dados_corpo[k] = v

                # Busca a rota por Regex
                funcao_rota = None
                params_url = {}
                
                for r in self.rotas:
                    match = r['regex'].match(caminho)
                    if match and r['metodo'] == metodo:
                        funcao_rota = r['funcao']
                        params_url = match.groupdict() # Extrai os <parametros>
                        break

                if funcao_rota:
                    try:
                        # Une os dados do corpo com os da URL
                        argumentos = {**params_url, **dados_corpo} if dados_corpo else params_url
                        corpo_res = funcao_rota(**argumentos) if argumentos else funcao_rota()
                        status = "200 OK"
                    except Exception as e:
                        print(f"❌ Erro: {e}")
                        corpo_res = "<h1>500 Internal Server Error</h1>"
                        status = "500 ERROR"
                else:
                    corpo_res = "<h1>404 Not Found</h1>"
                    status = "404 NOT FOUND"

                self._log(metodo, caminho, status)
                resposta = (f"HTTP/1.1 {status}\r\nContent-Type: text/html\r\n"
                            f"Content-Length: {len(corpo_res.encode())}\r\n\r\n{corpo_res}")
                conexao.sendall(resposta.encode('utf-8'))
            finally:
                conexao.close()

    def servir(self, host='127.0.0.1', porta=9000):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, porta))
        servidor.listen(5)
        print(f"🚀 Servidor Síncrono em http://{host}:{porta}")
        try: self._processar_requisicoes(servidor)
        except KeyboardInterrupt: print("\n🛑 Desligado.")
        finally: servidor.close()
