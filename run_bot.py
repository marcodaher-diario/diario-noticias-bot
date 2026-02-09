import os
import json
import feedparser
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

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

def gerar_texto_rest(titulo_noticia):
    """Gera texto via chamada REST direta para evitar erro 404 da biblioteca"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": f"Baseado na notícia '{titulo_noticia}', retorne APENAS um JSON: {{\"titulo\": \"...\", \"intro\": \"...\", \"sub1\": \"...\", \"texto1\": \"...\", \"sub2\": \"...\", \"texto2\": \"...\", \"sub3\": \"...\", \"texto3\": \"...\", \"texto_conclusao\": \"...\"}}"
            }]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        # Se v1beta falhar, tentamos v1 (Estável)
        url_v1 = url.replace("v1beta", "v1")
        response = requests.post(url_v1, json=payload)
        
    res_json = response.json()
    return json.loads(res_json['candidates'][0]['content']['parts'][0]['text'])

def executar():
    print("🚀 Iniciando Bot Diário de Notícias (Modo Direct Link)...")
    creds = renovar_token()
    service_blogger = build('blogger', 'v3', credentials=creds)

    # 1. Busca Notícia
    feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
    noticia = feed.entries[0]
    print(f"📰 Notícia: {noticia.title}")

    # 2. Gera Conteúdo (Usando a nova função REST)
    print("✍️ Gerando texto estruturado via REST...")
    dados = gerar_texto_rest(noticia.title)

    # 3. Preparar Imagens (Placeholder para garantir o post agora)
    dados['img_topo'] = "https://via.placeholder.com/1280x720.png?text=Noticia+Principal"
    dados['img_meio'] = "https://via.placeholder.com/1280x720.png?text=Analise+Detalhada"
    dados['assinatura'] = f"<hr><p style='text-align:right;'><i>Fonte: <a href='{noticia.link}'>G1 Política</a></i></p>"

    # 4. Montar e Publicar
    print("🏗️ Renderizando Template...")
    html_final = obter_esqueleto_html(dados)

    corpo_post = {
        'kind': 'blogger#post',
        'title': dados['titulo'],
        'content': html_final
    }
    
    service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
    print(f"✅ SUCESSO ABSOLUTO! Postado no Blogger.")

if __name__ == "__main__":
    executar()
