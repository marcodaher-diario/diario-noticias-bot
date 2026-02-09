import os
import json
import feedparser
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.generativeai as genai  # Biblioteca estável
import datetime
import pytz

# --- IMPORTAÇÃO DO TEMPLATE ---
try:
    from template_blog import obter_esqueleto_html
except ImportError:
    print("❌ ERRO: Arquivo 'template_blog.py' não encontrado.")
    raise

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "3884849132228514800"
genai.configure(api_key=GEMINI_API_KEY)

SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

# --- AUTENTICAÇÃO ---
def renovar_token():
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

# --- DRIVE ---
def upload_para_drive(service_drive, caminho_arquivo, nome_arquivo):
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    file = service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

# --- NÚCLEO ---
def executar():
    print("🚀 Iniciando Bot Diário de Notícias (Versão Estável)...")
    creds = renovar_token()
    service_blogger = build('blogger', 'v3', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)

    # 1. Busca Notícia
    feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
    noticia = feed.entries[0]
    titulo = noticia.title
    print(f"📰 Notícia: {titulo}")

    # 2. Gera Texto (Usando a biblioteca estável)
    model_text = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"Escreva um artigo de opinião longo (800 palavras) em HTML sobre: {titulo}. Use H2 e parágrafos."
    
    print("✍️ Gerando texto...")
    response = model_text.generate_content(prompt)
    texto_analitico = response.text

    # 3. Gerar Imagens (Simulação ou via Imagen se disponível)
    # Nota: A biblioteca estável usa um fluxo diferente para imagens. 
    # Para garantir o post AGORA, vou focar no texto e link da notícia.
    
    # 4. Publicar
    html_final = obter_esqueleto_html(
        titulo=titulo,
        corpo_texto=texto_analitico,
        img_topo="https://via.placeholder.com/800x450.png?text=Diario+de+Noticias",
        img_corpo="https://via.placeholder.com/800x450.png?text=Analise+Politica",
        fonte_link=noticia.link
    )

    corpo_post = {'kind': 'blogger#post', 'title': titulo, 'content': html_final}
    service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
    print(f"✅ SUCESSO! Postado: {titulo}")

if __name__ == "__main__":
    executar()
