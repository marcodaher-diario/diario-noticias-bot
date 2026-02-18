# -*- coding: utf-8 -*-

import os
import re
import feedparser
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
from imagem_engine import ImageEngine


AGENDA_POSTAGENS = {
    "13:40": "policial",
    "14:05": "economia",
    "14:10": "politica"
}


def autenticar_blogger():
    creds = Credentials.from_authorized_user_file("token.json")
    return build("blogger", "v3", credentials=creds)


def obter_horario_brasilia():
    agora = datetime.utcnow() - timedelta(hours=3)
    return agora.strftime("%H:%M")


def verificar_assunto(titulo, texto):
    conteudo = f"{titulo} {texto}".lower()

    if any(p in conteudo for p in PALAVRAS_POLICIAL):
        return "policial"
    if any(p in conteudo for p in PALAVRAS_POLITICA):
        return "politica"
    if any(p in conteudo for p in PALAVRAS_ECONOMIA):
        return "economia"

    return "geral"


def buscar_noticia(tipo):

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            titulo = entry.get("title", "")
            resumo = entry.get("summary", "")
            link = entry.get("link", "")
            imagem = entry.get("media_content", [{}])[0].get("url", "")

            if not titulo or not link:
                continue

            if verificar_assunto(titulo, resumo) != tipo:
                continue

            return {
                "titulo": titulo,
                "texto": resumo,
                "link": link,
                "imagem": imagem
            }

    return None


def separar_blocos(texto):

    secoes = {
        "contexto": "",
        "desdobramentos": "",
        "impactos": "",
        "conclusao": ""
    }

    atual = None

    for linha in texto.split("\n"):
        l = linha.strip()

        if l.lower().startswith("contexto"):
            atual = "contexto"
            continue
        if l.lower().startswith("desdobramentos"):
            atual = "desdobramentos"
            continue
        if l.lower().startswith("impactos"):
            atual = "impactos"
            continue
        if l.lower().startswith("considerações finais"):
            atual = "conclusao"
            continue

        if atual:
            secoes[atual] += l + "\n"

    for chave in secoes:
        if not secoes[chave].strip():
            secoes[chave] = "Não há informações adicionais disponíveis neste momento."

    return secoes


def publicar_post(service, titulo, html):

    post = {
        "title": titulo,
        "content": html
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post,
        isDraft=False
    ).execute()


if __name__ == "__main__":

    horario = obter_horario_brasilia()

    if horario not in AGENDA_POSTAGENS:
        exit()

    tema = AGENDA_POSTAGENS[horario]

    noticia = buscar_noticia(tema)

    if not noticia:
        exit()

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    texto_ia = gemini.gerar_analise_jornalistica(
        noticia["titulo"],
        noticia["texto"]
    )

    blocos = separar_blocos(texto_ia)

    imagem_final = imagem_engine.obter_imagem(noticia, tema)

    dados = {
        "titulo": noticia["titulo"],
        "imagem": imagem_final,
        "contexto": blocos["contexto"],
        "desdobramentos": blocos["desdobramentos"],
        "impactos": blocos["impactos"],
        "conclusao": blocos["conclusao"],
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    service = autenticar_blogger()

    publicar_post(service, noticia["titulo"], html)

    print("Post publicado com sucesso.")
