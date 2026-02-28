# -*- coding: utf-8 -*-

import os
import re
import feedparser
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime

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
# CONTROLE DE PUBLICAÇÃO
# ==========================================================

def ja_postou(data_str, horario_agenda):
    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False

    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or "|" not in linha: continue # Pula linhas vazias
            partes = linha.split("|")
            if len(partes) == 2:
                data, hora = partes
                if data == data_str and hora == horario_agenda:
                    return True
    return False


def registrar_postagem(data_str, horario_agenda):
    with open(ARQUIVO_CONTROLE_DIARIO, "a", encoding="utf-8") as f:
        f.write(f"{data_str}|{horario_agenda}\n")


# ==========================================================
# CONTROLE DE LINK JÁ PUBLICADO
# ==========================================================

def link_ja_publicado(link):
    if not os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        return False

    with open(ARQUIVO_POSTS_PUBLICADOS, "r", encoding="utf-8") as f:
        for linha in f:
            if linha.strip() == link:
                return True
    return False


def registrar_link_publicado(link):
    with open(ARQUIVO_POSTS_PUBLICADOS, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")


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
# GERAR TAGS SEO
# ==========================================================

def gerar_tags_seo(titulo, texto):
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos"]
    conteudo = f"{titulo} {texto[:100]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())

    tags_fixas = ["Notícias", "Diário de Notícias", "Marco Daher"]
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
# BUSCAR NOTÍCIA COM RANKING EDITORIAL
# ==========================================================

def buscar_noticia(tipo):

    pesos_por_tema = {
        "policial": {"homicídio": 12, "prisão": 10, "operação": 9, "flagrante": 9, "crime": 8, "suspeito": 7},
        "politica": {"stf": 12, "supremo": 12, "congresso": 10, "senado": 9, "cpi": 9, "presidente": 8},
        "economia": {"inflação": 12, "dólar": 10, "pib": 9, "selic": 9, "juros": 8, "mercado": 7}
    }

    palavras_peso = pesos_por_tema.get(tipo, {})
    noticias_validas = []
    agora = datetime.utcnow()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:15]:
            titulo = entry.get("title", "")
            resumo = entry.get("summary", "")
            link = entry.get("link", "")
            imagem = entry.get("media_content", [{}])[0].get("url", "") # Corrigido aqui

            if not titulo or not link:
                continue

            if verificar_assunto(titulo, resumo) != tipo:
                continue

            if link_ja_publicado(link):
                continue

            data_publicacao = None
            if hasattr(entry, "published"):
                try:
                    data_publicacao = parsedate_to_datetime(entry.published)
                    if data_publicacao.tzinfo is not None:
                        data_publicacao = data_publicacao.astimezone(tz=None).replace(tzinfo=None)
                except: pass

            if data_publicacao:
                if (agora - data_publicacao).days > 1:
                    continue

            conteudo = f"{titulo} {resumo}".lower()
            score = 0
            for palavra, peso in palavras_peso.items():
                if palavra in conteudo:
                    score += peso

            if data_publicacao:
                minutos_passados = (agora - data_publicacao).total_seconds() / 60
                bonus_recencia = max(0, 1000 - minutos_passados) / 1000
                score += bonus_recencia

            noticias_validas.append({
                "titulo": titulo,
                "texto": resumo,
                "link": link,
                "imagem": imagem, # Corrigido aqui
                "score": score
            })

    if not noticias_validas:
        return None

    noticia_escolhida = max(noticias_validas, key=lambda x: x["score"])

    return {
        "titulo": noticia_escolhida["titulo"],
        "texto": noticia_escolhida["texto"],
        "link": noticia_escolhida["link"],
        "imagem": noticia_escolhida["imagem"] # Corrigido aqui
    }


# ==========================================================
# MODO TESTE
# ==========================================================

def executar_modo_teste(tema_forcado=None, publicar=False):

    print("=== MODO TESTE ATIVADO ===")

    if not tema_forcado:
        tema_forcado = "policial"

    noticia = buscar_noticia(tema_forcado)

    if not noticia:
        print("Nenhuma notícia encontrada para teste.")
        return

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    texto_ia = gemini.gerar_analise_jornalistica(noticia["titulo"], noticia["texto"], tema_forcado)

    # Busca visual inteligente no Modo Teste também
    query_visual = gemini.gerar_query_visual(noticia["titulo"], noticia["texto"])
    imagem_final = imagem_engine.obter_imagem(noticia, tema_forcado, query_ia=query_visual)

    tags = gerar_tags_seo(noticia["titulo"], texto_ia)

    dados = {
        "titulo": noticia["titulo"],
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    service = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=service)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": noticia["titulo"],
            "content": html,
            "labels": tags
        },
        isDraft=not publicar
    ).execute()

    print("Postagem de teste concluída.")


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    if os.getenv("TEST_MODE") == "true":
        tema_teste = os.getenv("TEST_TEMA", "policial")
        publicar_teste = os.getenv("TEST_PUBLICAR", "false") == "true"
        executar_modo_teste(tema_forcado=tema_teste, publicar=publicar_teste)
        exit()

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

    texto_ia = gemini.gerar_analise_jornalistica(noticia["titulo"], noticia["texto"], tema_escolhido)
    
    # Nova lógica de busca visual inteligente
    query_visual = gemini.gerar_query_visual(noticia["titulo"], noticia["texto"])
    imagem_final = imagem_engine.obter_imagem(noticia, tema_forcado, query_ia=query_visual)
    
    tags = gerar_tags_seo(noticia["titulo"], texto_ia)

    dados = {
        "titulo": noticia["titulo"],
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    service = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=service)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": noticia["titulo"],
            "content": html,
            "labels": tags
        },
        isDraft=False
    ).execute()

    registrar_postagem(data_hoje, horario_escolhido)
    registrar_link_publicado(noticia["link"])

    print(f"Post publicado com sucesso: {noticia['titulo']}")
