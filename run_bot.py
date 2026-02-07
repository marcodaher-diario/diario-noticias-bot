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
# Removi a lista rígida de SCOPES para evitar o erro de conflito
client_gemini = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
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
        print(f"❌ Erro na IA de imagem: {e}")
        return None

def salvar_no_drive(drive_service, img_bytes, nome):
    print(f"💾 Salvando imagem no Google Drive...")
    try:
        media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/png')
        file = drive_service.files().create(body={'name': nome}, media_body=media, fields='id').execute()
        file_id = file.get('id')
        drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception as e:
        print(f"❌ Erro ao salvar no Drive: {e}")
        return ""

# --- EXECUÇÃO ---
def executar():
    # Carrega as credenciais sem forçar scopes extras
    creds = Credentials.from_authorized_user_file("token.json")
    
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"❌ Erro ao atualizar acesso: {e}. Você pode precisar gerar o token.json novamente no PC.")
            return

    blogger = build("blogger", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    feeds = ["https://g1.globo.com/rss/g1/"]
    
    items = feedparser.parse(feeds[0]).entries[:1]
    for item in items:
        titulo = item.title
        print(f"📰 Processando: {titulo}")
        
        prompt = f"Escreva uma notícia curta e profissional sobre: {titulo}. Fonte: {item.link}"
        texto_gerado = client_gemini.models.generate_content(model="gemini-1.5-flash", contents=prompt).text
        texto_html = texto_gerado.replace('\n', '<br>')
        
        img_data = gerar_imagem_ia(titulo)
        img_url = salvar_no_drive(drive, img_data, f"img_{int(time.time())}.png") if img_data else ""

        html_final = f"""<div style='font-family:Arial;'>
            <h1 style='text-align:center;'>{titulo}</h1>
            <img src='{img_url}' style='width:100%; border-radius:8px;'/>
            <p>{texto_html}</p>
            {BLOCO_FIXO_FINAL}
        </div>"""

        blogger.posts().insert(blogId=BLOG_ID, body={"title": titulo, "content": html_final}).execute()
        print(f"✅ Sucesso total!")

if __name__ == "__main__":
    executar()
