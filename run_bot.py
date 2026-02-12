# -*- coding: utf-8 -*-

import feedparser
import re
import os
import random
import subprocess
from datetime import datetime
import pytz

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


# ==========================================
# CONFIGURAÇÃO DE AGENDA BLINDADA
# ==========================================

FUSO_BRASILIA = pytz.timezone("America/Sao_Paulo")

AGENDA_POSTAGENS = {
    "09:00": "policial",
    "10:00": "economia",
    "11:00": "politica",
    "16:00": "policial",
    "17:00": "economia",
    "18:00": "politica"
}

TOLERANCIA_MINUTOS = 10


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

    hoje = datetime.now(FUSO_BRASILIA).strftime("%Y-%m-%d")

    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            data, hora = linha.strip().split("|")
            if data == hoje and hora == horario:
                return True
    return False


def registrar_postagem_diaria(horario):
    hoje = datetime.now(FUSO_BRASILIA).strftime("%Y-%m-%d")
    with open(ARQUIVO_CONTROLE_DIARIO, "a", encoding="utf-8") as f:
        f.write(f"{hoje}|{horario}\n")


# ==========================================
# CONTROLE DE ASSUNTO
# ==========================================

def extrair_assunto_principal(titulo):
    palavras = re.findall(r'\b\w{4,}\b', titulo.lower())
    stopwords = ["sobre", "para", "entre", "após", "caso", "governo", "brasil"]

    palavras = [p for p in palavras if p not in stopwords]

    if not palavras:
        return None

    return " ".join(palavras[:2])


def assunto_ja_usado(assunto):
    if not assunto:
        return False

    if not os.path.exists(ARQUIVO_CONTROLE_ASSUNTOS):
        return False

    hoje = datetime.now(FUSO_BRASILIA).strftime("%Y-%m-%d")

    with open(ARQUIVO_CONTROLE_ASSUNTOS, "r", encoding="utf-8") as f:
        for linha in f:
            data, assunto_salvo = linha.strip().split("|", 1)
            if data == hoje and assunto in assunto_salvo:
                return True
    return False


def registrar_assunto(assunto):
    if not assunto:
        return
    hoje = datetime.now(FUSO_BRASILIA).strftime("%Y-%m-%d")
    with open(ARQUIVO_CONTROLE_ASSUNTOS, "a", encoding="utf-8") as f:
        f.write(f"{hoje}|{assunto}\n")


# ==========================================
# GERAR TAGS (LIMITE TOTAL 200 CARACTERES)
# ==========================================

def gerar_tags_seo(titulo, texto):

    stopwords = [
        "com", "para", "sobre", "entre", "após",
        "caso", "contra", "diz", "afirma",
        "governo", "brasil"
    ]

    conteudo = f"{titulo} {texto[:200]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())

    tags = []

    for p in palavras:
        if p not in stopwords:
            tag = p.capitalize()
            tag = re.sub(r'[^a-zA-ZÀ-ÿ0-9 ]', '', tag)

            if tag and tag not in tags and len(tag) <= 30:
                tags.append(tag)

    tags_fixas = ["Noticias", "Diario De Noticias", "Marco Daher"]

    for tf in tags_fixas:
        if tf not in tags:
            tags.append(tf)

    resultado = []
    total = 0

    for tag in tags:
        adicional = len(tag) + (2 if resultado else 0)

        if total + adicional <= 200:
            resultado.append(tag)
            total += adicional
        else:
            break

    return resultado


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

            assunto = extrair_assunto_principal(titulo)
            if assunto_ja_usado(assunto):
                conti
