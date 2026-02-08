import os, time, io, feedparser, random, json, re
from datetime import datetime
import pytz
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google import genai
from google.genai import types

# --- IMPORTAÇÃO DE MÓDULOS LOCAIS ---
try:
    from template_blog import obter_esqueleto_html
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError as e:
    print(f"❌ Erro ao importar arquivos locais: {e}")
    BLOCO_FIXO_FINAL = "© Marco Daher 2026"

# --- CONFIGURAÇÕES ---
BLOG_ID = "7605688984374445860"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client_gemini = genai.Client(api_key=GEMINI_API_KEY)

# Sua lista completa de fontes restaurada
RSS_FEEDS = [
   "https://g1.globo.com/rss/g1/",
   "https://feeds.uol.com.br/home.xml",
   "https://rss.uol.com.br/feed/noticias.xml",
   "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
   "https://agenciabrasil.ebc.com.br/rss",
   "https://feeds.bbci.co.uk/portuguese/rss.xml",
   "https://www.gazetadopovo.com.br/feed/rss/brasil.xml",
   "https://reporterbrasil.org.br/feed/",
   "https://www.cnnbrasil.com.br/feed/",
   "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
   "https://g1.globo.com/rss/g1/economia/"
]

def definir_tema_por_horario():
    fuso = pytz.timezone('America/Sao_Paulo')
    hora = datetime.now(fuso).hour
    if 5 <= hora <= 11:
        return "Policial", "polícia, crime, prisão, investigação, segurança, homicídio, delegacia"
    elif 12 <= hora <= 16:
        return "Economia", "preços, inflação, mercado, emprego, impostos, salário, inss, dólar"
    else:
        return "Política", "governo, congresso, judiciário, leis, eleições, corrupção, ministério"

def buscar_noticia_por_tema(tema, keywords):
    print(f"🔍 Pesquisando notícias de {tema} em múltiplos portais...")
    noticias_candidatas = []
    palavras_chave = keywords.split(", ")
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                texto_busca = (entry.title + " " + entry.get('summary', '')).lower()
                if any(k in texto_busca for k in palavras_chave):
                    noticias_candidatas.append(entry)
        except: continue
    
    if noticias_candidatas:
        return random.choice(noticias_candidatas)
    # Se não achar nada específico, pega a mais recente do primeiro feed
    return feedparser.parse(RSS_FEEDS[0]).entries[0]

def gerar_imagem_ia(titulo, contexto, sufixo):
    print(f"🎨 Gerando imagem IA 16:9 ({sufixo})...")
    try:
        res = client_gemini.models.generate_image(
            model="imagen-3.0-generate-001",
            prompt=f"Professional news photojournalism, realistic, cinematic lighting, 8k. Scene: {titulo}. Focus on: {contexto}",
            config=types.GenerateImageConfig(aspect_ratio="16:9")
        )
        return res.generated_images[0].image_bytes if hasattr(res, 'generated_images') else res.image_bytes
    except Exception as e:
        print(f"❌ Erro na imagem {sufixo}: {e}")
        return None

def salvar_no_drive(drive_service, img_bytes, nome):
    if not img_bytes: return ""
    try:
        media = MediaIoBaseUpload(io.BytesIO(img_bytes), mimetype='image/png')
        file = drive_service.files().create(body={'name': nome}, media_body=media, fields='id').execute()
        file_id = file.get('id')
        drive_service.permissions().create(fileId=file_id, body={'type': 'anyone', 'role': 'viewer'}).execute()
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except: return ""

def renovar_token():
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive"])
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

def executar():
    tema_nome, keywords = definir_tema_por_horario()
    noticia = buscar_noticia_por_tema(tema_nome, keywords)
    print(f"📰 Fonte encontrada: {noticia.title}")

    # PROMPT ÉTICO ANALÍTICO (Foco 700-900 palavras)
    prompt_jornalistico = (
        f"Você é um Jornalista Analítico Sênior. Escreva uma postagem PROFUNDA (700 a 900 palavras) sobre: {noticia.title}.\n"
        f"Use o fato da fonte apenas como base: {noticia.link}\n"
        "REGRAS:\n"
        "1. Tom neutro, imparcial, focado em causas e consequências.\n"
        "2. Ignore referências a vídeos. Escreva um artigo completo.\n"
        "3. PROIBIDO Markdown (# ou **). Proibido plágio.\n"
        "4. Responda APENAS em JSON com as chaves: 'intro', 'sub1', 'texto1', 'sub2', 'texto2', 'sub3', 'texto3', 'texto_conclusao'.\n"
        "5. Desenvolva cada parágrafo com riqueza de detalhes."
    )

    try:
        response = client_gemini.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt_jornalistico,
            config={'response_mime_type': 'application/json'}
        )
        conteudo = json.loads(response.text)
        if isinstance(conteudo, list): conteudo = conteudo[0]
    except Exception as e:
        print(f"❌ Erro na IA: {e}")
        return

    creds = renovar_token()
    drive_service = build("drive", "v3", credentials=creds)
    blogger_service = build("blogger", "v3", credentials=creds)

    # Imagens Contextualizadas
    img_topo = gerar_imagem_ia(noticia.title, "Cenário principal do fato", "topo")
    img_meio = gerar_imagem_ia(noticia.title, "Impacto social ou detalhe analítico", "meio")
    
    url_topo = salvar_no_drive(drive_service, img_topo, f"topo_{int(time.time())}.png")
    url_meio = salvar_no_drive(drive_service, img_meio, f"meio_{int(time.time())}.png")

    # Montagem no Template
    dados_post = {
        'titulo': noticia.title,
        'img_topo': url_topo,
        'img_meio': url_meio,
        'intro': conteudo.get('intro', '').replace('\n', '<br/>'),
        'sub1': conteudo.get('sub1', '').upper(),
        'texto1': conteudo.get('texto1', '').replace('\n', '<br/>'),
        'sub2': conteudo.get('sub2', '').upper(),
        'texto2': conteudo.get('texto2', '').replace('\n', '<br/>'),
        'sub3': conteudo.get('sub3', '').upper(),
        'texto3': conteudo.get('texto3', '').replace('\n', '<br/>'),
        'texto_conclusao': f"{conteudo.get('texto_conclusao', '')}<br/><br/><b>Referências e Fontes:</b><br/>• {noticia.link}".replace('\n', '<br/>'),
        'assinatura': BLOCO_FIXO_FINAL
    }

    html_final = obter_esqueleto_html(dados_post)

    corpo_blogger = {
        "title": noticia.title,
        "content": html_final,
        "labels": [tema_nome, "Notícias Brasil", "Análise Jornalística"],
        "status": "LIVE"
    }

    try:
        blogger_service.posts().insert(blogId=BLOG_ID, body=corpo_blogger).execute()
        print(f"✅ SUCESSO! Post de {tema_nome} publicado via Multi-RSS.")
    except Exception as e:
        print(f"❌ Erro Blogger: {e}")

if __name__ == "__main__":
    executar()
