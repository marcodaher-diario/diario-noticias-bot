import os, time, re, io, feedparser
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google import genai
from google.genai import types

# --- CONFIGURAÇÕES ---
BLOG_ID = "7605688984374445860"
client_gemini = genai.Client() # Pega a chave do ambiente automaticamente
BLOCO_FIXO_FINAL = "<p>© Marco Daher 2026</p>"

def gerar_imagem_ia(titulo):
    print(f"🎨 Criando imagem 16:9 para: {titulo}")
    try:
        # CORREÇÃO: O comando correto na versão 1.0.0+ é client.models.imagen.generate_image
        res = client_gemini.models.imagen.generate_image(
            model="imagen-3.0-generate-001",
            prompt=f"Professional photojournalism, wide angle, high quality, realistic: {titulo}",
            config=types.GenerateImageConfig(
                number_of_images=1, 
                aspect_ratio="16:9", 
                output_mime_type="image/png"
            )
        )
        return res.generated_images[0].image_bytes
    except Exception as e:
        print(f"❌ Erro na IA de imagem: {e}")
        return None

def salvar_no_drive(drive_service, img_bytes, nome):
    print(f"💾 Gravando no Google Drive...")
    try:
        media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/png')
        file_metadata = {'name': nome}
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')
        # Torna visível para o blog
        drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception as e:
        print(f"❌ Erro Drive: {e}")
        return ""

def executar():
    creds = Credentials.from_authorized_user_file("token.json")
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    blogger = build("blogger", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    feed = feedparser.parse("https://g1.globo.com/rss/g1/").entries[0]
    titulo = feed.title
    print(f"📰 Notícia: {titulo}")
    
    # Gerar Texto
    prompt = f"Escreva uma notícia completa e profissional: {titulo}. Link base: {feed.link}"
    resposta = client_gemini.models.generate_content(
        model="gemini-3-flash-preview" # Usando a versão mais estável/recente
        contents=prompt
    )
    
    texto_html = resposta.text.replace('\n', '<br>')
    
    # Gerar Imagem
    img_data = gerar_imagem_ia(titulo)
    img_url = salvar_no_drive(drive, img_data, f"capa_{int(time.time())}.png") if img_data else ""

    html_final = f"""<div style='font-family:Arial; text-align:justify;'>
        <h1 style='text-align:center;'>{titulo}</h1>
        <img src='{img_url}' style='width:100%; border-radius:10px; margin-bottom:20px;'/>
        <div style='line-height:1.6;'>{texto_html}</div>
        <p style='margin-top:20px;'><i>Fonte: <a href='{feed.link}'>G1</a></i></p>
        <hr>
        {BLOCO_FIXO_FINAL}
    </div>"""

    # Publicar
    try:
        blogger.posts().insert(blogId=BLOG_ID, body={
            "title": titulo, 
            "content": html_final,
            "status": "LIVE"
        }).execute()
        print("✅ SUCESSO! Confira seu blog.")
    except Exception as e:
        print(f"❌ Erro ao postar no Blogger: {e}")

if __name__ == "__main__":
    executar()
