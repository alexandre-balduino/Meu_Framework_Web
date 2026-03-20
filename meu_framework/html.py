
def tag(nome, conteudo, **attrs):
    """Função base para gerar qualquer tag HTML com atributos"""
    html_attrs = " ".join([f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items()])
    abertura = f"<{nome} {html_attrs}>" if html_attrs else f"<{nome}>"
    return f"{abertura}{conteudo}</{nome}>"

# Atalhos para as tags mais comuns
def h1(texto, **attrs): return tag('h1', texto, **attrs)
def h2(texto, **attrs): return tag('h2', texto, **attrs)
def p(texto, **attrs): return tag('p', texto, **attrs)
def div(*args, **attrs): return tag('div', "".join(args), **attrs)
def a(texto, href="#", **attrs): return tag('a', texto, href=href, **attrs)
def button(texto, **attrs): return tag('button', texto, **attrs)

def html_full(titulo, corpo):
    """Gera uma estrutura HTML completa básica"""
    return (
        "<!DOCTYPE html><html><head>"
        f"<title>{titulo}</title>"
        '<meta charset="UTF-8">'
        '<link rel="stylesheet" href="/static/estilo.css">'
        f"</head><body>{corpo}</body></html>"
    )
