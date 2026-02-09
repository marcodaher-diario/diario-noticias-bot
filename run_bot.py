import os
import json
import feedparser
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google import genai
from google.genai import types

# --- IMPORTAÇÃO DO SEU TEMPLATE ---
from template_blog import obter_esqueleto_html

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# ID ATUALIZADO CONFORME SUA URL:
BLOG_ID = "7605688984374445860" 

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
    print(f"🚀 Iniciando Bot no Blog ID: {BLOG_ID}")
    creds = renovar_token()
    service_blogger = build('blogger', 'v3', credentials=creds)
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 1. Busca Notícia
    feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
    if not feed.entries:
        print("⚠️ Nenhum feed encontrado.")
        return
    
    noticia = feed.entries[0]
    print(f"📰 Notícia: {noticia.title}")

    # 2. IA gera o texto (Gemini 3 Flash - Sucesso comprovado no teste anterior)
    prompt = (
        f"Com base na notícia '{noticia.title}', escreva um artigo analítico profundo para um blog de política. "
        "Retorne APENAS um JSON com estas chaves: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao."
    )
    
    print("✍️ Gerando conteúdo com Gemini 3...")
    response = client.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    dados = json.loads(response.text)

    # 3. Preparar Campos do Template
    # Usando proporção 16:9 conforme sua preferência
    dados['img_topo'] = "https://via.placeholder.com/1280x720.png?text=Noticia+do+Dia"
    dados['img_meio'] = "https://via.placeholder.com/1280x720.png?text=Analise+Politica"
    dados['assinatura'] = f"<hr><p style='text-align:right;'>Fonte: <a href='{noticia.link}'>G1 Política</a> | IA Bot 2026</p>"

    # 4. Montar e Publicar
    print("🏗️ Renderizando Template Azul Marinho...")
    html_final = obter_esqueleto_html(dados)

    corpo_post = {
        'kind': 'blogger#post',
        'title': dados['titulo'],
        'content': html_final
    }
    
    print("📤 Enviando para o Blogger...")
    try:
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO ABSOLUTO! O post '{dados['titulo']}' já deve estar visível.")
    except Exception as e:
        print(f"❌ Erro na publicação final: {e}")

if __name__ == "__main__":
    executar()
