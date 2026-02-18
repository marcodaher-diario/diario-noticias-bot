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
    "14:05": "policial",
    "10:00": "economia",
    "11:00": "politica",
    "16:00": "policial",
    "17:00": "economia",
    "18:00": "politica"
}

JANELA_MINUTOS = 10  # tolerância de ±10 minutos


# ==========================================
# ARQUIVOS DE CONTROLE
# ==========================================

ARQUIVO_LOG = "posts_publicados.txt"
ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"


# ==========================================
# AUTENTICAÇÃO BLOGGER
# ==========================================

def autenticar_blogger():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("token.json não encontrado.")
    creds = Credentials.from_authorized_user_file("token.json")
    return build("blogger", "v3", credentials=creds)


# ==========================================
# CONTROLE DE TEMPO
# ==========================================

def obter_horario_brasilia():
    agora_utc = datetime.utcnow()
    agora_brasilia = agora_utc - timedelta(hours=3)
    return agora_brasilia


def horario_para_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def dentro_da_janela(horario_atual_min, horario_agenda_min):
    return abs(horario_atual_min - horario_agenda_min) <= JANELA_MINUTOS


def ja_postou_neste_horario(data_str, horario_agenda):
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

        for entry in feed.entries:

            titulo = entry.get("title", "")
            texto = entry.get("summary", "")
            link = entry.get("link", "")

            if not titulo or not link:
                continue

            tipo_detectado = verificar_assunto(titulo, texto)
            if tipo_detectado != tipo_alvo:
                continue

            noticias.append({
                "titulo": titulo,
                "texto": texto,
                "link": link
            })

    random.shuffle(noticias)
    return noticias[:limite]


# ==========================================
# GERAR CONTEÚDO COM IA
# ==========================================

def gerar_conteudo(noticia, tema):

    gemini = GeminiEngine()

    texto_original = re.sub(r"<[^>]+>", "", noticia["texto"])[:4000]

    analise = gemini.gerar_analise_jornalistica(
        titulo=noticia["titulo"],
        conteudo_original=texto_original,
        categoria=tema
    )

    dados = {
        "titulo": noticia["titulo"],
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

    return obter_esqueleto_html(dados)


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":

    try:

        agora = obter_horario_brasilia()
        horario_atual_min = agora.hour * 60 + agora.minute
        data_hoje = agora.strftime("%Y-%m-%d")

        horario_escolhido = None
        tema_escolhido = None

        for horario_agenda, tema in AGENDA_POSTAGENS.items():

            horario_agenda_min = horario_para_minutos(horario_agenda)

            if dentro_da_janela(horario_atual_min, horario_agenda_min):

                if not ja_postou_neste_horario(data_hoje, horario_agenda):
                    horario_escolhido = horario_agenda
                    tema_escolhido = tema
                    break

        if not horario_escolhido:
            exit()

        service = autenticar_blogger()

        noticias = buscar_noticias(tema_escolhido, limite=1)

        if not noticias:
            exit()

        conteudo_html = gerar_conteudo(noticias[0], tema_escolhido)

        post = {
            "title": noticias[0]["titulo"][:150],
            "content": conteudo_html
        }

        service.posts().insert(
            blogId=BLOG_ID,
            body=post,
            isDraft=False
        ).execute()

        registrar_postagem(data_hoje, horario_escolhido)

    except Exception as erro:
        print("Erro:", erro)
