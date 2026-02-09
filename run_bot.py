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
    """Gera o texto estruturado via chamada REST usando a rota estável v1"""
    # Mudança para v1 (estável) e modelo 'latest'
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    f"Com base na notícia '{titulo_noticia}', escreva um artigo analítico profundo. "
                    "Responda APENAS com um objeto JSON puro, sem markdown, usando estas chaves: "
                    "titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao."
                )
            }]
        }]
        # Removi o generationConfig para evitar o erro 400 na v1 caso o suporte seja instável
    }
    
    response = requests.post(url, json=payload)
    res_json = response.json()
    
    if "candidates" not in res_json:
        print(f"❌ Erro detalhado da API: {json.dumps(res_json, indent=2)}")
        raise Exception("Falha na comunicação com o Gemini.")
        
    texto_puro = res_json['candidates'][0]['content']['parts'][0]['text']
    
    # Limpeza extra caso o Gemini mande ```json ... ``` mesmo pedindo para não mandar
    if "```" in texto_puro:
        texto_puro = texto_puro.split("```json")[-1].split("```")[0].strip()
        
    return json.loads(texto_puro)

def executar():
    print("🚀 Iniciando Bot Diário de Notícias...")
    try:
        creds = renovar_token()
        service_blogger = build('blogger', 'v3', credentials=creds)

        # 1. Busca Notícia
        feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
        noticia = feed.entries[0]
        print(f"📰 Notícia: {noticia.title}")

        # 2. Gera Conteúdo
        print("✍️ Gerando texto estruturado...")
        dados = gerar_texto_rest(noticia.title)

        # 3. Preparar Campos do Template
        dados['img_topo'] = "https://via.placeholder.com/1280x720.png?text=Noticia+Principal"
        dados['img_meio'] = "https://via.placeholder.com/1280x720.png?text=Analise"
        dados['assinatura'] = f"<p style='text-align:right;'>Fonte: {noticia.link}</p>"

        # 4. Montar e Publicar
        print("🏗️ Renderizando Template...")
        html_final = obter_esqueleto_html(dados)

        corpo_post = {
            'kind': 'blogger#post',
            'title': dados['titulo'],
            'content': html_final
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO! Postado no Blogger.")
        
    except Exception as e:
        print(f"💥 Falha crítica no bot: {e}")

if __name__ == "__main__":
    executar()
