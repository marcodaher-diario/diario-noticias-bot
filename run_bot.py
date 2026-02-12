import feedparser
import re
import os
import json
import time
import io
import requests
import random
import pytz
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai
from PIL import Image

# =============================
# CONFIGURAÇÕES BÁSICAS
# =============================
BLOG_ID = "7605688984374445860"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ARQUIVO_LOG = "posts_publicados.txt"
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/", "https://feeds.uol.com.br/home.xml",
    "https://rss.uol.com.br/feed/noticias.xml", "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://agenciabrasil.ebc.com.br/rss", "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.gazetadopovo.com.br/feed/rss/brasil.xml", "https://reporterbrasil.org.br/feed/",
    "https://www.cnnbrasil.com.br/feed/", "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
    "https://g1.globo.com/rss/g1/economia/"
]

try:
    from configuracoes import BLOCO_FIXO_FINAL
    from template_blog import obter_esqueleto_html
except:
    BLOCO_FIXO_FINAL = "<footer>Diário de Notícias</footer>"

# =============================
# FUNÇÕES DE APOIO
# =============================
def autenticar_google():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("Erro: 'token.json' não encontrado!")
    creds_data = json.load(open("token.json"))
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f: f.write(creds.to_json())
    return creds

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG): return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def definir_tema_por_horario():
    fuso = pytz.timezone('America/Sao_Paulo')
    hora = datetime.now(fuso).hour
    if 5 <= hora <= 11: return "Policial", "investigação, crime, polícia, operação"
    elif 12 <= hora <= 17: return "Economia", "mercado, inflação, dólar, economia"
    else: return "Política", "governo, congresso, stf, política"

# =============================
# GERAÇÃO DE IMAGENS (MODELO CORRIGIDO)
# =============================
def gerar_imagens_ia(client, titulo):
    arquivos = []
    prompt = f"Professional journalistic photography, 16:9 aspect ratio, high resolution: {titulo}"
    
    for i in range(1):
        nome_f = f"temp_img_{i}.png"
        try:
            # ADICIONADO 'models/' NO INÍCIO
            res = client.models.generate_content(model="models/imagen-3.0-generate-001", contents=[prompt])
            for part in res.parts:
                if part.inline_data:
                    img = Image.open(io.BytesIO(part.inline_data.data))
                    img.save(nome_f)
                    arquivos.append(nome_f)
                    break
        except Exception as e:
            print(f"⚠️ IA Imagem falhou, usando fallback: {e}")
            res_backup = requests.get(f"https://loremflickr.com/1280/720/news?lock={random.randint(1,999)}")
            with open(nome_f, "wb") as f: f.write(res_backup.content)
            arquivos.append(nome_f)
    return arquivos

# =============================
# FLUXO PRINCIPAL
# =============================
def executar():
    print(f"🚀 Iniciando Bot Diário de Notícias...")
    
    try:
        creds = autenticar_google()
        service_blogger = build("blogger", "v3", credentials=creds)
        service_drive = build("drive", "v3", credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'})

        tema, keywords = definir_tema_por_horario()
        print(f"🔍 Buscando notícias de {tema}...")
        
        # Sorteia um feed e tenta achar uma notícia nova
        feeds_embaralhados = RSS_FEEDS.copy()
        random.shuffle(feeds_embaralhados)
        
        noticia_selecionada = None
        for url in feeds_embaralhados:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not ja_publicado(entry.link):
                    noticia_selecionada = entry
                    break
            if noticia_selecionada: break
        
        if not noticia_selecionada:
            print("Nenhuma notícia nova encontrada.")
            return

        # GERAÇÃO DE TEXTO (MODELO CORRIGIDO)
        print(f"✍️ Gerando artigo sobre: {noticia_selecionada.title}")
        prompt_texto = (
            f"Escreva um artigo jornalístico profissional com 800 palavras. "
            f"Responda APENAS em JSON com as chaves: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao. "
            f"Tema: {noticia_selecionada.title}"
        )
        
        # ADICIONADO 'models/' NO INÍCIO
        res_ai = client.models.generate_content(model="models/gemini-1.5-flash", contents=prompt_texto)
        
        match = re.search(r'\{.*\}', res_ai.text, re.DOTALL)
        if not match: raise Exception("Falha ao extrair JSON da IA.")
        dados = json.loads(match.group(0))

        # IMAGENS
        imgs_locais = gerar_imagens_ia(client, dados['titulo'])
        links_drive = []
        for img_p in imgs_locais:
            media = MediaFileUpload(img_p, mimetype='image/png')
            file = service_drive.files().create(body={'name': img_p}, media_body=media, fields='id').execute()
            service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
            links_drive.append(f"https://drive.google.com/uc?export=view&id={file.get('id')}")

        # MONTAGEM (TRATAMENTO DE LARGURA)
        dados_final = {
            'titulo': dados.get('titulo', noticia_selecionada.title),
            'img_topo': links_drive[0] if links_drive else "",
            'img_meio': links_drive[0] if links_drive else "",
            'intro': str(dados.get('intro', '')).replace('\n', '<br/>'),
            'sub1': dados.get('sub1', 'Destaque'),
            'texto1': str(dados.get('texto1', '')).replace('\n', '<br/>'),
            'sub2': dados.get('sub2', 'Contexto'),
            'texto2': str(dados.get('texto2', '')).replace('\n', '<br/>'),
            'sub3': dados.get('sub3', 'Análise'),
            'texto3': str(dados.get('texto3', '')).replace('\n', '<br/>'),
            'texto_conclusao': str(dados.get('texto_conclusao', '')).replace('\n', '<br/>'),
            'assinatura': f"<br><b>Fonte:</b> {noticia_selecionada.link}<br><br>{BLOCO_FIXO_FINAL}"
        }

        html_conteudo = obter_esqueleto_html(dados_final)
        
        corpo = {
            "title": dados_final['titulo'].upper(),
            "content": html_conteudo,
            "labels": [tema, "Notícias"],
            "status": "LIVE"
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo).execute()
        registrar_publicacao(noticia_selecionada.link)
        print(f"✅ SUCESSO! Post publicado.")

    except Exception as e:
        print(f"💥 ERRO: {e}")

if __name__ == "__main__":
    executar()
