# =========================================================
# RUN_BOT.PY — VERSÃO FINAL ESTÁVEL (Blogger Safe Edition)
# =========================================================
# ✔ Layout preservado
# ✔ Texto JUSTIFICADO
# ✔ Fontes intactas
# ✔ TAGs (labels) até 200 caracteres
# ✔ Bloqueio de conteúdo pobre
# ✔ Sem conflitos de CSS / layout
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

PALAVRAS_POLITICA = ["política", "governo", "presidente", "lula", "bolsonaro", "congresso", "stf"]
PALAVRAS_ECONOMIA = ["economia", "inflação", "selic", "dólar", "mercado", "banco central"]

# =============================
# AUTENTICAÇÃO
# =============================

def autenticar_blogger():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("token.json não encontrado")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# CONTROLE DE DUPLICAÇÃO
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
# EXTRAÇÃO DE IMAGEM
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
    texto_limpo = re.sub(r"<[^>]+>", "", texto).strip()
    if len(texto_limpo) < 120:
        return True

    bloqueio = ["assista", "veja", "vídeo", "clique", "confira"]
    return any(p in texto_limpo.lower() for p in bloqueio)

# =============================
# CLASSIFICAÇÃO DE ASSUNTO
# =============================

def verificar_assunto(titulo, texto):
    base = f"{titulo} {texto}".lower()
    if any(p in base for p in PALAVRAS_POLITICA):
        return "politica"
    if any(p in base for p in PALAVRAS_ECONOMIA):
        return "economia"
    return "geral"

# =============================
# LIMITADOR DE TAGS (200 chars)
# =============================

def gerar_tags_blogger(tags, limite=200):
    tags_final = []
    total = 0

    for tag in tags:
        tag = tag.strip()
        if not tag or tag.lower() in [t.lower() for t in tags_final]:
            continue

        tamanho = len(tag)
        if total + tamanho > limite:
            break

        tags_final.append(tag)
        total += tamanho

    return tags_final

def gerar_tags_noticia(titulo, texto):
    base = f"{titulo} {texto}".lower()
    tags = []

    if any(p in base for p in PALAVRAS_POLITICA):
        tags.extend(["Política", "Governo", "Brasil"])

    if any(p in base for p in PALAVRAS_ECONOMIA):
        tags.extend(["Economia", "Mercado", "Brasil"])

    tags.append("Diário de Notícias")

    palavras = re.findall(r'\b[a-záéíóúâêôãõç]{5,}\b', base)
    for p in palavras[:10]:
        tags.append(p.capitalize())

    return gerar_tags_blogger(tags, limite=200)

# =============================
# FORMATAÇÃO DE TEXTO
# =============================

def quebrar_paragrafos(texto):
    frases = re.split(r'(?<=[.!?])\s+', texto)
    blocos, temp = [], []

    for frase in frases:
        temp.append(frase)
        if len(temp) >= 2:
            blocos.append(" ".join(temp))
            temp = []

    if temp:
        blocos.append(" ".join(temp))

    return "".join(f"<p style='text-align:justify;'>{b}</p>" for b in blocos)

# =============================
# BUSCA DE NOTÍCIAS
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
            if not noticia_recente(entry):
                continue

            titulo = entry.get("title", "")
            texto = entry.get("summary", "")
            link = entry.get("link", "")

            if not titulo or not texto or not link:
                continue
            if ja_publicado(link):
                continue
            if verificar_assunto(titulo, texto) != tipo:
                continue
            if conteudo_insuficiente(texto):
                continue

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
# GERAÇÃO DE HTML FINAL
# =============================

def gerar_conteudo(n):
    texto_limpo = re.sub(r"<[^>]+>", "", n["texto"])
    corpo = quebrar_paragrafos(texto_limpo)

    return f"""
    <h2 style="text-align:center;">{n['titulo']}</h2>
    <div style="text-align:center; margin:20px 0;">
        <img src="{n['imagem']}" alt="{n['titulo']}" style="max-width:100%; height:auto;">
    </div>
    <p><b>Fonte:</b> {n['fonte']}</p>
    {corpo}
    <p style="text-align:center;">
        <a href="{n['link']}" target="_blank">Leia a matéria original</a>
    </p>
    """

# =============================
# EXECUÇÃO PRINCIPAL
# =============================

def executar():
    service = autenticar_blogger()
    hora = datetime.now().hour

    tipo = "politica" if hora < 12 else "geral" if hora < 18 else "economia"
    noticias = buscar_noticias(tipo)

    for n in noticias:
        try:
            tags = gerar_tags_noticia(n["titulo"], n["texto"])

            service.posts().insert(
                blogId=BLOG_ID,
                body={
                    "title": n["titulo"],
                    "content": gerar_conteudo(n),
                    "labels": tags,
                    "status": "LIVE"
                }
            ).execute()

            registrar_publicacao(n["link"])
            print(f"✅ Publicado: {n['titulo']}")

        except Exception as e:
            print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
