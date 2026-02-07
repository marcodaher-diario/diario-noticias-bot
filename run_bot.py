# =============================================================
# RUN_BOT.PY — DIÁRIO DE NOTÍCIAS (VERSÃO GEMINI IA)
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
from google import genai  # Biblioteca do Google Gemini

# IMPORTAÇÃO DA ASSINATURA DO ARQUIVO CONFIGURACOES.PY
try:
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    BLOCO_FIXO_FINAL = "<p style='text-align:center;'>© Marco Daher 2026</p>"

# =============================
# CONFIGURAÇÕES GERAIS
# =============================

BLOG_ID = "7605688984374445860"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

# Configuração da API do Gemini
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
# AUTENTICAÇÃO BLOGGER
# =============================

def autenticar_blogger():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("O arquivo token.json não foi encontrado!")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("blogger", "v3", credentials=creds)

# ===============================
# IA — GERAÇÃO COM GEMINI
# ===============================

def gerar_texto_ia_gemini(titulo, fonte_nome):
    prompt = (
        f"Aja como um jornalista sênior. Escreva uma notícia detalhada, imparcial e informativa baseada no título: '{titulo}'.\n"
        f"Mencione que os fatos iniciais foram apurados pelo portal {fonte_nome}. "
        "O texto deve ter pelo menos 4 parágrafos bem desenvolvidos (aprox. 500 palavras). "
        "Use tom jornalístico profissional. Não use formatação Markdown (como asteriscos ou hashtags)."
    )
    try:
        response = client_gemini.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"⚠️ Erro Gemini: {e}")
        return f"Matéria em atualização sobre: {titulo}. Mais detalhes em instantes."

# ===============================
# TRATAMENTO DE IMAGEM E DATA
# ===============================

def noticia_recente(entry, horas=48):
    data = entry.get("published_parsed") or entry.get("updated_parsed")
    if not data:
        return False
    return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)

def extrair_imagem(entry):
    img = None
    if hasattr(entry, "media_content"):
        img = entry.media_content[0].get("url")
    elif hasattr(entry, "media_thumbnail"):
        img = entry.media_thumbnail[0].get("url")
    
    if not img:
        summary = entry.get("summary", "")
        match = re.search(r'<img[^>]+src="([^">]+)"', summary)
        if match: img = match.group(1)
    
    if img and any(x in img.lower() for x in ["video", "icon", "1x1", "logo"]):
        return IMAGEM_FALLBACK
    return img if img else IMAGEM_FALLBACK

def gerar_tags(titulo):
    palavras = re.findall(r'\w+', titulo.lower())
    ignorar = {"o", "a", "os", "as", "em", "de", "do", "da", "para", "com", "que"}
    tags = [p.capitalize() for p in palavras if p not in ignorar and len(p) > 3]
    return tags[:5]

# ===============================
# FORMATAÇÃO HTML
# ===============================

def formatar_texto_html(texto_ia):
    paragrafos = texto_ia.split('\n')
    html = ""
    for p in paragrafos:
        if len(p.strip()) > 10:
            html += f"<p style='text-align:justify; font-size: medium; line-height:1.6;'>{p.strip()}</p>"
    return html

def gerar_html_final(n):
    return f"""
    <div style="color: #003366; font-family: Arial, sans-serif; line-height: 1.6;">
        <h1 style="font-weight: bold; margin-bottom: 20px; text-align: center; font-size: x-large;">
            {n['titulo'].upper()}
        </h1>

        <div style='text-align:center; margin-bottom:20px;'>
            <img src='{n['imagem']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'/>
        </div>

        <p style="text-align:center; font-size:13px; color: #666; margin-bottom: 20px;">
            <b>Fonte Original:</b> {n['fonte']}
        </p>

        {formatar_texto_html(n['texto'])}

        <div style="text-align:center; margin: 30px 0;">
            <a href="{n['link']}" target="_blank" style="background-color: #003366; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                Leia a Matéria Completa na Fonte
            </a>
        </div>

        <div style="margin-top: 10px;">
            {BLOCO_FIXO_FINAL}
        </div>
    </div>
    """

# =============================
# EXECUÇÃO PRINCIPAL
# =============================

def executar():
    service = autenticar_blogger()
    noticias_processadas = []
    
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte_nome = feed.feed.get("title", "Portal de Notícias")
        
        for entry in feed.entries:
            # FILTRO POR DATA (O que você já usava)
            if not noticia_recente(entry, horas=12):
                continue
                
            titulo = entry.get("title", "").strip()
            link = entry.get("link", "")
            
            # IA gera o texto completo baseado no título
            texto_ia = gerar_texto_ia_gemini(titulo, fonte_nome)
            imagem = extrair_imagem(entry)
            
            noticias_processadas.append({
                "titulo": titulo,
                "texto": texto_ia,
                "link": link,
                "fonte": fonte_nome,
                "imagem": imagem
            })
            if len(noticias_processadas) >= 10: break
        if len(noticias_processadas) >= 10: break

    for n in noticias_processadas:
        try:
            service.posts().insert(
                blogId=BLOG_ID,
                body={
                    "title": n["titulo"],
                    "content": gerar_html_final(n),
                    "labels": gerar_tags(n["titulo"]),
                    "status": "LIVE"
                }
            ).execute()
            print(f"✅ Publicado: {n['titulo']}")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    executar()
