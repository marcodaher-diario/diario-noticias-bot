# =========================================================
# BOT BLOGGER – VERSÃO FINAL CORRIGIDA E ROBUSTA
# =========================================================
# ✔ HTML seguro
# ✔ Proteção contra erro 400
# ✔ Remoção de emojis inválidos
# ✔ Vídeo YouTube com fallback
# ✔ Não quebra formatação do tema
# =========================================================

import feedparser
import re
import os
import time
import random
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# =============================
# CONFIGURAÇÕES
# =============================
BLOG_ID = "7605688984374445860"
SCOPES = ["https://www.googleapis.com/auth/blogger"]
TOKEN_FILE = "token.json"
ARQUIVO_LOG = "posts_publicados.txt"

RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/",
    "https://feeds.uol.com.br/home.xml",
    "https://rss.uol.com.br/feed/noticias.xml",
    "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.cnnbrasil.com.br/feed/",
]

IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"

PALAVRAS_POLITICA = ["política", "governo", "presidente", "congresso", "stf", "lula", "bolsonaro"]
PALAVRAS_ECONOMIA = ["economia", "inflação", "dólar", "selic", "mercado"]

# =============================
# AUTENTICAÇÃO
# =============================

def autenticar():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# UTILIDADES CRÍTICAS
# =============================

def limpar_titulo(titulo):
    return re.sub(r"[^\w\sÀ-ÿ:.,-]", "", titulo)


def limpar_html_seguro(html):
    if not html:
        return "<p>Conteúdo indisponível.</p>"

    html = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", html)
    return html


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
    if "media_content" in entry:
        return entry.media_content[0].get("url")
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0].get("url")
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    if match:
        return match.group(1)
    return IMAGEM_FALLBACK


def extrair_video_id(link):
    if "youtube.com/watch" in link:
        return link.split("watch?v=")[1].split("&")[0]
    if "youtu.be/" in link:
        return link.split("youtu.be/")[1]
    return None


def gerar_video_embed(video_id):
    if not video_id:
        return None

    return f"""
    <div style=\"position:relative;padding-bottom:56.25%;height:0;overflow:hidden;margin:20px 0;\">
        <iframe src=\"https://www.youtube.com/embed/{video_id}\"
            style=\"position:absolute;top:0;left:0;width:100%;height:100%;border:0;\"
            allowfullscreen loading=\"lazy\"></iframe>
    </div>
    """

# =============================
# TEXTO
# =============================

def quebrar_paragrafos(texto):
    frases = re.split(r'(?<=[.!?]) +', texto)
    blocos = []
    atual = []
    for f in frases:
        atual.append(f)
        if len(atual) >= 2:
            blocos.append(" ".join(atual))
            atual = []
    if atual:
        blocos.append(" ".join(atual))
    return "".join(f"<p>{b}</p>" for b in blocos)

# =============================
# CLASSIFICAÇÃO
# =============================

def verificar_assunto(titulo, texto):
    c = f"{titulo} {texto}".lower()
    if any(p in c for p in PALAVRAS_POLITICA): return "politica"
    if any(p in c for p in PALAVRAS_ECONOMIA): return "economia"
    return "geral"

# =============================
# CONTEÚDO FINAL
# =============================

def gerar_conteudo(n):
    texto = re.sub(r"<[^>]+>", "", n["texto"])
    texto = quebrar_paragrafos(texto)

    video_id = extrair_video_id(n["link"])
    video_html = gerar_video_embed(video_id)

    if video_html:
        media = video_html
    else:
        media = f"""
        <div style=\"text-align:center;margin:20px 0;\">
            <a href=\"{n['link']}\" target=\"_blank\">
                <img src=\"{n['imagem']}\" style=\"max-width:100%;height:auto;\">
                <p><strong>▶ Assistir na fonte</strong></p>
            </a>
        </div>
        """

    html = f"""
    <div>
        <h2 style=\"text-align:center;\">{n['titulo']}</h2>
        {media}
        <p><strong>Fonte:</strong> {n['fonte']}</p>
        <div style=\"text-align:justify;font-size:16px;line-height:1.6;\">
            {texto}
        </div>
        <p style=\"text-align:center;\">
            <a href=\"{n['link']}\" target=\"_blank\">🔗 Leia a matéria original</a>
        </p>
    </div>
    """

    return limpar_html_seguro(html)

# =============================
# BUSCA DE NOTÍCIAS
# =============================

def noticia_recente(entry, horas=48):
    data = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not data:
        return False
    data_noticia = datetime.fromtimestamp(time.mktime(data))
    return data_noticia >= datetime.now() - timedelta(hours=horas)


def buscar_noticias(tipo, limite=6):
    noticias = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")
        for entry in feed.entries:
            if not noticia_recente(entry): continue
            titulo = entry.get("title", "")
            link = entry.get("link", "")
            texto = entry.get("summary", "")
            if not titulo or not link: continue
            if ja_publicado(link): continue
            if verificar_assunto(titulo, texto) != tipo: continue

            noticias.append({
                "titulo": limpar_titulo(titulo),
                "texto": texto,
                "link": link,
                "fonte": fonte,
                "imagem": extrair_imagem(entry)
            })

    random.shuffle(noticias)
    return noticias[:limite]

# =============================
# EXECUÇÃO
# =============================

def executar():
    service = autenticar()
    hora = datetime.now().hour
    tipo = "politica" if hora < 12 else "geral" if hora < 18 else "economia"

    noticias = buscar_noticias(tipo)

    for n in noticias:
        try:
            conteudo = gerar_conteudo(n)
            if len(re.sub(r"<[^>]+>", "", conteudo).strip()) < 120:
                continue

            service.posts().insert(
                blogId=BLOG_ID,
                body={"title": n["titulo"], "content": conteudo, "status": "LIVE"}
            ).execute()

            registrar_publicacao(n["link"])
            print(f"✅ Publicado: {n['titulo']}")
            time.sleep(10)

        except HttpError as e:
            print("⛔ Erro Blogger, pulando item")


if __name__ == "__main__":
    executar()
