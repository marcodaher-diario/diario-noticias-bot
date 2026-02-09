import os
import json
import feedparser
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai  # Biblioteca oficial 2026
from google.genai import types
import datetime

# --- IMPORTAÇÃO DO TEMPLATE ---
try:
    from template_blog import obter_esqueleto_html
except ImportError:
    print("❌ ERRO: template_blog.py não encontrado.")
    raise

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "3884849132228514800"

# Escopos
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

def renovar_token():
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def executar():
    print("🚀 Iniciando Bot Diário de Notícias...")
    creds = renovar_token()
    service_blogger = build('blogger', 'v3', credentials=creds)
    
    # Inicializa o Cliente Gemini corretamente
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 1. Busca Notícia
    feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
    noticia = feed.entries[0]
    titulo = noticia.title
    print(f"📰 Notícia: {titulo}")

    # 2. Gera Texto usando Gemini 3 Flash (Alta performance e cota estável)
    prompt = f"Escreva um artigo de opinião longo (800 palavras) em HTML sobre: {titulo}."
    
    print("✍️ Gerando texto com Gemini 3 Flash...")
    try:
        # Tentativa com o modelo mais atual da sua categoria (Free Tier)
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt
        )
    except Exception:
        # Fallback caso o preview ainda não esteja na sua chave
        print("⚠️ Gemini 3 não encontrado, tentando Gemini 1.5 Flash...")
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=prompt
        )
    
    texto_analitico = response.text

    # 3. Monta e Publica
    html_final = obter_esqueleto_html(
        titulo=titulo,
        corpo_texto=texto_analitico,
        img_topo="https://via.placeholder.com/1280x720.png?text=Diario+de+Noticias",
        img_corpo="https://via.placeholder.com/1280x720.png?text=Noticia+do+Dia",
        fonte_link=noticia.link
    )

    corpo_post = {'kind': 'blogger#post', 'title': titulo, 'content': html_final}
    service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
    print(f"✅ SUCESSO! Postado: {titulo}")

if __name__ == "__main__":
    executar()
