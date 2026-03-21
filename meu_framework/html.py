
def tag(nome, conteudo="", **attrs):
    """Função base para gerar qualquer tag HTML com atributos."""
    # Converte class_="nome" para class="nome" e data_id para data-id
    html_attrs = " ".join([
        f'{k.replace("_", "-").rstrip("-")}="{v}"' 
        for k, v in attrs.items()
    ])
    
    abertura = f"<{nome} {html_attrs}>" if html_attrs else f"<{nome}>"
    
    # Tags auto-contidas (void elements / self-closing)
    if nome in ['input', 'img', 'br', 'hr', 'link', 'meta']:
        return abertura
        
    return f"{abertura}{conteudo}</{nome}>"

# --- ESTRUTURA DO DOCUMENTO ---
def doc(titulo, conteudo, lang="pt-br", head_extra=""):
    """Gera um documento HTML5 completo e válido com CSS automático."""
    css_link = tag('link', rel="stylesheet", href="/static/estilo.css")
    
    # Monta o Head
    h = tag('head', 
        tag('meta', charset="UTF-8") +
        tag('meta', name="viewport", content="width=device-width, initial-scale=1.0") +
        tag('title', titulo) +
        css_link +
        head_extra
    )
    
    # Monta o Body
    b = tag('body', conteudo)
    
    return f"<!DOCTYPE html><html lang='{lang}'>{h}{b}</html>"

# --- TAGS ESTRUTURAIS ---
def head(*args): return tag('head', "".join(args))
def body(*args, **attrs): return tag('body', "".join(args), **attrs)
def header(*args, **attrs): return tag('header', "".join(args), **attrs)
def footer(*args, **attrs): return tag('footer', "".join(args), **attrs)
def main(*args, **attrs): return tag('main', "".join(args), **attrs)
def nav(*args, **attrs): return tag('nav', "".join(args), **attrs)

# --- CABEÇALHOS (H1-H6) ---
def h1(texto, **attrs): return tag('h1', texto, **attrs)
def h2(texto, **attrs): return tag('h2', texto, **attrs)
def h3(texto, **attrs): return tag('h3', texto, **attrs)
def h4(texto, **attrs): return tag('h4', texto, **attrs)
def h5(texto, **attrs): return tag('h5', texto, **attrs)
def h6(texto, **attrs): return tag('h6', texto, **attrs)

# --- BLOCOS E TEXTO ---
def div(*args, **attrs): return tag('div', "".join(args), **attrs)
def p(texto, **attrs): return tag('p', texto, **attrs)
def span(texto, **attrs): return tag('span', texto, **attrs)
def a(texto, href="#", **attrs): return tag('a', texto, href=href, **attrs)
def br(): return tag('br')
def hr(**attrs): return tag('hr', **attrs)

# --- LISTAS E TABELAS ---
def ul(*args, **attrs): 
    itens = "".join([tag('li', str(item)) for item in args])
    return tag('ul', itens, **attrs)

def table(*args, **attrs): return tag('table', "".join(args), **attrs)
def tr(*args, **attrs): 
    celulas = "".join([tag('td', str(item)) for item in args])
    return tag('tr', celulas, **attrs)

# --- FORMULÁRIOS ---
def form(*args, **attrs): return tag('form', "".join(args), **attrs)
def input(**attrs): return tag('input', **attrs)
def label(texto, **attrs): return tag('label', texto, **attrs)
def button(texto, **attrs): return tag('button', texto, **attrs)
def textarea(texto="", **attrs): return tag('textarea', texto, **attrs)

# --- MÍDIA ---
def img(src, alt="", **attrs): return tag('img', src=src, alt=alt, **attrs)
