# -*- coding: utf-8 -*-

import os
import requests
from datetime import datetime, timedelta
from PIL import Image
from io import BytesIO


ARQUIVO_CONTROLE_IMAGENS = "controle_imagens.txt"
PASTA_ASSETS = "assets"
DIAS_BLOQUEIO = 30


class ImageEngine:

    def __init__(self):
        self.pexels_key = os.getenv("PEXELS_API_KEY")
        self.unsplash_key = os.getenv("UNSPLASH_API_KEY")


    # ==========================================================
    # CONTROLE DE REPETIÇÃO POR TEMA (30 DIAS) - BLINDADO
    # ==========================================================

    def _imagem_usada_recentemente(self, tema, url):
        if not os.path.exists(ARQUIVO_CONTROLE_IMAGENS):
            return False

        hoje = datetime.utcnow()

        with open(ARQUIVO_CONTROLE_IMAGENS, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()

                # Ignora linha vazia
                if not linha:
                    continue

                # Ignora linha inválida
                if "|" not in linha:
                    continue

                partes = linha.split("|")

                if len(partes) != 3:
                    continue

                data_str, tema_salvo, url_salva = partes

                if tema_salvo != tema:
                    continue

                try:
                    data_img = datetime.strptime(data_str, "%Y-%m-%d")
                except:
                    continue

                if url_salva == url and (hoje - data_img).days < DIAS_BLOQUEIO:
                    return True

        return False


    def _registrar_imagem(self, tema, url):
        hoje = datetime.utcnow().strftime("%Y-%m-%d")

        with open(ARQUIVO_CONTROLE_IMAGENS, "a", encoding="utf-8") as f:
            f.write(f"{hoje}|{tema}|{url}\n")


    # ==========================================================
    # VERIFICAR TAMANHO RSS (>= 600px)
    # ==========================================================

    def _rss_valida(self, url):
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(BytesIO(response.content))
            largura, _ = img.size
            return largura >= 600
        except:
            return False


    # ==========================================================
    # BUSCA PEXELS
    # ==========================================================

    def _buscar_pexels(self, query, tema):

        headers = {"Authorization": self.pexels_key}

        url = "https://api.pexels.com/v1/search"

        params = {
            "query": query,
            "orientation": "landscape",
            "size": "large",
            "per_page": 10
        }

        r = requests.get(url, headers=headers, params=params)

        if r.status_code != 200:
            return None

        data = r.json()

        for foto in data.get("photos", []):
            img_url = foto["src"]["large"]

            if not self._imagem_usada_recentemente(tema, img_url):
                self._registrar_imagem(tema, img_url)
                return img_url

        return None


    # ==========================================================
    # BUSCA UNSPLASH
    # ==========================================================

    def _buscar_unsplash(self, query, tema):

        url = "https://api.unsplash.com/search/photos"

        params = {
            "query": query,
            "orientation": "landscape",
            "per_page": 10,
            "client_id": self.unsplash_key
        }

        r = requests.get(url, params=params)

        if r.status_code != 200:
            return None

        data = r.json()

        for foto in data.get("results", []):
            img_url = foto["urls"]["regular"]

            if not self._imagem_usada_recentemente(tema, img_url):
                self._registrar_imagem(tema, img_url)
                return img_url

        return None


    # ==========================================================
    # IMAGEM INSTITUCIONAL SEQUENCIAL
    # ==========================================================

    def _buscar_institucional(self, tema):

        pasta_tema = os.path.join(PASTA_ASSETS, tema)

        if not os.path.exists(pasta_tema):
            return None

        arquivos = sorted([f for f in os.listdir(pasta_tema) if f.lower().endswith(".jpg")])

        if not arquivos:
            return None

        ultimo_usado = None

        if os.path.exists(ARQUIVO_CONTROLE_IMAGENS):
            with open(ARQUIVO_CONTROLE_IMAGENS, "r", encoding="utf-8") as f:
                for linha in reversed(f.readlines()):
                    linha = linha.strip()

                    if not linha or "|" not in linha:
                        continue

                    partes = linha.split("|")

                    if len(partes) != 3:
                        continue

                    data_str, tema_salvo, url_salva = partes

                    if tema_salvo == tema and "assets" in url_salva:
                        ultimo_usado = os.path.basename(url_salva)
                        break

        if ultimo_usado and ultimo_usado in arquivos:
            indice = arquivos.index(ultimo_usado) + 1
        else:
            indice = 0

        if indice >= len(arquivos):
            indice = 0

        proximo = arquivos[indice]

        caminho_relativo = f"{PASTA_ASSETS}/{tema}/{proximo}"

        url_publica = f"https://marcodaher-diario.github.io/diario-noticias-bot/{caminho_relativo}"

        self._registrar_imagem(tema, url_publica)

        return url_publica


    # ==========================================================
    # FUNÇÃO PRINCIPAL
    # ==========================================================

    def obter_imagem(self, noticia, tema):

        # 1️⃣ RSS
        rss_img = noticia.get("imagem", "")

        if rss_img and self._rss_valida(rss_img):
            if not self._imagem_usada_recentemente(tema, rss_img):
                self._registrar_imagem(tema, rss_img)
                return rss_img

        # Query refinada Brasil
        titulo = noticia.get("titulo", "")
        query = f"{tema} Brasil {titulo}"

        # 2️⃣ Pexels
        if self.pexels_key:
            img = self._buscar_pexels(query, tema)
            if img:
                return img

        # 3️⃣ Unsplash
        if self.unsplash_key:
            img = self._buscar_unsplash(query, tema)
            if img:
                return img

        # 4️⃣ Institucional
        return self._buscar_institucional(tema)
