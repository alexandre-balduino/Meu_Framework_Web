
from web_app import MeuFramework

app = MeuFramework()

# Rota para exibir o formulário (GET)
@app.rota("/")
async def home():
    return app.render_template("index.html")

# Rota para processar o nome (POST)
@app.rota("/boas-vindas", metodos=["POST"])
async def boas_vindas(usuario):
    # O framework extrai 'usuario' automaticamente do corpo do POST
    return app.render_template("index.html", nome=usuario)

if __name__ == "__main__":
    app.servir()
