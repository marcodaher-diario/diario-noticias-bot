# -*- coding: utf-8 -*-

import os
import requests
import random
from datetime import datetime, timedelta

ARQUIVO_IMAGENS = "imagens_usadas.txt"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")

# ==========================================
# CONTROLE DE IMAGENS USADAS (30 DIAS)
# ==========================================

def carregar_imagens_usadas():
    imagens = {}

    if not os.path.exists(ARQUIVO_IMAGENS):
        return imagens

    with open(ARQUIVO_IMAGENS, "r", encoding="utf-8") as f:
        for linha in f:
            try:
                url, data_str = linha.strip().split("|")
                data = datetime.strptime(data_str, "%Y-%m-%d")
                imagens[url] = data
            except:
                continue

    return imagens


def limpar_imagens_antigas(imagens):
    hoje = datetime.now()
    limite = hoje - timedelta(days=30)

    imagens_filtradas = {
        url: data for url, data in imagens.items()
        if data >= limite
    }

    with open(ARQUIVO_IMAGENS, "w", encoding="utf-8") as f:
        for url, data in imagens_filtradas.items():
            f.write(f"{url}|{data.strftime('%Y-%m-%d')}\n")

    return imagens_filtradas


def registrar_imagem(url):
    hoje = datetime.now().strftime("%Y-%m-%d")

    with open(ARQUIVO_IMAGENS, "a", encoding="utf-8") as f:
        f.write(f"{url}|{hoje}\n")


# ==========================================
# BUSCAR IMAGEM NO PEXELS
# ==========================================

def buscar_imagem_pexels(query):

    if not PEXELS_API_KEY:
        return None

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "orientation": "landscape",
        "size": "large",
        "per_page": 15
    }

    try:
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return None

        data = response.json()
        fotos = data.get("photos", [])

        if not fotos:
            return None

        imagens_usadas = carregar_imagens_usadas()
        imagens_usadas = limpar_imagens_antigas(imagens_usadas)

        candidatos = []

        for foto in fotos:
            url = foto.get("src", {}).get("large")

            if url and url not in imagens_usadas:
                candidatos.append(url)

        if not candidatos:
            return None

        imagem_escolhida = random.choice(candidatos)

        registrar_imagem(imagem_escolhida)

        return imagem_escolhida

    except Exception:
        return None


# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================

def obter_imagem_para_noticia(titulo, tipo):

    # Prioridade 1: usar título
    imagem = buscar_imagem_pexels(titulo)

    if imagem:
        return imagem

    # Prioridade 2: usar categoria
    imagem = buscar_imagem_pexels(tipo)

    if imagem:
        return imagem

    # Fallback absoluto
    return "https://images.pexels.com/photos/518543/pexels-photo-518543.jpeg"
