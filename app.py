
from meu_framework import MeuFramework
from meu_framework.html import h1, p, div, a, html_full

app = MeuFramework()

@app.rota("/rapido")
async def pagina_rapida():
    # Construindo o corpo programaticamente
    conteudo = div(
        h1("Página Gerada no Python! 🐍"),
        p("Esta página não usou um arquivo .html externo."),
        a("Voltar para Home", href="/"),
        style="padding: 20px; border: 2px solid blue;"
    )
    return html_full("Minha Página Dinâmica", conteudo)

@app.rota("/")
async def home():
    # Ainda usando o template engine para a home
    return app.render_template("index.html")

@app.rota("/boas-vindas", metodos=["POST"])
async def boas_vindas(usuario):
    return app.render_template("index.html", nome=usuario)


if __name__ == "__main__":
    app.servir()

