
import os
from jinja2 import Environment, FileSystemLoader

class TemplateEngine:
    def __init__(self, caminho_templates_abs):
        """
        Inicializa o motor de templates.
        :param caminho_templates_abs: Caminho total no disco para a pasta de templates.
        """
        self.path_abs = caminho_templates_abs
        
        # Verificação amigável para o desenvolvedor no console
        if not os.path.exists(self.path_abs):
            print(f"\n[SISTEMA] ⚠️ AVISO: A pasta de templates não foi encontrada em:")
            print(f"          > {self.path_abs}")
            print(f"          Certifique-se de que a pasta 'templates' existe no seu projeto.\n")
        
        # Configura o ambiente do Jinja2
        # autoescape=True é uma boa prática de segurança contra ataques XSS
        self.env = Environment(
            loader=FileSystemLoader(self.path_abs),
            autoescape=True 
        )

    def render(self, template_name, **context):
        """
        Renderiza um arquivo HTML usando o dicionário de contexto.
        """
        try:
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            # Caso o arquivo .html não exista dentro da pasta
            return f"<h1>Erro de Template</h1><p>O arquivo '{template_name}' não foi encontrado ou está corrompido.</p><p>Erro: {e}</p>"
