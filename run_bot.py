import os
import json
import feedparser
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google import genai  # Biblioteca do seu manual
from google.genai import types

# --- IMPORTAÇÃO DO SEU TEMPLATE ---
from template_blog import obter_esqueleto_html

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "3884849132228514800"
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
    print("🚀 Iniciando Bot Diário de Notícias (Manual 2026)...")
    creds = renovar_token()
    service_blogger = build('blogger', 'v3', credentials=creds)
    
    # Inicializa o cliente conforme seu manual
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 1. Busca Notícia
    feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
    noticia = feed.entries[0]
    print(f"📰 Notícia: {noticia.title}")

    # 2. Gera Texto usando o modelo do seu manual (Gemini 3 Flash Preview)
    prompt = (
        f"Com base na notícia '{noticia.title}', escreva um artigo analítico. "
        "Retorne APENAS um JSON com estas chaves: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao."
    )
    
    print("✍️ Gerando texto estruturado com Gemini 3...")
    try:
        # Usando o modelo EXATO do seu manual
        response = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        dados = json.loads(response.text)
    except Exception as e:
        print(f"⚠️ Erro no Gemini 3, tentando 1.5-flash-002: {e}")
        # Segunda tentativa com o nome técnico mais recente
        response = client.models.generate_content(
            model="gemini-1.5-flash-002", 
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        dados = json.loads(response.text)

    # 3. Preparar Campos do Template
    dados['img_topo'] = "https://via.placeholder.com/1280x720.png?text=Noticia+Principal"
    dados['img_meio'] = "https://via.placeholder.com/1280x720.png?text=Analise+Politica"
    dados['assinatura'] = f"<hr><p style='text-align:right;'>Fonte: <a href='{noticia.link}'>G1 Política</a></p>"

    # 4. Montar e Publicar
    print("🏗️ Renderizando Template...")
    html_final = obter_esqueleto_html(dados)

    corpo_post = {
        'kind': 'blogger#post',
        'title': dados['titulo'],
        'content': html_final
    }
    
    service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
    print(f"✅ SUCESSO! Postado no Blogger via Gemini 3.")

if __name__ == "__main__":
    executar()
