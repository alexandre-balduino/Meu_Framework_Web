
def tag(nome, conteudo="", **attrs):
    """Função base para gerar qualquer tag HTML com atributos."""
    html_attrs = " ".join([
        f'{k.replace("_", "-").rstrip("-")}="{v}"' 
        for k, v in attrs.items()
    ])
    abertura = f"<{nome} {html_attrs}>" if html_attrs else f"<{nome}>"
    
    # Tags auto-contidas
    if nome in ['input', 'img', 'br', 'hr', 'link', 'meta', 'source']:
        return abertura
    return f"{abertura}{conteudo}</{nome}>"

# --- ESTRUTURA E SEMÂNTICA ---
def doc(titulo, conteudo, lang="pt-br", head_extra=""):
    css = tag('link', rel="stylesheet", href="/static/estilo.css")
    h = tag('head', tag('meta', charset="UTF-8") + tag('title', titulo) + css + head_extra)
    return f"<!DOCTYPE html><html lang='{lang}'>{h}{tag('body', conteudo)}</html>"

def header(*args, **attrs): return tag('header', "".join(args), **attrs)
def footer(*args, **attrs): return tag('footer', "".join(args), **attrs)
def main(*args, **attrs): return tag('main', "".join(args), **attrs)
def nav(*args, **attrs): return tag('nav', "".join(args), **attrs)
def aside(*args, **attrs): return tag('aside', "".join(args), **attrs)
def article(*args, **attrs): return tag('article', "".join(args), **attrs)

# --- CABEÇALHOS (H1-H6) ---
def h1(t, **a): return tag('h1', t, **a)
def h2(t, **a): return tag('h2', t, **a)
def h3(t, **a): return tag('h3', t, **a)
def h4(t, **a): return tag('h4', t, **a)
def h5(t, **a): return tag('h5', t, **a)
def h6(t, **a): return tag('h6', t, **a)

# --- TEXTO E BLOCOS ---
def div(*args, **attrs): return tag('div', "".join(args), **attrs)
def p(t, **a): return tag('p', t, **a)
def span(t, **a): return tag('span', t, **a)
def a(t, href="#", **a): return tag('a', t, href=href, **a)
def li(t, **a): return tag('li', t, **a)
def ul(*args, **attrs): return tag('ul', "".join([li(i) if isinstance(i, str) else i for i in args]), **attrs)
def br(): return tag('br')
def hr(**a): return tag('hr', **a)

# --- TABELAS ---
def table(*args, **attrs): return tag('table', "".join(args), **attrs)
def thead(*args, **attrs): return tag('thead', "".join(args), **attrs)
def tbody(*args, **attrs): return tag('tbody', "".join(args), **attrs)
def tr(*args, **attrs): return tag('tr', "".join([tag('td', str(i)) if not str(i).startswith('<td') else i for i in args]), **attrs)

# --- FORMULÁRIOS ---
def form(*args, **attrs): return tag('form', "".join(args), **attrs)
def input(**a): return tag('input', **a)
def label(t, **a): return tag('label', t, **a)
def button(t, **a): return tag('button', t, **a)
def textarea(t="", **a): return tag('textarea', t, **a)
def select(*args, **attrs): return tag('select', "".join(args), **attrs)
def option(t, **a): return tag('option', t, **a)

# --- MÍDIA E SCRIPTS ---
def img(src, alt="", **a): return tag('img', src=src, alt=alt, **a)
def video(*args, **attrs): return tag('video', "".join(args), **attrs)
def script(codigo="", src="", **attrs): 
    if src: attrs['src'] = src
    return tag('script', codigo, **attrs)
def iframe(src, **a): return tag('iframe', "", src=src, **a)
