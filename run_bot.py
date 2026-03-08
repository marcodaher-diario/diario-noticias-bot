# -*- coding: utf-8 -*-

import os
import re
import feedparser
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
import unicodedata

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

from configuracoes import (
    BLOG_ID,
    RSS_FEEDS,
    PESOS_POR_TEMA,
    BLOCO_FIXO_FINAL
)

from template_blog import obter_esqueleto_html
from gemini_engine import GeminiEngine
from imagem_engine import ImageEngine


# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

AGENDA_POSTAGENS = {
    "09:00": "policial",
    "13:00": "economia",
    "19:00": "politica"
}

JANELA_MINUTOS = 60
ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"
ARQUIVO_POSTS_PUBLICADOS = "posts_publicados.txt"


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
# CONTROLE DE PUBLICAÇÃO (COM RODÍZIO DE 15 LINHAS)
# ==========================================================

def ja_postou(data_str, horario_agenda):
    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False
    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or "|" not in linha:
                continue
            partes = linha.split("|")
            if len(partes) == 2:
                data, hora = partes
                if data == data_str and hora == horario_agenda:
                    return True
    return False


def registrar_postagem(data_str, horario_agenda):
    linhas = []
    if os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
            linhas = f.readlines()

    nova_linha = f"{data_str}|{horario_agenda}\n"

    if nova_linha not in linhas:
        linhas.append(nova_linha)

    linhas = linhas[-15:]

    with open(ARQUIVO_CONTROLE_DIARIO, "w", encoding="utf-8") as f:
        f.writelines(linhas)


# ==========================================================
# CONTROLE DE LINKS (COM RODÍZIO DE 100 LINHAS)
# ==========================================================

def registrar_link_publicado(link):
    linhas = []
    if os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        with open(ARQUIVO_POSTS_PUBLICADOS, "r", encoding="utf-8") as f:
            linhas = f.readlines()

    nova_linha = f"{link}\n"

    if nova_linha not in linhas:
        linhas.append(nova_linha)

    linhas = linhas[-100:]

    with open(ARQUIVO_POSTS_PUBLICADOS, "w", encoding="utf-8") as f:
        f.writelines(linhas)


def link_ja_publicado(link):
    if not os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        return False
    with open(ARQUIVO_POSTS_PUBLICADOS, "r", encoding="utf-8") as f:
        return any(link.strip() == l.strip() for l in f)


# ==========================================================
# PROTEÇÃO EXTRA CONTRA REPETIÇÃO
# ==========================================================

def gerar_id_noticia(titulo):
    texto = titulo.lower()
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    palavras = texto.split()
    return "-".join(palavras[:8])


# ==========================================================
# CONTROLE DE IMAGENS
# ==========================================================

def registrar_imagem_usada(url_imagem):
    ARQUIVO_IMAGENS = "imagens_usadas.txt"

    linhas = []

    if os.path.exists(ARQUIVO_IMAGENS):
        with open(ARQUIVO_IMAGENS, "r", encoding="utf-8") as f:
            linhas = f.readlines()

    nova_linha = f"{url_imagem}\n"

    if nova_linha not in linhas:
        linhas.append(nova_linha)

    linhas = linhas[-50:]

    with open(ARQUIVO_IMAGENS, "w", encoding="utf-8") as f:
        f.writelines(linhas)


# ==========================================================
# VERIFICAR TEMA
# ==========================================================

def verificar_assunto(titulo, texto):

    conteudo = remover_acentos(f"{titulo} {texto}".lower())

    melhor_tema = "geral"
    maior_score = 0

    for tema, palavras_chave in PESOS_POR_TEMA.items():

        score_atual = 0

        for palavra, peso in palavras_chave.items():

            palavra_norm = remover_acentos(palavra.lower())

            ocorrencias = conteudo.count(palavra_norm)

            if ocorrencias > 0:
                score_atual += peso * ocorrencias

        if score_atual > maior_score:
            maior_score = score_atual
            melhor_tema = tema

    # mínimo para considerar tema específico
    if maior_score >= 8:
        return melhor_tema

    return "geral"


# ==========================================================
# GERAR TAGS SEO
# ==========================================================

def gerar_tags_seo(titulo, texto):

    stopwords = ["com","de","do","da","em","para","um","uma","os","as","que","no","na","ao","aos"]

    conteudo = f"{titulo} {texto[:100]}"

    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())

    tags = []

    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())

    tags_fixas = ["Notícias","Diário de Notícias","Marco Daher"]

    for tf in tags_fixas:
        if tf not in tags:
            tags.append(tf)

    resultado = []

    tamanho_atual = 0

    for tag in tags:
        if tamanho_atual + len(tag) + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += len(tag) + 2
        else:
            break

    return resultado


# ==========================================================
# BUSCAR NOTÍCIA (BUSCA PROGRESSIVA ATÉ 48H)
# ==========================================================

def buscar_noticia(tipo):

    palavras_peso = PESOS_POR_TEMA.get(tipo, {})

    agora = datetime.utcnow()

    janelas_busca = [6,12,24,36,48]

    for limite_horas in janelas_busca:

        noticias_validas = []

        for feed_url in RSS_FEEDS:

            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:

                titulo = entry.get("title","")
                resumo = entry.get("summary","")
                link = entry.get("link","")

                imagem = ""

                if "media_content" in entry and len(entry.media_content) > 0:
                    imagem = entry.media_content[0].get("url","")

                if not titulo or not link:
                    continue

                if verificar_assunto(titulo,resumo) != tipo:
                    continue

                id_noticia = gerar_id_noticia(titulo)

                if link_ja_publicado(link):
                    continue

                if link_ja_publicado(id_noticia):
                    continue

                data_publicacao = None

                if hasattr(entry,"published"):
                    try:
                        data_publicacao = parsedate_to_datetime(entry.published)

                        if data_publicacao.tzinfo is not None:
                            data_publicacao = data_publicacao.astimezone(tz=None).replace(tzinfo=None)

                    except:
                        pass

                if data_publicacao:

                    horas_passadas = (agora - data_publicacao).total_seconds() / 3600

                    if horas_passadas > limite_horas:
                        continue

                conteudo = remover_acentos(f"{titulo} {resumo}".lower())

                score = 0

                for palavra,peso in palavras_peso.items():

                    palavra_norm = remover_acentos(palavra.lower())
                
                    if palavra_norm in conteudo:
                        score += peso

                if data_publicacao:

                    minutos_passados = (agora - data_publicacao).total_seconds() / 60

                    bonus_recencia = max(0,1200-minutos_passados)/1200

                    score += bonus_recencia * 8

                dominio = ""

                try:
                    dominio = link.split("/")[2]
                except:
                    pass

                fontes_bonus = {
                    "g1.globo.com":4,
                    "uol.com.br":3,
                    "folha.uol.com.br":4,
                    "bbc.co.uk":5,
                    "cnnbrasil.com.br":3,
                    "estadao.com.br":4
                }

                for fonte,bonus in fontes_bonus.items():

                    if fonte in dominio:
                        score += bonus

                noticias_validas.append({
                    "titulo":titulo,
                    "texto":resumo,
                    "link":link,
                    "imagem":imagem,
                    "score":score
                })

        if noticias_validas:

            noticia_escolhida = max(noticias_validas,key=lambda x:x["score"])

            return noticia_escolhida

    return None
