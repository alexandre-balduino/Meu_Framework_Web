
from datetime import datetime

class Logger:
    """
    Responsável por exibir logs coloridos no terminal para facilitar a depuração.
    """
    # Cores ANSI para o terminal
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    @staticmethod
    def info(method, path, status_code):
        """
        Exibe uma mensagem de informação sobre uma requisição HTTP.
        :param method: Método HTTP (GET, POST, etc.)
        :param path: Caminho da URL acessada
        :param status_code: Código de status retornado (ex: 200, 404, 500)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Define a cor baseada no Status Code (Família 200, 300, 400 ou 500)
        if status_code >= 500:
            color = Logger.RED
        elif status_code >= 400:
            color = Logger.YELLOW
        elif status_code >= 300:
            color = Logger.CYAN
        else:
            color = Logger.GREEN

        # Imprime no formato: [12:30:05] GET /home -> 200
        print(
            f"[{timestamp}] {Logger.BOLD}{method}{Logger.RESET} "
            f"{path} -> {color}{status_code}{Logger.RESET}"
        )

    @staticmethod
    def error(message):
        """
        Exibe uma mensagem de erro crítica em vermelho.
        :param message: A descrição do erro ou exceção capturada.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {Logger.RED}{Logger.BOLD}![ERROR]! {message}{Logger.RESET}")

    @staticmethod
    def debug(message):
        """
        Exibe mensagens de depuração simples.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [DEBUG] {message}")
