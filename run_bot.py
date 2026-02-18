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


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

AGENDA_POSTAGENS = {
    "20:34": "policial",
    "14:05": "economia",
    "14:10": "politica"
}

JANELA_MINUTOS = 10
ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"


# ==========================================================
# UTILIDADES DE TEMPO
# ==========================================================

def obter_horario_brasilia():
    return datetime.utcnow() - timedelta(hours=3)


def horario_para_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def dentro_da_janela(min_atual, min_agenda):
    return abs(min_atual - min_agenda) <= JANELA_MINUTOS


# ==========================================================
# CONTROLE DE PUBLICAÇÃO
# ==========================================================

def ja_postou(data_str, horario_agenda):
    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False

    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            data, hora = linha.strip().split("|")
            if data == data_str and hora == horario_agenda:
                return True
    return False


def registrar_postagem(data_str, horario_agenda):
    with open(ARQUIVO_CONTROLE_DIARIO, "a", encoding="utf-8") as f:
        f.write(f"{data_str}|{horario_agenda}\n")


# ==========================================================
# AUTENTICAÇÃO BLOGGER
# ==========================================================

def autenticar_blogger():
    creds = Credentials.from_authorized_user_file("token.json")
    return build("blogger", "v3", credentials=creds)


# ==========================================================
# VERIFICAR TEMA
# ==========================================================

def verificar_assunto(titulo, texto):
    conteudo = f"{titulo} {texto}".lower()

    if any(p in conteudo for p in PALAVRAS_POLICIAL):
        return "policial"
    if any(p in conteudo for p in PALAVRAS_POLITICA):
        return "politica"
    if any(p in conteudo for p in PALAVRAS_ECONOMIA):
        return "economia"

    return "geral"


# ==========================================================
# BUSCAR NOTÍCIA
# ==========================================================

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


# ==========================================================
# SEPARAR BLOCOS DO GEMINI
# ==========================================================

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


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    agora = obter_horario_brasilia()
    min_atual = agora.hour * 60 + agora.minute
    data_hoje = agora.strftime("%Y-%m-%d")

    horario_escolhido = None
    tema_escolhido = None

    for horario_agenda, tema in AGENDA_POSTAGENS.items():

        min_agenda = horario_para_minutos(horario_agenda)

        if dentro_da_janela(min_atual, min_agenda):
            if not ja_postou(data_hoje, horario_agenda):
                horario_escolhido = horario_agenda
                tema_escolhido = tema
                break

    if not horario_escolhido:
        exit()

    noticia = buscar_noticia(tema_escolhido)

    if not noticia:
        exit()

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    texto_ia = gemini.gerar_analise_jornalistica(
    noticia["titulo"],
    noticia["texto"],
    tema_escolhido
)

    blocos = separar_blocos(texto_ia)

    imagem_final = imagem_engine.obter_imagem(noticia, tema_escolhido)

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

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": noticia["titulo"], "content": html},
        isDraft=False
    ).execute()

    registrar_postagem(data_hoje, horario_escolhido)

    print("Post publicado com sucesso.")
