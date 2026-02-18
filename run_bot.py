# -*- coding: utf-8 -*-

import feedparser
import re
import os
import random
import subprocess
import json
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
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
# CONFIGURAÇÃO DE AGENDA FIXA
# ==========================================

AGENDA_POSTAGENS = {
    "09:00": "policial",
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
# AUTENTICAÇÃO BLOGGER (ATUALIZADO)
# ==========================================

def autenticar_blogger():

    SCOPES = ["https://www.googleapis.com/auth/blogger"]

    # Cria credentials.json a partir do Secret
    if not os.path.exists("credentials.json"):
        cred_json = os.getenv("GOOGLE_CREDENTIALS")
        if not cred_json:
            raise Exception("Secret GOOGLE_CREDENTIALS não encontrado.")
        with open("credentials.json", "w", encoding="utf-8") as f:
            f.write(cred_json)

    creds = None

    # Se já existir token.json válido
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Se não existir ou estiver inválido, gera novo
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_console()

        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())

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

    _, hoje = obter_horario_brasilia()

    with open(ARQUIVO_CONTROLE_ASSUNTOS, "r", encoding="utf-8") as f:
        for linha in f:
            data, assunto_salvo = linha.strip().split("|", 1)
            if data == hoje and assunto in assunto_salvo:
                return True
    return False


def registrar_assunto(assunto):
    if not assunto:
        return
    _, hoje = obter_horario_brasilia()
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
                continue

            noticias.append({
                "titulo": titulo,
                "texto": texto,
                "link": link,
                "fonte": fonte,
                "imagem": entry.get("media_content", [{}])[0].get("url", ""),
                "assunto": assunto,
                "labels": gerar_tags_seo(titulo, texto)
            })

    random.shuffle(noticias)

    return noticias[:limite]


# ==========================================
# GERAR CONTEÚDO HTML
# ==========================================

def gerar_conteudo(n):

    texto_limpo = re.sub(r"<[^>]+>", "", n["texto"])[:4000]

    dados = {
        "titulo": n["titulo"],
        "img_topo": n["imagem"],
        "intro": texto_limpo[:500],
        "sub1": "Contexto",
        "texto1": texto_limpo[500:1200],
        "img_meio": n["imagem"],
        "sub2": "Desdobramentos",
        "texto2": texto_limpo[1200:2000],
        "sub3": "Impactos",
        "texto3": texto_limpo[2000:3000],
        "texto_conclusao": texto_limpo[3000:3800],
        "assinatura": BLOCO_FIXO_FINAL
    }

    html_final = obter_esqueleto_html(dados)

    if len(html_final) > 900000:
        html_final = html_final[:900000]

    return html_final


# ==========================================
# PUBLICAR POST
# ==========================================

def publicar_post(service, noticia):

    conteudo_html = gerar_conteudo(noticia)

    labels_seguras = [str(l).strip() for l in noticia.get("labels", []) if l]

    post = {
        "title": str(noticia["titulo"])[:150],
        "content": conteudo_html,
        "labels": labels_seguras
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post,
        isDraft=False
    ).execute()

    registrar_publicacao(noticia["link"])
    registrar_assunto(noticia["assunto"])


# ==========================================
# SALVAR ESTADO NO GITHUB
# ==========================================

def salvar_estado_github():
    try:
        subprocess.run(["git", "config", "--global", "user.name", "github-actions"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Atualiza controle automático"], check=True)
        subprocess.run(["git", "push"], check=True)
    except Exception:
        pass


# ==========================================
# EXECUÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":

    try:

        print("===== MODO TESTE FORÇADO ATIVO =====")

        service = autenticar_blogger()

        tipo_teste = "economia"

        print(f"Buscando notícia do tipo: {tipo_teste}")

        noticias = buscar_noticias(tipo_teste, limite=1)

        if not noticias:
            print("Nenhuma notícia encontrada.")
            exit()

        print("Publicando notícia de teste...")
        publicar_post(service, noticias[0])

        print("✅ POST PUBLICADO COM SUCESSO!")

        salvar_estado_github()

    except Exception as erro:
        print("Erro:", erro)
