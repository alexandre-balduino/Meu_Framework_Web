
from meu_framework import MyFramework, BuiltInServer, Model, html

# 1. Inicializa o Framework (detecção automática de pastas ativada)
app = MyFramework()

# 2. Define o Modelo de Dados (ORM)
class Lead(Model):
    table_name = "leads"
    fields = {
        "name": "TEXT",
        "email": "TEXT",
        "message": "TEXT"
    }

# Cria a tabela no banco de dados 'data.db' se não existir
Lead.create_table()

# --- ROTA 1: Home usando Template Externo ---
@app.route("/")
async def home(request):
    """Renderiza o arquivo index.html da pasta templates."""
    return app.render_template("index.html")

# --- ROTA 2: Cadastro usando Funções HTML (Python DSL) ---
@app.route("/register")
async def register_page(request):
    """Gera o formulário inteiramente via código Python."""
    
    form_content = html.div(
        html.h1("Cadastro de Lead"),
        html.p("Preencha o formulário abaixo gerado via Python DSL:"),
        
        html.form(
            html.div(
                html.label("Nome:", for_="nome"),
                html.input_(type="text", name="user_name", id="nome", required="required"),
            ),
            html.div(
                html.label("E-mail:", for_="email"),
                html.input_(type="email", name="user_email", id="email", required="required"),
            ),
            html.div(
                html.label("Mensagem:", for_="msg"),
                html.textarea("Olá, gostaria de saber mais...", name="user_msg", id="msg"),
            ),
            html.button("Enviar Dados", type="submit", style="margin-top: 10px;"),
            
            action="/submit", method="POST"
        ),
        style="padding: 20px; max-width: 400px; margin: auto; border: 1px solid #ccc; border-radius: 8px;"
    )
    
    # Usa a função 'doc' que corrigimos no html.py
    return html.doc("Cadastro - Meu Framework", form_content)

# --- ROTA 3: Processamento do Formulário (POST) ---
@app.route("/submit", methods=["POST"])
async def handle_submit(request):
    """Recebe os dados do formulário e salva no banco de dados."""
    
    # Pega os dados via objeto Request
    name = request.form.get("user_name")
    email = request.form.get("user_email")
    msg = request.form.get("user_msg")

    # Salva no Banco de Dados usando o ORM
    Lead.create(name=name, email=email, message=msg)

    # Retorna o template da home passando o nome do usuário para o Jinja2
    return app.render_template("index.html", nome=name)

# --- ROTA 4: Listagem de Dados ---
@app.route("/list")
async def list_leads(request):
    """Busca todos os leads salvos e exibe em uma lista HTML."""
    all_leads = Lead.all()
    
    items = []
    for lead in all_leads:
        items.append(html.li(f"{lead['name']} ({lead['email']}) - {lead['message']}"))
    
    content = html.div(
        html.h1("Lista de Leads Cadastrados"),
        html.ul(*items) if items else html.p("Nenhum lead encontrado."),
        html.a("Voltar para Home", href="/")
    )
    
    return html.doc("Lista de Contatos", content)

# 3. Inicia o Servidor
if __name__ == "__main__":
    server = BuiltInServer(app)
    server.run(host='127.0.0.1', port=9000)
