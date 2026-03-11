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

import requests
from bs4 import BeautifulSoup


def extrair_imagem_noticia(entry):

    # ======================================================
    # 1️⃣ CAMPOS RSS MAIS COMUNS
    # ======================================================

    try:

        if hasattr(entry, "media_content"):
            for media in entry.media_content:
                url = media.get("url", "")
                if url:
                    return url

        if hasattr(entry, "media_thumbnail"):
            for media in entry.media_thumbnail:
                url = media.get("url", "")
                if url:
                    return url

        if hasattr(entry, "links"):
            for link in entry.links:
                if link.get("type", "").startswith("image"):
                    return link.get("href")

        if hasattr(entry, "enclosures"):
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image"):
                    return enc.get("href")

    except:
        pass


    # ======================================================
    # 2️⃣ IMAGEM DENTRO DO SUMMARY
    # ======================================================

    try:

        if hasattr(entry, "summary"):
            soup = BeautifulSoup(entry.summary, "html.parser")

            img = soup.find("img")

            if img and img.get("src"):
                return img.get("src")

    except:
        pass


    # ======================================================
    # 3️⃣ OG:IMAGE DA PÁGINA DA NOTÍCIA
    # ======================================================

    try:

        url = entry.link

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=8)

        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")

        if og and og.get("content"):
            return og.get("content")

        tw = soup.find("meta", attrs={"name": "twitter:image"})

        if tw and tw.get("content"):
            return tw.get("content")

    except:
        pass


    return ""

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
# CONTROLE DE LINKS
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

    if maior_score >= 8:
        return melhor_tema

    return "geral"


# ==========================================================
# BUSCAR NOTÍCIA (BUSCA PROGRESSIVA)
# ==========================================================

def buscar_noticia(tipo):

    tipo = remover_acentos(tipo.lower())

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
                imagem = extrair_imagem_noticia(entry)

                if not titulo or not link:
                    continue

                tema_detectado = verificar_assunto(titulo,resumo)

                if tema_detectado != tipo and tema_detectado != "geral":
                    continue

                if link_ja_publicado(link):
                    continue
                    
                data_publicacao = None
                
                if hasattr(entry,"published"):
                    try:
                        data_publicacao = parsedate_to_datetime(entry.published)
                
                        # normaliza timezone para evitar erro datetime
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

                    ocorrencias = conteudo.count(palavra_norm)

                    if ocorrencias > 0:
                        score += peso * ocorrencias

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

# ==========================================================
# GERAR TAGS SEO - SISTEMA AVANÇADO DE NOTÍCIAS
# ==========================================================

def gerar_tags_seo(titulo, texto):

    stopwords = [
        "com","como","para","porque","sobre","entre","de","do","da",
        "dos","das","em","um","uma","os","as","que","no","na","ao",
        "aos","por","mais","menos","ser","estar","ter","se","sua",
        "seu","suas","seus","também","muito","muitos","muitas"
    ]

    # ======================================================
    # CLUSTERS PRINCIPAIS
    # ======================================================

    clusters = {

        "política": [
            "governo","planalto","presidente","ministro","congresso",
            "senado","câmara","camara","stf","supremo","eleição",
            "reforma","partido","deputado","senador"
        ],

        "economia": [
            "economia","inflação","inflacao","selic","juros","dólar",
            "pib","mercado","investimento","bolsa","ibovespa",
            "ipca","emprego","desemprego"
        ],

        "segurança": [
            "polícia","policia","crime","assassinato","homicídio",
            "latrocínio","tráfico","operação","prisão","suspeito",
            "delegacia","investigação"
        ],

        "justiça": [
            "tribunal","justiça","juiz","sentença","processo",
            "acusação","denúncia","investigação"
        ],

        "internacional": [
            "guerra","otan","china","russia","ucrânia","israel",
            "irã","eua","europa"
        ]
    }

    # ======================================================
    # ENTIDADES IMPORTANTES
    # ======================================================

    entidades = {

        "stf": "Supremo Tribunal Federal",
        "supremo": "Supremo Tribunal Federal",
        "senado": "Senado Federal",
        "câmara": "Câmara dos Deputados",
        "camara": "Câmara dos Deputados",
        "planalto": "Palácio do Planalto",
        "congresso": "Congresso Nacional",
        "polícia federal": "Polícia Federal",
        "pf": "Polícia Federal",
        "banco central": "Banco Central",
        "ibovespa": "Ibovespa",
        "petrobras": "Petrobras",
        "vale": "Vale",
        "onu": "ONU",
        "otan": "OTAN"
    }

    # ======================================================
    # ENTIDADES DE PESSOAS (FIGURAS PÚBLICAS)
    # ======================================================

    pessoas = {
        "lula": "Lula",
        "bolsonaro": "Bolsonaro",
        "moraes": "Alexandre de Moraes",
        "barroso": "Luís Roberto Barroso",
        "fachin": "Edson Fachin",
        "putin": "Vladimir Putin",
        "biden": "Joe Biden",
        "netanyahu": "Benjamin Netanyahu",
        "xi": "Xi Jinping"
    }

    conteudo = f"{titulo} {texto[:200]}"
    texto_total = conteudo.lower()

    palavras_titulo = re.findall(r'\b[a-zà-ÿ]{4,}\b', titulo.lower())
    palavras_texto = re.findall(r'\b[a-zà-ÿ]{4,}\b', texto_total)

    tags = []

    # ======================================================
    # TAGS DO TÍTULO
    # ======================================================

    for p in palavras_titulo:
        if p not in stopwords:
            tag = p.capitalize()
            if tag not in tags:
                tags.append(tag)

    # ======================================================
    # TAGS DO TEXTO
    # ======================================================

    for p in palavras_texto:
        if p not in stopwords:
            tag = p.capitalize()
            if tag not in tags:
                tags.append(tag)

    # ======================================================
    # ENTIDADES
    # ======================================================

    for chave, entidade in entidades.items():
        if chave in texto_total and entidade not in tags:
            tags.append(entidade)

    # ======================================================
    # PESSOAS IMPORTANTES
    # ======================================================

    for chave, nome in pessoas.items():
        if chave in texto_total and nome not in tags:
            tags.append(nome)

    # ======================================================
    # CLUSTERS
    # ======================================================

    for cluster, palavras in clusters.items():
        for palavra in palavras:
            if palavra in texto_total:
                tag_cluster = cluster.capitalize()
                if tag_cluster not in tags:
                    tags.append(tag_cluster)
                break

    # ======================================================
    # TAGS FIXAS
    # ======================================================

    tags_fixas = [
        "Diário de Notícias",
        "Marco Daher"
    ]

    for tf in tags_fixas:
        if tf not in tags:
            tags.append(tf)

    # ======================================================
    # LIMITADOR DE 200 CARACTERES
    # ======================================================

    resultado = []
    tamanho_atual = 0

    for tag in tags:

        tamanho_tag = len(tag)

        if tamanho_atual + tamanho_tag + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += tamanho_tag + 2
        else:
            break

    return resultado


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

    texto_ia = gemini.gerar_analise_jornalistica(
        noticia["titulo"],
        noticia["texto"],
        tema_forcado
    )

    query_visual = gemini.gerar_query_visual(
        noticia["titulo"],
        noticia["texto"]
    )
    texto_total = (noticia["titulo"] + " " + noticia["texto"]).lower()

    if "stf" in texto_total or "supremo" in texto_total:
        query_visual = "Supremo Tribunal Federal Brasília Brazil building"
    
    elif "senado" in texto_total:
        query_visual = "Senado Federal Brasília Brazil congress building"
    
    elif "câmara" in texto_total or "camara" in texto_total:
        query_visual = "Câmara dos Deputados Brasília Brazil congress building"
    
    elif "planalto" in texto_total:
        query_visual = "Palácio do Planalto Brasília Brazil government palace"

    # IRÃ / KHAMENEI
    if "khamenei" in texto_total or "irã" in texto_total or "ira" in texto_total:
        query_visual = "Ali Khamenei Iran supreme leader portrait Tehran"
    
    # STF
    elif "stf" in texto_total or "supremo tribunal federal" in texto_total:
        query_visual = "Supremo Tribunal Federal building Brasília Brazil"
    
    # CONGRESSO
    elif "senado" in texto_total:
        query_visual = "Senado Federal Brasília Brazil congress building"
    
    elif "câmara" in texto_total or "camara" in texto_total:
        query_visual = "Câmara dos Deputados Brasília Brazil congress building"
    
    # GOVERNO BRASIL
    elif "planalto" in texto_total or "presidente" in texto_total:
        query_visual = "Palácio do Planalto Brasília Brazil government palace"

    texto_total = (noticia["titulo"] + " " + noticia["texto"]).lower()

    imagem_final = imagem_engine.obter_imagem(
        noticia,
        tema_forcado,
        query_ia=query_visual
    )

    dados = {
        "titulo": noticia["titulo"],
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    service = Credentials.from_authorized_user_file("token.json")

    service = build("blogger", "v3", credentials=service)

    tags = gerar_tags_seo(noticia["titulo"], texto_ia)

service.posts().insert(
    blogId=BLOG_ID,
    body={
        "title": noticia["titulo"],
        "content": html,
        "labels": tags
    },
    isDraft=False
).execute()

    print("Postagem de teste concluída.")


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    if os.getenv("TEST_MODE") == "true":

        tema_teste = os.getenv("TEST_TEMA","policial")

        publicar_teste = os.getenv("TEST_PUBLICAR","false") == "true"

        executar_modo_teste(
            tema_forcado=tema_teste,
            publicar=publicar_teste
        )

        exit()

    agora = obter_horario_brasilia()

    min_atual = agora.hour * 60 + agora.minute

    data_hoje = agora.strftime("%Y-%m-%d")

    horario_escolhido = None

    tema_escolhido = None

    for horario_agenda,tema in AGENDA_POSTAGENS.items():

        min_agenda = horario_para_minutos(horario_agenda)

        if dentro_da_janela(min_atual,min_agenda):

            if not ja_postou(data_hoje,horario_agenda):
                horario_escolhido = horario_agenda
                tema_escolhido = tema
                break

    if not horario_escolhido:
        exit()

    noticia = buscar_noticia(tema_escolhido)

    if not noticia:
        exit()

    executar_modo_teste(tema_escolhido, True)

    registrar_postagem(data_hoje, horario_escolhido)

    registrar_link_publicado(noticia["link"])

    registrar_link_publicado(gerar_id_noticia(noticia["titulo"]))

    print(f"Post publicado com sucesso: {noticia['titulo']}")
