
from .core import MyFramework
from .responses import Response, HTMLResponse, JSONResponse, RedirectResponse
from .logger import Logger
from .database import Database, Model
from .requests import Request
from .server import BuiltInServer # Adicionado o servidor traduzido

from . import html

__version__ = "1.0.0" # Parabéns pela versão 1.0!
