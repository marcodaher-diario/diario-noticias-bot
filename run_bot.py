# =============================================================
# RUN_BOT.PY — DIÁRIO DE NOTÍCIAS (VERSÃO BLINDADA)
# =============================================================

import feedparser
import re
import os
import time
import json
import random
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google import genai

try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = "<p style='text-align:center;'>© Marco Daher 2026</p>"

# =============================
# CONFIGURAÇÕES GERAIS
# =============================
BLOG_ID = "7605688984374445860"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/",
    "https://feeds.uol.com.br/home.xml",
    "https://rss.uol.com.br/feed/noticias.xml",
    "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://agenciabrasil.ebc.com.br/rss",
    "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
    "https://www.camara.leg.br/noticias/rss/politica", 
    "https://www12.senado.leg.br/noticias/rss", 
    "https://www.infomoney.com.br/mercado/feed/", 
    "https://br.investing.com/rss/news.rss", 
    "https://portal.stf.jus.br/noticias/rss.asp", 
    "https://www.canalrural.com.br/feed/",
    "https://www.poder360.com.br/feed/"
]

IMAGEM_FALLBACK = "https://images.pexels.com/photos/3944454/pexels-photo-3944454.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"

# =============================
# FILTROS DE QUALIDADE
# =============================

def e_titulo_inutil(titulo):
    """Filtra títulos que não são notícias reais (vídeos, transmissões, etc)."""
    termos_proibidos = ["VÍDEOS:", "ASSISTA:", "OUÇA:", "ÍNTEGRA:", "AO VIVO:", "JORNAL ANHANGUERA", "VÍDEO:", "PODCAST:"]
    for termo in termos_proibidos:
        if termo in titulo.upper():
            return True
    return False

# =============================
# AUTENTICAÇÃO
# =============================

def autenticar_blogger():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("token.json ausente!")
    creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/blogger"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("blogger", "v3", credentials=creds)

# ===============================
# IA — GERAÇÃO COM GEMINI
# ===============================

def gerar_texto_ia_gemini(titulo, fonte_nome):
    prompt = (
        f"Aja como um jornalista sênior. Escreva uma notícia detalhada e informativa baseada exclusivamente no título: '{titulo}'.\n"
        f"Mencione que os fatos iniciais são do portal {fonte_nome}. "
        "O texto deve ser longo, com no mínimo 5 parágrafos e tom sério. "
        "Se o título não contiver uma notícia real ou for impossível criar um texto informativo, responda apenas com a palavra: ERRO_INSUFICIENTE."
    )
    try:
        response = client_gemini.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        texto = response.text.strip()
        # Se a IA não gerou conteúdo suficiente ou deu a palavra de erro, descartamos
        if "ERRO_INSUFICIENTE" in texto or len(texto) < 500:
            return None
        return texto
    except:
        return None

# ===============================
# UTILITÁRIOS
# ===============================

def noticia_recente(entry, horas=12):
    data = entry.get("published_parsed") or entry.get("updated_parsed")
    if not data: return False
    return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)

def extrair_imagem(entry):
    img = None
    if hasattr(entry, "media_content"): img = entry.media_content[0].get("url")
    elif hasattr(entry, "media_thumbnail"): img = entry.media_thumbnail[0].get("url")
    if not img:
        match = re.search(r'<img[^>]+src="([^">]+)"', entry.get("summary", ""))
        if match: img = match.group(1)
    if img and any(x in img.lower() for x in ["video", "icon", "1x1", "logo"]):
        return IMAGEM_FALLBACK
    return img or IMAGEM_FALLBACK

def gerar_html_final(n):
    paragrafos = n['texto'].split('\n')
    html_corpo = "".join([f"<p style='text-align:justify; font-size: medium; line-height:1.6;'>{p.strip()}</p>" for p in paragrafos if len(p.strip()) > 10])
    
    return f"""
    <div style="color: #003366; font-family: Arial, sans-serif;">
        <h1 style="text-align: center;">{n['titulo'].upper()}</h1>
        <div style='text-align:center; margin-bottom:20px;'>
            <img src='{n['imagem']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px;'/>
        </div>
        <p style="text-align:center; font-size:13px; color: #666;"><b>Fonte Original:</b> {n['fonte']}</p>
        {html_corpo}
        <div style="text-align:center; margin: 30px 0;">
            <a href="{n['link']}" target="_blank" style="background-color: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">Leia a Matéria Original</a>
        </div>
        {BLOCO_FIXO_FINAL}
    </div>
    """

# =============================
# EXECUÇÃO
# =============================

def executar():
    service = autenticar_blogger()
    processadas = []
    
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Notícias")
        for entry in feed.entries:
            titulo = entry.get("title", "").strip()
            
            # FILTRO 1: Ignora títulos inúteis (vídeos/transmissões)
            if e_titulo_inutil(titulo) or not noticia_recente(entry):
                continue
            
            # FILTRO 2: Tenta gerar com IA, se retornar None (erro ou curto), descarta
            texto_ia = gerar_texto_ia_gemini(titulo, fonte)
            if not texto_ia:
                print(f"⏩ Descartado (Sem conteúdo real): {titulo}")
                continue
                
            processadas.append({
                "titulo": titulo, "texto": texto_ia, "link": entry.get("link", ""),
                "fonte": fonte, "imagem": extrair_imagem(entry)
            })
            if len(processadas) >= 5: break
        if len(processadas) >= 5: break

    for n in processadas:
        try:
            service.posts().insert(blogId=BLOG_ID, body={
                "title": n["titulo"], "content": gerar_html_final(n),
                "labels": ["Notícias", n["fonte"]], "status": "LIVE"
            }).execute()
            print(f"✅ Publicado: {n['titulo']}")
            time.sleep(10)
        except Exception as e: print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar()
