
import socket

# 1. Configurações básicas de rede
HOST = '127.0.0.1'
PORT = 9000

# 2. Cria o objeto de comunicação (Socket)
# AF_INET = IPV4 | SOCK_STREAM = TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Servidor rodando em http://{HOST}:{PORT}")

while True:
    # 3. Espera uma conexão (O navegador batendo na porta)
    client_connection, client_address = server_socket.accept()
    
    # 4. Lê o que o navegador enviou (A Requisição)
    request = client_connection.recv(1024).decode()
    print("--- Requisição Recebida ---")
    print(request)
    
    # 5. Monta a Resposta HTTP manualmente
    # O navegador precisa dessa estrutura exata: Versão Status \n Cabeçalho \n\n Corpo
    response = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: text/html; charset=utf-8\r\n"
        "\r\n"
        "<h1>Olá Mundo!</h1>"
        "<p>Este é um servidor Socket puro, sem framework nenhum.</p>"
    )
    
    # 6. Envia a resposta e fecha a conexão do cliente
    client_connection.sendall(response.encode())
    client_connection.close()
