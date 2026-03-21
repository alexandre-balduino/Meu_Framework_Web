
def tag(nome, conteudo="", **attrs):
    """Função base para gerar qualquer tag HTML com atributos."""
    # Converte class_="nome" para class="nome" e data_id para data-id
    html_attrs = " ".join([
        f'{k.replace("_", "-").rstrip("-")}="{v}"' 
        for k, v in attrs.items()
    ])
    
    abertura = f"<{nome} {html_attrs}>" if html_attrs else f"<{nome}>"
    
    # Tags auto-contidas (void elements)
    if nome in ['input', 'img', 'br', 'hr', 'link', 'meta']:
        return abertura
        
    return f"{abertura}{conteudo}</{nome}>"

# --- ESTRUTURA GLOBAL ---
def doc(titulo, conteudo, lang="pt-br", head_extra=""):
    """Gera um documento HTML5 completo e válido."""
    css_link = tag('link', rel="stylesheet", href="/static/estilo.css")
    
    head = tag('head', 
        tag('meta', charset="UTF-8") +
        tag('meta', name="viewport", content="width=device-width, initial-scale=1.0") +
        tag('title', titulo) +
        css_link +
        head_extra
    )
    
    body = tag('body', conteudo)
    
    return f"<!DOCTYPE html><html lang='{lang}'>{head}{body}</html>"

# --- TAGS DE TEXTO E BLOCO ---
def div(*args, **attrs): return tag('div', "".join(args), **attrs)
def section(*args, **attrs): return tag('section', "".join(args), **attrs)
def h1(texto, **attrs): return tag('h1', texto, **attrs)
def h2(texto, **attrs): return tag('h2', texto, **attrs)
def p(texto, **attrs): return tag('p', texto, **attrs)
def span(texto, **attrs): return tag('span', texto, **attrs)
def a(texto, href="#", **attrs): return tag('a', texto, href=href, **attrs)

# --- LISTAS E TABELAS ---
def ul(*args, **attrs): 
    itens = "".join([tag('li', str(item)) for item in args])
    return tag('ul', itens, **attrs)

def table(*args, **attrs): 
    # args devem ser tr()
    return tag('table', "".join(args), **attrs)

def tr(*args, **attrs): 
    # Gera uma linha com várias células (td)
    celulas = "".join([tag('td', str(item)) for item in args])
    return tag('tr', celulas, **attrs)

# --- FORMULÁRIOS (Essencial para HTMX) ---
def form(*args, **attrs): return tag('form', "".join(args), **attrs)
def input(**attrs): return tag('input', **attrs)
def label(texto, **attrs): return tag('label', texto, **attrs)
def button(texto, **attrs): return tag('button', texto, **attrs)
