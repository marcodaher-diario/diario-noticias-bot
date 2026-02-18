# -*- coding: utf-8 -*-

import requests
import os
import re


PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


# ==========================================
# VALIDAR IMAGEM RSS
# ==========================================

def imagem_rss_valida(url):

    if not url:
        return False

    if not url.startswith("http"):
        return False

    try:
        response = requests.head(url, timeout=5)

        if response.status_code != 200:
            return False

        content_type = response.headers.get("Content-Type", "")

        if "image" not in content_type:
            return False

        return True

    except Exception:
        return False


# ==========================================
# LIMPAR TÍTULO PARA BUSCA
# ==========================================

def limpar_titulo_para_busca(titulo):

    titulo = re.sub(r"[^\w\s]", "", titulo)
    titulo = titulo.lower()

    palavras = re.findall(r"\b\w{4,}\b", titulo)

    stopwords = [
        "sobre", "entre", "após", "para",
        "governo", "brasil", "caso"
    ]

    palavras = [p for p in palavras if p not in stopwords]

    return " ".join(palavras[:3])


# ==========================================
# BUSCAR IMAGEM NO PEXELS
# ==========================================

def buscar_imagem_pexels(query):

    if not PEXELS_API_KEY:
        return None

    url = "https://api.pexels.com/v1/search"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": 10,
        "orientation": "landscape"
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()

        fotos = data.get("photos", [])

        if not fotos:
            return None

        return fotos[0]["src"]["large2x"]

    except Exception:
        return None


# ==========================================
# MOTOR PRINCIPAL
# ==========================================

def obter_imagem_inteligente(titulo, imagem_rss):

    # 1️⃣ Tenta usar imagem RSS
    if imagem_rss_valida(imagem_rss):
        return imagem_rss

    # 2️⃣ Se não for válida → busca no Pexels
    query = limpar_titulo_para_busca(titulo)

    imagem_pexels = buscar_imagem_pexels(query)

    return imagem_pexels
