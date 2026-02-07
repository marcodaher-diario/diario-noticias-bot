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

try:
    from configuracoes import BLOCO_FIXO_FINAL
except:
    BLOCO_FIXO_FINAL = "<p>© Marco Daher 2026</p>"

# --- FUNÇÕES DE APOIO ---
def gerar_imagem_ia(titulo):
    print(f"🎨 Criando imagem para: {titulo}")
    try:
        res = client_gemini.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=f"Professional editorial news photography, 16:9 aspect ratio, high quality, related to: {titulo}",
            config=types.GenerateImageConfig(number_of_images=1, aspect_ratio="16:9", output_mime_type="image/png")
        )
        return res.generated_images[0].image_bytes
    except: return None

def salvar_no_drive(drive_service, img_bytes, nome):
    media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/png')
    file = drive_service.files().create(body={'name': nome}, media_body=media, fields='id').execute()
    file_id = file.get('id')
    drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file_id}"

# --- EXECUÇÃO ---
def executar():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if creds.expired and creds.refresh_token: creds.refresh(Request())
    
    blogger = build("blogger", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    feeds = ["https://g1.globo.com/rss/g1/", "https://rss.uol.com.br/feed/noticias.xml"]
    
    for url in feeds:
        items = feedparser.parse(url).entries[:2] # 2 por feed para testar
        for item in items:
            titulo = item.title
            prompt = f"Aja como um jornalista. Escreva uma notícia autoral de 500 palavras sobre: {titulo}. Fonte base: {item.link}"
            texto = client_gemini.models.generate_content(model="gemini-1.5-flash", contents=prompt).text
            
            img_data = gerar_imagem_ia(titulo)
            img_url = salvar_no_drive(drive, img_data, f"capa_{int(time.time())}.png") if img_data else ""

            html = f"""<div style='font-family:Arial; text-align:justify;'>
                <h1 style='text-align:center;'>{titulo.upper()}</h1>
                <img src='{img_url}' style='width:100%; border-radius:8px;'/>
                <p>{texto.replace('\n', '<br>')}</p>
                <p><b>Fontes:</b> <a href='{item.link}'>{item.link}</a></p>
                {BLOCO_FIXO_FINAL}</div>"""

            blogger.posts().insert(blogId=BLOG_ID, body={"title": titulo, "content": html, "status": "LIVE"}).execute()
            print(f"✅ Postado: {titulo}")
            time.sleep(10)

if __name__ == "__main__": executar()
