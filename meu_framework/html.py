
def tag(nome, conteudo="", **attrs):
    """Função base robusta para gerar tags"""
    # Converte argumentos_python="valor" para argumentos-html="valor"
    html_attrs = " ".join([f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items()])
    abertura = f"<{nome} {html_attrs}>" if html_attrs else f"<{nome}>"
    
    # Tags que não fecham (self-closing)
    if nome in ['input', 'img', 'br', 'hr', 'link', 'meta']:
        return abertura
        
    return f"{abertura}{conteudo}</{nome}>"

# Estrutura
def div(*args, **attrs): return tag('div', "".join(args), **attrs)
def section(*args, **attrs): return tag('section', "".join(args), **attrs)
def span(texto, **attrs): return tag('span', texto, **attrs)

# Listas e Tabelas
def ul(*args, **attrs): return tag('ul', "".join([tag('li', i) for i in args]), **attrs)
def ol(*args, **attrs): return tag('ol', "".join([tag('li', i) for i in args]), **attrs)
def table(*args, **attrs): return tag('table', "".join(args), **attrs)
def tr(*args, **attrs): return tag('tr', "".join([tag('td', i) for i in args]), **attrs)

# Formulários (Importante para HTMX!)
def form(*args, **attrs): return tag('form', "".join(args), **attrs)
def input(**attrs): return tag('input', **attrs)
def label(texto, **attrs): return tag('label', texto, **attrs)
def select(*args, **attrs): 
    options = "".join([tag('option', opt, value=opt) for opt in args])
    return tag('select', options, **attrs)
