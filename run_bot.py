import os, time, io, feedparser
# Importa suas configurações personalizadas (WhatsApp, Shopee, Redes)
try:
    import configuracao
except ImportError:
    configuracao = None

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google import genai
from google.genai import types

# --- CONFIGURAÇÕES ---
BLOG_ID = "7605688984374445860"
client_gemini = genai.Client()

def limpar_markdown(texto):
    """Remove marcações como #, ** e ### para evitar sujeira no post"""
    texto = texto.replace('###', '👉').replace('##', '👉').replace('#', '👉')
    texto = texto.replace('**', '').replace('*', '•')
    return texto

def gerar_imagem_ia(titulo):
    print(f"🎨 Criando imagem 16:9 para: {titulo}")
    try:
        res = client_gemini.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=f"Professional photojournalism, wide angle, high quality, realistic: {titulo}",
            config=types.GenerateImageConfig(
                number_of_images=1, 
                aspect_ratio="16:9", 
                output_mime_type="image/png"
            )
        )
        if hasattr(res, 'generated_images'):
            return res.generated_images[0].image_bytes
        return res.image_bytes
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

    # Lendo o feed
    rss = feedparser.parse("https://g1.globo.com/rss/g1/")
    # Pegamos um item diferente a cada rodada baseado no tempo para evitar notícias repetidas
    index = int(time.time()) % 5 
    feed = rss.entries[index]
    titulo = feed.title
    print(f"📰 Notícia: {titulo}")
    
    # Gerar Texto com instruções para NÃO usar Markdown
    prompt = f"Aja como jornalista. Escreva uma notícia sobre: {titulo}. Link: {feed.link}. Não use negritos ou cerquilhas (#). Use parágrafos claros."
    resposta = client_gemini.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt
    )
    
    # Limpa o texto de marcações residuais e converte para HTML
    texto_limpo = limpar_markdown(resposta.text)
    texto_html = texto_limpo.replace('\n', '<br>')
    
    # Processo da Imagem
    img_data = gerar_imagem_ia(titulo)
    img_url = salvar_no_drive(drive, img_data, f"capa_{int(time.time())}.png") if img_data else ""

    # Recupera sua assinatura e banner do configuracao.py
    assinatura = getattr(configuracao, 'ASSINATURA_COMPLETA', "© Marco Daher 2026")

    html_final = f"""<div style='font-family:Arial; text-align:justify; line-height:1.6;'>
        <h1 style='text-align:center;'>{titulo}</h1>
        {"<img src='" + img_url + "' style='width:100%; border-radius:10px; margin-bottom:20px;'/>" if img_url else ""}
        <div>{texto_html}</div>
        <p style='margin-top:20px;'><i>Fonte: <a href='{feed.link}'>G1</a></i></p>
        <hr>
        <div style='text-align:center;'>
            {assinatura}
        </div>
    </div>"""

    try:
        blogger.posts().insert(blogId=BLOG_ID, body={
            "title": titulo, 
            "content": html_final,
            "status": "LIVE"
        }).execute()
        print("✅ SUCESSO TOTAL! Texto limpo, Assinatura recuperada e Imagem ok.")
    except Exception as e:
        print(f"❌ Erro ao postar: {e}")

if __name__ == "__main__":
    executar()
