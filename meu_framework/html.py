
def tag(_tag_name, *content, **attrs):
    """
    Função base universal para gerar qualquer tag HTML.
    Utiliza _tag_name com underscore para evitar conflitos com o atributo 'name' do HTML.
    """
    processed_attrs = []
    for k, v in attrs.items():
        # Remove o underscore no final para permitir palavras reservadas (class_, for_)
        # Converte underscores no meio em hifens (data_id -> data-id)
        key = k.rstrip("_").replace("_", "-")
        processed_attrs.append(f' {key}="{v}"')
    
    props = "".join(processed_attrs)
    inner = "".join(list(content))
    return f"<{_tag_name}{props}>{inner}</{_tag_name}>"

# --- Cabeçalhos (Headers) ---
def h1(*args, **kwargs): return tag("h1", *args, **kwargs)
def h2(*args, **kwargs): return tag("h2", *args, **kwargs)
def h3(*args, **kwargs): return tag("h3", *args, **kwargs)
def h4(*args, **kwargs): return tag("h4", *args, **kwargs)
def h5(*args, **kwargs): return tag("h5", *args, **kwargs)
def h6(*args, **kwargs): return tag("h6", *args, **kwargs)

# --- Tags de Layout e Texto ---
def div(*args, **kwargs): return tag("div", *args, **kwargs)
def section(*args, **kwargs): return tag("section", *args, **kwargs)
def span(*args, **kwargs): return tag("span", *args, **kwargs)
def p(*args, **kwargs): return tag("p", *args, **kwargs)
def a(*args, **kwargs): return tag("a", *args, **kwargs)
def strong(*args, **kwargs): return tag("strong", *args, **kwargs)
def em(*args, **kwargs): return tag("em", *args, **kwargs)

# --- Listas ---
def ul(*args, **kwargs): return tag("ul", *args, **kwargs)
def li(*args, **kwargs): return tag("li", *args, **kwargs)

# --- Tags de Formulário ---
def form(*args, **kwargs): return tag("form", *args, **kwargs)
def label(*args, **kwargs): return tag("label", *args, **kwargs)
def button(*args, **kwargs): return tag("button", *args, **kwargs)
def select(*args, **kwargs): return tag("select", *args, **kwargs)
def option(*args, **kwargs): return tag("option", *args, **kwargs)
def textarea(*args, **kwargs): return tag("textarea", *args, **kwargs)

def input_(**kwargs):
    """
    Gera uma tag <input>. Tags de input não têm fechamento </input> em HTML5.
    Aceita o atributo 'name' sem conflitos agora.
    """
    props = []
    for k, v in kwargs.items():
        key = k.rstrip("_").replace("_", "-")
        props.append(f' {key}="{v}"')
    return f"<input{''.join(props)}>"

# --- Estrutura de Documento Completa ---
def doc(title, content, lang="pt-br"):
    """
    Gera a estrutura HTML5 completa de uma página (substitui o antigo html_full).
    :param title: Título da aba do navegador.
    :param content: Conteúdo HTML (body).
    """
    return (
        f'<!DOCTYPE html><html lang="{lang}">'
        f'<head>'
        f'<meta charset="UTF-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>{title}</title>'
        f'</head>'
        f'<body style="margin:0; font-family: sans-serif; background-color: #f4f4f4;">'
        f'{content}'
        f'</body></html>'
    )
