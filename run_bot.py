# =========================================================
# RUN_BOT.PY — ARQUIVO FINAL CONSOLIDADO (Blogger Safe Edition)
# Curadoria ativa, bloqueio de conteúdo pobre, reaproveitamento
# =========================================================

import feedparser
import re
import os
import time
import random
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =============================
# CONFIGURAÇÕES
# =============================
BLOG_ID = "7605688984374445860"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/",
    "https://feeds.uol.com.br/home.xml",
    "https://rss.uol.com.br/feed/noticias.xml",
    "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://agenciabrasil.ebc.com.br/rss",
    "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.gazetadopovo.com.br/feed/rss/brasil.xml",
    "https://www.cnnbrasil.com.br/feed/",
    "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
]

IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

PALAVRAS_POLITICA = ["política","governo","presidente","lula","bolsonaro","congresso","stf"]
PALAVRAS_ECONOMIA = ["economia","inflação","selic","dólar","mercado","banco central"]

# =============================
# AUTENTICAÇÃO
# =============================

def autenticar_blogger():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("token.json não encontrado")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# UTILITÁRIOS
#
