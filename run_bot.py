import os, time, io, feedparser
from datetime import datetime
import pytz 

# --- INTEGRAÇÃO COM SEU ARQUIVO DE CONFIGURAÇÕES ---
try:
    # Ajustado para o nome exato do seu arquivo no GitHub: configuracoes.py
    import configuracoes 
    ASSINATURA = configuracoes.BLOCO_FIXO_FINAL
except ImportError:
    ASSINATURA = "<p>© Marco Daher 2026</p>"

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google import genai
from google.genai import types

# --- CONFIGURAÇÕES GERAIS ---
BLOG_ID = "7605688984374445860"
client_gemini = genai.Client()

def definir_tema_por_horario():
    fuso = pytz.timezone('America/Sao_Paulo')
    hora = datetime.now(fuso).hour
    # Filtros baseados nos seus horários de preferência
    if 5 <= hora <= 11:
        return "Policial", "polícia, crime, prisão, operação policial, acidente, investigação, homicídio"
    elif 12 <= hora <= 16:
        return "Economia", "preços, inflação, emprego, mercado, salário, impostos, economia, INSS"
    else:
        return "Política", "governo, senado, congresso, leis, política, eleição, ministério, corrupção"

def limpar_estetica_texto(texto):
    """Substitui marcações de Markdown por símbolos limpos (setas e pontos)"""
    texto = texto.replace('###', '👉').replace('##', '👉').replace('#', '👉')
    texto = texto.replace('**', '').replace('* ', '• ')
    return texto

def gerar_imagem_ia(titulo, tema):
    print(f"🎨 Gerando imagem 16:9 para o tema {tema}")
    try:
        res = client_gemini.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=f"Professional editorial news photography, realistic, high quality, theme {tema}: {titulo}",
            config=types.GenerateImageConfig(aspect_ratio="16:9")
        )
        if hasattr(res, 'generated_images'):
            return res.generated_images[0].image_bytes
        return res.image_bytes
    except Exception as e:
        print(f"❌ Erro na imagem: {e}")
        return None

def salvar_no_drive(drive_service, img_bytes, nome):
    try:
        media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/png')
        file = drive_service.files().create(body={'name': nome}, media_body=media, fields='id').execute()
        file_id = file.get('id')
        drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except:
        return ""

def executar():
    creds = Credentials.from_authorized_user_file("token.json")
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    blogger = build("blogger", "v3", credentials=creds)
    drive = build("drive", "v3", credentials=creds)

    tema_nome, keywords = definir_tema_por_horario()
    print(f"⏰ Turno detectado: {tema_nome}")

    rss = feedparser.parse("https://g1.globo.com/rss/g1/")
    
    # Busca uma notícia que se encaixe no tema do horário
    noticia = None
    palavras = keywords.split(", ")
    for entry in rss.entries:
        conteudo = (entry.title + entry.summary).lower()
        if any(p in conteudo for p in palavras):
            noticia = entry
            break
    
    if not noticia:
        noticia = rss.entries[0]

    print(f"📰 Notícia selecionada: {noticia.title}")
    
    # Prompt editorial rigoroso
    prompt = (f"Aja como jornalista profissional. Escreva uma notícia completa em português sobre: {noticia.title}. "
              f"Foco total em {tema_nome}. Use parágrafos e pontos. "
              f"PROIBIDO usar o símbolo # ou asteriscos **.")
    
    resposta = client_gemini.models.generate_content(
        model="gemini-3-flash-preview", 
        contents=prompt
    )
    
    texto_limpo = limpar_estetica_texto(resposta.text)
    texto_html = texto_limpo.replace('\n', '<br>')
    
    img_data = gerar_imagem_ia(noticia.title, tema_nome)
    img_url = salvar_no_drive(drive, img_data, f"capa_{int(time.time())}.png") if img_data else ""

    # Montagem final com o BLOCO_FIXO_FINAL do seu configuracoes.py
    html_final = f"""<div style='font-family:Arial; text-align:justify;'>
        <h1 style='text-align:center;'>{noticia.title}</h1>
        {"<img src='" + img_url + "' style='width:100%; border-radius:10px; margin-bottom:20px;'/>" if img_url else ""}
        <div style='line-height:1.6;'>{texto_html}</div>
        <br><p><i>Fonte: <a href='{noticia.link}'>G1 Notícias</a></i></p>
        <div style='margin-top:30px;'>
            {ASSINATURA}
        </div>
    </div>"""

    try:
        blogger.posts().insert(blogId=BLOG_ID, body={
            "title": noticia.title, 
            "content": html_final,
            "status": "LIVE"
        }).execute()
        print(f"✅ Sucesso! Post de {tema_nome} publicado com assinatura e imagem.")
    except Exception as e:
        print(f"❌ Erro ao postar no Blogger: {e}")

if __name__ == "__main__":
    executar()
