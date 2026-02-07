import os, time, re, io, feedparser
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google import genai
from google.genai import types

# --- CONFIGURAÇÕES ---
BLOG_ID = "7605688984374445860"
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
BLOCO_FIXO_FINAL = "<p>© Marco Daher 2026</p>"

def gerar_imagem_ia(titulo):
    print(f"🎨 Criando imagem 16:9 para: {titulo}")
    try:
        # Usando o nome correto do modelo para esta biblioteca
        res = client_gemini.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=f"Professional editorial news photography, high quality, realistic, related to: {titulo}",
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
    print(f"💾 Salvando no Drive...")
    try:
        media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/png')
        file = drive_service.files().create(body={'name': nome}, media_body=media, fields='id').execute()
        file_id = file.get('id')
        drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception as e:
        print(f"❌ Erro Drive: {e}")
        return ""

def executar():
    # Carrega as credenciais
    creds = Credentials.from_authorized_user_file("token.json")
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    blogger = build("blogger", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    # Pegando apenas a primeira notícia para testar se vai funcionar tudo
    feed = feedparser.parse("https://g1.globo.com/rss/g1/").entries[0]
    titulo = feed.title
    print(f"📰 Notícia encontrada: {titulo}")
    
    # AJUSTE AQUI: O modelo precisa ser referenciado assim na nova SDK
    prompt = f"Aja como um jornalista. Escreva uma notícia sobre: {titulo}. Fonte: {feed.link}"
    resposta = client_gemini.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
    
    texto_html = resposta.text.replace('\n', '<br>')
    
    img_data = gerar_imagem_ia(titulo)
    img_url = salvar_no_drive(drive, img_data, f"capa_{int(time.time())}.png") if img_data else ""

    html_final = f"""<div style='font-family:Arial; text-align:justify;'>
        <h1 style='text-align:center;'>{titulo}</h1>
        <img src='{img_url}' style='width:100%; border-radius:10px; margin:20px 0;'/>
        <p>{texto_html}</p>
        <hr>
        {BLOCO_FIXO_FINAL}
    </div>"""

    blogger.posts().insert(blogId=BLOG_ID, body={
        "title": titulo, 
        "content": html_final,
        "status": "LIVE"
    }).execute()
    
    print("✅ PROCESSO FINALIZADO COM SUCESSO!")

if __name__ == "__main__":
    executar()
