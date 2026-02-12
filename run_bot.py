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
import google.generativeai as google_ai # BIBLIOTECA ESTÁVEL
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
    if 5 <= hora <= 11: return "Policial", "crime, investigação, polícia"
    elif 12 <= hora <= 17: return "Economia", "mercado, economia, dólar"
    else: return "Política", "brasília, governo, política"

# =============================
# FLUXO PRINCIPAL
# =============================
def executar():
    print(f"🚀 Iniciando Bot Diário de Notícias...")
    
    try:
        # CONFIGURAÇÃO DA IA (MÉTODO 100% ESTÁVEL)
        google_ai.configure(api_key=GEMINI_API_KEY)
        model = google_ai.GenerativeModel('gemini-1.5-flash')

        creds = autenticar_google()
        service_blogger = build("blogger", "v3", credentials=creds)

        tema, keywords = definir_tema_por_horario()
        print(f"🔍 Buscando notícias de {tema}...")
        
        noticia_selecionada = None
        random.shuffle(RSS_FEEDS)
        for url in RSS_FEEDS:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not ja_publicado(entry.link):
                    noticia_selecionada = entry
                    break
            if noticia_selecionada: break
        
        if not noticia_selecionada:
            print("Nenhuma notícia nova encontrada.")
            return

        print(f"✍️ Gerando artigo sobre: {noticia_selecionada.title}")
        prompt_texto = (
            f"Escreva um artigo jornalístico profissional com 800 palavras. "
            f"Responda APENAS em JSON com as chaves: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao. "
            f"Tema: {noticia_selecionada.title}"
        )
        
        # Chamada direta que não dá 404
        response = model.generate_content(prompt_texto)
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if not match: raise Exception("IA não retornou um JSON válido.")
        dados = json.loads(match.group(0))

        # IMAGEM 16:9 (Usando LoremFlickr para estabilizar agora, depois ativamos o Imagen 3)
        img_url = f"https://loremflickr.com/1280/720/news?lock={random.randint(1,999)}"

        dados_final = {
            'titulo': dados.get('titulo', noticia_selecionada.title),
            'img_topo': img_url,
            'img_meio': img_url,
            'intro': str(dados.get('intro', '')).replace('\n', '<br/>'),
            'sub1': dados.get('sub1', 'Destaque'),
            'texto1': str(dados.get('texto1', '')).replace('\n', '<br/>'),
            'sub2': dados.get('sub2', 'Análise'),
            'texto2': str(dados.get('texto2', '')).replace('\n', '<br/>'),
            'sub3': dados.get('sub3', 'Contexto'),
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
        print(f"✅ SUCESSO! Post publicado no Blogger.")

    except Exception as e:
        print(f"💥 ERRO: {e}")

if __name__ == "__main__":
    executar()
