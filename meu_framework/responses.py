
import json

class Response:
    """Classe base para todas as respostas HTTP do framework"""
    def __init__(self, body, status="200 OK", content_type="text/html"):
        self.body = body
        self.status = status
        self.content_type = content_type

    def serialize(self):
        """Transforma o objeto Response em bytes formatados para o protocolo HTTP/1.1"""
        # Garante que o corpo seja bytes
        if isinstance(self.body, str):
            body_bytes = self.body.encode('utf-8')
        elif isinstance(self.body, bytes):
            body_bytes = self.body
        else:
            # Se não for string nem bytes, tenta converter (ex: números)
            body_bytes = str(self.body).encode('utf-8')

        # Montagem do cabeçalho (Header)
        header = (
            f"HTTP/1.1 {self.status}\r\n"
            f"Content-Type: {self.content_type}; charset=utf-8\r\n"
            f"Content-Length: {len(body_bytes)}\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8')

        return header + body_bytes

class HTMLResponse(Response):
    """Resposta específica para documentos HTML"""
    def __init__(self, body, status="200 OK"):
        super().__init__(body, status, "text/html")

class JSONResponse(Response):
    """Resposta para APIs, converte dicionários Python em JSON automaticamente"""
    def __init__(self, data, status="200 OK"):
        body = json.dumps(data)
        super().__init__(body, status, "application/json")

class RedirectResponse(Response):
    """Resposta de redirecionamento (Status 302)"""
    def __init__(self, location):
        self.location = location
        super().__init__(body="", status="302 Found")

    def serialize(self):
        header = (
            f"HTTP/1.1 {self.status}\r\n"
            f"Location: {self.location}\r\n"
            "Content-Length: 0\r\n"
            "Connection: close\r\n"
            "\r\n"
        ).encode('utf-8')
        return header
