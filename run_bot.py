import os
import json
import feedparser
import time
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai
from google.genai import types
import datetime
import pytz

# Configuração de Importação do seu Template
try:
    from template_blog import obter_esqueleto_html
except ImportError:
    # Caso o arquivo esteja com 't' minúsculo no GitHub
    from template_blog import obter_esqueleto_html

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "3884849132228514800" # ID do Diário de Notícias

# Escopos EXATAMENTE iguais ao seu token.json
SCOPES = [
    "https://www.googleapis.com/auth/blogger",
    "https://www.googleapis.com/auth/drive.file"
]

# --- FUNÇÕES DE AUTENTICAÇÃO ---
def renovar_token():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("O arquivo token.json não foi encontrado!")
    
    with open("token.json", "r") as f:
        info = json.load(f)
    
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

# --- FUNÇÕES DE IMAGEM E DRIVE ---
def upload_para_drive(service_drive, caminho_arquivo, nome_arquivo):
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    file = service_drive.files().create(body=file_metadata, media_body=media, fields='id, webContentLink').execute()
    
    # Torna a imagem pública para o Blogger conseguir ler
    service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    
    # Retorna o link direto da imagem
    return f"https://lh3.googleusercontent.com/u/0/d/{file.get('id')}"

def gerar_imagens_ia(titulo_noticia):
    client = genai.Client(api_key=GEMINI_API_KEY)
    imagens_links = []
    
    prompts = [
        f"Crie uma imagem cinematográfica e realista para o topo de uma notícia sobre: {titulo_noticia}. Estilo fotojornalismo profissional, 16:9.",
        f"Crie uma ilustração ou foto detalhada que complemente o contexto de: {titulo_noticia}. Estilo moderno, 16:9."
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"img_{i}.png"
        response = client.models.generate_images(
            model='imagen-3.0-generate-002',
            prompt=p,
            config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
        )
        for j, img in enumerate(response.generated_images):
            img.image.save(nome_arq)
            imagens_links.append(nome_arq)
            
    return imagens_links

# --- NÚCLEO DO BOT ---
def executar():
    print("🚀 Iniciando Bot Diário de Notícias...")
    creds = renovar_token()
    service_blogger = build('blogger', 'v3', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)
    client_gemini = genai.Client(api_key=GEMINI_API_KEY)

    # 1. Busca Notícia (RSS G1 como exemplo)
    feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
    if not feed.entries:
        print("Nenhuma notícia encontrada.")
        return
    
    noticia = feed.entries[0]
    titulo = noticia.title
    link_original = noticia.link

    # 2. IA gera o texto analítico (800 palavras)
    prompt_texto = f"""
    Escreva um artigo de opinião e análise profunda sobre a notícia: '{titulo}'.
    O texto deve ter entre 700 a 900 palavras. 
    Use subtítulos (H2), parágrafos claros e uma conclusão forte.
    Fale sobre os impactos disso para o Brasil e o cenário futuro.
    Retorne apenas o corpo do texto em HTML (sem <html> ou <body>).
    """
    response_texto = client_gemini.models.generate_content(model="gemini-1.5-flash-002", contents=prompt_texto)
    texto_analitico = response_texto.text

    # 3. Gerar e fazer Upload das Imagens
    arquivos_fotos = gerar_imagens_ia(titulo)
    links_drive = []
    for arq in arquivos_fotos:
        link = upload_para_drive(service_drive, arq, arq)
        links_drive.append(link)

    # 4. Montar HTML final usando seu Template
    html_final = obter_esqueleto_html(
        titulo=titulo,
        corpo_texto=texto_analitico,
        img_topo=links_drive[0],
        img_corpo=links_drive[1] if len(links_drive) > 1 else links_drive[0],
        fonte_link=link_original
    )

    # 5. Publicar no Blogger
    corpo_post = {
        'kind': 'blogger#post',
        'title': titulo,
        'content': html_final
    }
    service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
    print(f"✅ Postado com sucesso: {titulo}")

if __name__ == "__main__":
    executar()
