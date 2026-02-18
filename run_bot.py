# -*- coding: utf-8 -*-

import feedparser
import re
import os
import random
import subprocess

from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from configuracoes import (
    BLOG_ID,
    RSS_FEEDS,
    PALAVRAS_POLICIAL,
    PALAVRAS_POLITICA,
    PALAVRAS_ECONOMIA,
    BLOCO_FIXO_FINAL
)

from template_blog import obter_esqueleto_html
from gemini_engine import GeminiEngine


# ==========================================
# CONFIGURAÇÃO DE AGENDA FIXA
# ==========================================

AGENDA_POSTAGENS = {
    "08:45": "policial",
    "10:00": "economia",
    "11:00": "politica",
    "16:00": "policial",
    "17:00": "economia",
    "18:00": "politica"
}


# ==========================================
# ARQUIVOS DE CONTROLE
# ==========================================

ARQUIVO_LOG = "posts_publicados.txt"
ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"
ARQUIVO_CONTROLE_ASSUNTOS = "controle_assuntos.txt"


# ==========================================
# AUTENTICAÇÃO BLOGGER
# ==========================================

def autenticar_blogger():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("token.json não encontrado.")
    creds = Credentials.from_authorized_user_file("token.json")
    return build("blogger", "v3", credentials=creds)


# ==========================================
# CONTROLE DE PUBLICAÇÃO
# ==========================================

def obter_horario_brasilia():
    agora_utc = datetime.utcnow()
    agora_brasilia = agora_utc - timedelta(hours=3)
    return agora_brasilia.strftime("%H:%M"), agora_brasilia.strftime("%Y-%m-%d")


def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG):
        return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()


def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")


def ja_postou_neste_horario(horario):
    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False

    _, hoje = obter_horario_brasilia()

    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            data, hora = linha.strip().split("|")
            if data == hoje and hora == horario:
                return True
    return False


def registrar_postagem_diaria(horario):
    _, hoje = obter_horario_brasilia()
    with open(ARQUIVO_CONTROLE_DIARIO, "a", encoding="utf-8") as f:
        f.write(f"{hoje}|{horario}\n")


# ==========================================
# VERIFICAR TEMA
# ==========================================

def verificar_assunto(titulo, texto):
    conteudo = f"{titulo} {texto}".lower()

    if any(p in conteudo for p in PALAVRAS_POLICIAL):
        return "policial"

    if any(p in conteudo for p in PALAVRAS_POLITICA):
        return "politica"

    if any(p in conteudo for p in PALAVRAS_ECONOMIA):
        return "economia"

    return "geral"


# ==========================================
# BUSCAR NOTÍCIAS
# ==========================================

def buscar_noticias(tipo_alvo, limite=1):

    noticias = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")

        for entry in feed.entries:

            titulo = entry.get("title", "")
            texto = entry.get("summary", "")
            link = entry.get("link", "")

            if not titulo or not link:
                continue

            if ja_publicado(link):
                continue

            tipo_detectado = verificar_assunto(titulo, texto)
            if tipo_detectado != tipo_alvo:
                continue

            noticias.append({
                "titulo": titulo,
                "texto": texto,
                "link": link,
                "fonte": fonte
            })

    random.shuffle(noticias)

    return noticias[:limite]


# ==========================================
# GERAR CONTEÚDO HTML COM IA
# ==========================================

def gerar_conteudo(n, tema):

    gemini = GeminiEngine()

    texto_original = re.sub(r"<[^>]+>", "", n["texto"])[:4000]

    analise = gemini.gerar_analise_jornalistica(
        titulo=n["titulo"],
        conteudo_original=texto_original,
        categoria=tema
    )

    dados = {
        "titulo": n["titulo"],
        "img_topo": "",
        "intro": analise[:800],
        "sub1": "Contexto",
        "texto1": analise,
        "img_meio": "",
        "sub2": "",
        "texto2": "",
        "sub3": "",
        "texto3": "",
        "texto_conclusao": "",
        "assinatura": BLOCO_FIXO_FINAL
    }

    html_final = obter_esqueleto_html(dados)

    return html_final


# ==========================================
# PUBLICAR POST
# ==========================================

def publicar_post(service, noticia, tema):

    conteudo_html = gerar_conteudo(noticia, tema)

    post = {
        "title": str(noticia["titulo"])[:150],
        "content": conteudo_html
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post,
        isDraft=False
    ).execute()

    registrar_publicacao(noticia["link"])


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":

    try:

        horario_atual, _ = obter_horario_brasilia()

        if horario_atual not in AGENDA_POSTAGENS:
            exit()

        tema = AGENDA_POSTAGENS[horario_atual]

        if ja_postou_neste_horario(horario_atual):
            exit()

        service = autenticar_blogger()

        noticias = buscar_noticias(tema, limite=1)

        if not noticias:
            exit()

        publicar_post(service, noticias[0], tema)

        registrar_postagem_diaria(horario_atual)

    except Exception as erro:
        print("Erro:", erro)
