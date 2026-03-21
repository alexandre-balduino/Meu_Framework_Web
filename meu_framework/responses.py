
import json

class Response:
    """
    Classe base para todas as respostas HTTP do framework.
    Transforma conteúdo Python em uma string formatada para o navegador.
    """
    def __init__(self, body, status="200 OK", content_type="text/html"):
        """
        Inicializa a resposta.
        :param body: O conteúdo principal (texto, HTML, bytes).
        :param status: O código de status HTTP (ex: 200 OK, 404 NOT FOUND).
        :param content_type: O tipo de mídia (MIME type).
        """
        self.body = body
        self.status = status
        self.content_type = content_type
        self.headers = {
            "Content-Type": f"{self.content_type}; charset=utf-8",
            "Server": "MeuFramework/0.1.2",
            "Connection": "close"
        }

    def serialize(self):
        """
        Transforma o objeto Response em uma string de bytes pronta para o envio via socket.
        """
        # Se o corpo for string, converte para bytes
        if isinstance(self.body, str):
            encoded_body = self.body.encode("utf-8")
        else:
            encoded_body = self.body

        # Constrói a linha de status e os cabeçalhos
        response_line = f"HTTP/1.1 {self.status}\r\n"
        self.headers["Content-Length"] = len(encoded_body)
        
        headers_section = ""
        for key, value in self.headers.items():
            headers_section += f"{key}: {value}\r\n"
        
        # O protocolo HTTP exige uma linha vazia (\r\n) entre os headers e o corpo
        full_response = response_line.encode("utf-8") + \
                        headers_section.encode("utf-8") + \
                        b"\r\n" + \
                        encoded_body
        
        return full_response

class HTMLResponse(Response):
    """Resposta específica para documentos HTML."""
    def __init__(self, body, status="200 OK"):
        super().__init__(body, status, content_type="text/html")

class JSONResponse(Response):
    """Resposta específica para APIs, convertendo dicionários em JSON automaticamente."""
    def __init__(self, data, status="200 OK"):
        body = json.dumps(data)
        super().__init__(body, status, content_type="application/json")

class RedirectResponse(Response):
    """Resposta de redirecionamento para enviar o usuário para outra URL."""
    def __init__(self, location, status="302 FOUND"):
        super().__init__(body="", status=status)
        self.headers["Location"] = location
