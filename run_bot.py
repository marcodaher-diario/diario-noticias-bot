import os, time, re, io, feedparser
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google import genai
from google.genai import types

# --- CONFIGURAÇÕES ---
BLOG_ID = "7605688984374445860"
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Bloco final padrão caso não encontre o arquivo de configurações
BLOCO_FIXO_FINAL = "<p>© Marco Daher 2026</p>"

# --- FUNÇÕES DE APOIO ---
def gerar_imagem_ia(titulo):
    print(f"🎨 Criando imagem para: {titulo}")
    try:
        res = client_gemini.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=f"Professional editorial news photography, high quality, related to: {titulo}",
            config=types.GenerateImageConfig(
                number_of_images=1, 
                aspect_ratio="16:9", 
                output_mime_type="image/png"
            )
        )
        return res.generated_images[0].image_bytes
    except Exception as e:
        print(f"❌ Erro ao gerar imagem: {e}")
        return None

def salvar_no_drive(drive_service, img_bytes, nome):
    print(f"💾 Salvando imagem no Google Drive...")
    media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/png')
    file_metadata = {'name': nome}
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')
    # Torna a imagem pública para o Blogger conseguir exibir
    drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file_id}"

# --- EXECUÇÃO ---
def executar():
    # Carrega as credenciais do token.json que você subiu
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    
    blogger = build("blogger", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    # Feeds de notícias
    feeds = ["https://g1.globo.com/rss/g1/", "https://rss.uol.com.br/feed/noticias.xml"]
    
    for url in feeds:
        items = feedparser.parse(url).entries[:1] # Pega 1 notícia de cada feed para teste
        for item in items:
            titulo = item.title
            print(f"📰 Processando: {titulo}")
            
            prompt = f"Escreva uma notícia detalhada e profissional sobre: {titulo}. Fonte base: {item.link}. Use um tom jornalístico."
            texto_gerado = client_gemini.models.generate_content(model="gemini-1.5-flash", contents=prompt).text
            
            # Corrige as quebras de linha fora da f-string para evitar o erro anterior
            texto_html = texto_gerado.replace('\n', '<br>')
            
            # Gera a imagem 16:9
            img_data = gerar_imagem_ia(titulo)
            img_url = ""
            if img_data:
                img_url = salvar_no_drive(drive, img_data, f"noticia_{int(time.time())}.png")

            # Monta o post
            html_final = f"""<div style='font-family:Arial; text-align:justify;'>
                <h1 style='text-align:center;'>{titulo.upper()}</h1>
                <img src='{img_url}' style='width:100%; border-radius:8px; margin-bottom:20px;'/>
                <p>{texto_html}</p>
                <p><b>Fonte:</b> <a href='{item.link}'>Leia mais no original</a></p>
                <hr>
                {BLOCO_FIXO_FINAL}
            </div>"""

            blogger.posts().insert(blogId=BLOG_ID, body={
                "title": titulo,
                "content": html_final,
                "status": "LIVE"
            }).execute()
            
            print(f"✅ Postado com sucesso!")
            time.sleep(5)

if __name__ == "__main__":
    executar()
