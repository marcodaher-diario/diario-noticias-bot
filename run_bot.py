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
# =============================

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG):
        return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# =============================
# EXTRAÇÃO DE MÍDIA
# =============================

def extrair_imagem(entry):
    if hasattr(entry, "media_content"):
        return entry.media_content[0].get("url")
    if hasattr(entry, "media_thumbnail"):
        return entry.media_thumbnail[0].get("url")
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    return match.group(1) if match else IMAGEM_FALLBACK

# =============================
# VALIDAÇÃO DE CONTEÚDO
# =============================

def conteudo_insuficiente(texto):
    texto = re.sub(r"<[^>]+>", "", texto).strip()
    if len(texto) < 120:
        return True
    bloqueio = ["assista","veja","vídeo","clique","confira"]
    return any(p in texto.lower() for p in bloqueio)

# =============================
# BUSCA ALTERNATIVA
# =============================

def buscar_conteudo_alternativo(titulo_base):
    base = titulo_base.lower()[:50]
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")
        for entry in feed.entries:
            titulo = entry.get("title", "")
            texto = entry.get("summary", "")
            if not titulo or not texto:
                continue
            if base in titulo.lower():
                imagem = extrair_imagem(entry)
                if imagem and not conteudo_insuficiente(texto):
                    return {
                        "titulo": titulo,
                        "texto": texto,
                        "link": entry.get("link", ""),
                        "fonte": fonte,
                        "imagem": imagem
                    }
    return None

# =============================
# FORMATAÇÃO
# =============================

def quebrar_paragrafos(texto):
    frases = re.split(r'(?<=[.!?])\s+', texto)

    blocos = []
    temp = []

    for frase in frases:
        temp.append(frase)

        if len(temp) >= 2:
            blocos.append(" ".join(temp))
            temp = []

    if temp:
        blocos.append(" ".join(temp))

    return "".join(f"<p>{b}</p>" for b in blocos)


# =============================
# CLASSIFICAÇÃO
# =============================

def verificar_assunto(titulo, texto):
    base = f"{titulo} {texto}".lower()
    if any(p in base for p in PALAVRAS_POLITICA): return "politica"
    if any(p in base for p in PALAVRAS_ECONOMIA): return "economia"
    return "geral"

# =============================
# BUSCA PRINCIPAL
# =============================

def noticia_recente(entry, horas=48):
    data = entry.get("published_parsed") or entry.get("updated_parsed")
    if not data:
        return False
    return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)


def buscar_noticias(tipo, limite=5):
    noticias = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")
        for entry in feed.entries:
            if not noticia_recente(entry): continue
            titulo = entry.get("title", "")
            texto = entry.get("summary", "")
            link = entry.get("link", "")
            if not titulo or not link or ja_publicado(link): continue
            if verificar_assunto(titulo, texto) != tipo: continue
            if conteudo_insuficiente(texto):
                alternativa = buscar_conteudo_alternativo(titulo)
                if not alternativa:
                    print(f"⛔ BLOQUEADO (conteúdo pobre): {titulo}")
                    continue
                noticias.append(alternativa)
            else:
                noticias.append({
                    "titulo": titulo,
                    "texto": texto,
                    "link": link,
                    "fonte": fonte,
                    "imagem": extrair_imagem(entry)
                })
    random.shuffle(noticias)
    return noticias[:limite]

# =============================
# GERAÇÃO HTML
# =============================

def gerar_conteudo(n):
    texto = quebrar_paragrafos(re.sub(r"<[^>]+>", "", n["texto"]))
    return f"""
    <h2 style=\"text-align:center;\">{n['titulo']}</h2>
    <div style=\"text-align:center; margin:20px 0;\">
        <img src=\"{n['imagem']}\" alt=\"{n['titulo']}\">
    </div>
    <p><b>Fonte:</b> {n['fonte']}</p>
    {texto}
    <p style=\"text-align:center;\"><a href=\"{n['link']}\" target=\"_blank\">Leia a matéria original</a></p>
    """

# =============================
# EXECUÇÃO
# =============================

def executar():
    service = autenticar_blogger()
    hora = datetime.now().hour
    tipo = "politica" if hora < 12 else "geral" if hora < 18 else "economia"
    noticias = buscar_noticias(tipo)
    for n in noticias:
        try:
            service.posts().insert(
                blogId=BLOG_ID,
                body={"title": n['titulo'], "content": gerar_conteudo(n), "status": "LIVE"}
            ).execute()
            registrar_publicacao(n['link'])
            print(f"✅ Publicado: {n['titulo']}")
        except Exception as e:
            print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
