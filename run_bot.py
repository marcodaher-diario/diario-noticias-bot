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

# Tentativa de importar configurações externas
try:
    from configuracoes import BLOCO_FIXO_FINAL
    from template_blog import obter_esqueleto_html
except ImportError:
    BLOCO_FIXO_FINAL = "<br><p align='center'>© 2026 Diário de Notícias - Todos os direitos reservados.</p>"
    def obter_esqueleto_html(d):
        return f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: auto;">
            <img src="{d['img_topo']}" style="width: 100%; border-radius: 8px;" />
            <p>{d['intro']}</p>
            <h2>{d['sub1']}</h2>
            <p>{d['texto1']}</p>
            <img src="{d['img_meio']}" style="width: 100%; border-radius: 8px;" />
            <h2>{d['sub2']}</h2>
            <p>{d['texto2']}</p>
            <h2>{d['sub3']}</h2>
            <p>{d['texto3']}</p>
            <hr>
            <p><i>{d['texto_conclusao']}</i></p>
            {d['assinatura']}
        </div>
        """

# =============================
# FUNÇÕES DE APOIO
# =============================
def autenticar_google():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("Erro: 'token.json' não encontrado! Certifique-se de que o arquivo token.json está na mesma pasta.")
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
    if 5 <= hora <= 11: 
        return "Policial", "notícias policiais, investigação, segurança pública"
    elif 12 <= hora <= 17: 
        return "Economia", "mercado financeiro, pib, economia brasileira, investimentos"
    else: 
        return "Política", "brasília, governo federal, congresso, decisões stf"

# =============================
# GERAÇÃO DE IMAGEM IA (NANO BANANA / IMAGEN 3)
# =============================
def gerar_imagem_ia(client, titulo):
    nome_f = "thumb_gerada.png"
    # Prompt respeitando a regra de 16:9 das suas instruções
    prompt_img = f"Professional journalistic photography, realistic style, 16:9 aspect ratio, high resolution, news thumbnail: {titulo}"
    
    try:
        print(f"📸 Gerando imagem IA para: {titulo}")
        # Usando o modelo genérico para evitar erro de versão
        res = client.models.generate_content(
            model="gemini-2.0-flash", # Modelo multimodal que gera imagens no 2026
            contents=[prompt_img]
        )
        for part in res.parts:
            if part.inline_data:
                img = Image.open(io.BytesIO(part.inline_data.data))
                img.save(nome_f)
                return nome_f
    except Exception as e:
        print(f"⚠️ IA falhou na imagem: {e}. Usando banco de imagens.")
        res_backup = requests.get(f"https://loremflickr.com/1280/720/news?lock={random.randint(1,999)}")
        with open(nome_f, "wb") as f: f.write(res_backup.content)
        return nome_f

# =============================
# EXECUÇÃO DO BOT
# =============================
def executar():
    print(f"🚀 Iniciando Bot Diário de Notícias...")
    
    try:
        # 1. Autenticação e Cliente IA
        creds = autenticar_google()
        service_blogger = build("blogger", "v3", credentials=creds)
        service_drive = build("drive", "v3", credentials=creds)
        
        # IMPORTANTE: Usando a versão v1beta que é a mais estável para modelos flash em contas pessoais
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1beta'})

        # 2. Busca de Notícia
        tema, keywords = definir_tema_por_horario()
        print(f"🔍 Tema do momento: {tema}")
        
        noticia_selecionada = None
        feeds_misturados = RSS_FEEDS.copy()
        random.shuffle(feeds_misturados)
        
        for url in feeds_misturados:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if not ja_publicado(entry.link):
                    noticia_selecionada = entry
                    break
            if noticia_selecionada: break
        
        if not noticia_selecionada:
            print("Nenhuma notícia nova encontrada em nenhum feed.")
            return

        # 3. Geração de Texto
        print(f"✍️ Notícia base: {noticia_selecionada.title}")
        prompt_texto = (
            f"Escreva um artigo jornalístico profissional, autoral e detalhado com aproximadamente 800 palavras. "
            f"Use um tom sério e informativo. O texto deve ser dividido em introdução, três subtítulos e uma conclusão analítica. "
            f"Retorne OBRIGATORIAMENTE um JSON puro com estas chaves exatas: "
            f"titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao. "
            f"Foco na notícia: {noticia_selecionada.title}"
        )
        
        # Chamada ao modelo com o nome completo exigido pela v1beta
        response = client.models.generate_content(
            model="models/gemini-1.5-flash", 
            contents=prompt_texto
        )
        
        # Limpeza do JSON (a IA às vezes coloca ```json ... ```)
        texto_limpo = response.text.replace('```json', '').replace('```', '').strip()
        match = re.search(r'\{.*\}', texto_limpo, re.DOTALL)
        if not match:
            raise Exception("A IA não retornou um formato JSON válido.")
        
        dados = json.loads(match.group(0))

        # 4. Geração de Imagem e Upload para Drive
        img_local = gerar_imagem_ia(client, dados['titulo'])
        
        media = MediaFileUpload(img_local, mimetype='image/png')
        file_drive = service_drive.files().create(
            body={'name': f"thumb_{int(time.time())}.png"}, 
            media_body=media, 
            fields='id'
        ).execute()
        
        file_id = file_drive.get('id')
        service_drive.permissions().create(
            fileId=file_id, 
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        img_url_final = f"https://drive.google.com/uc?export=view&id={file_id}"

        # 5. Montagem do HTML Final
        dados_final = {
            'titulo': dados.get('titulo', noticia_selecionada.title).upper(),
            'img_topo': img_url_final,
            'img_meio': img_url_final,
            'intro': str(dados.get('intro', '')).replace('\n', '<br/>'),
            'sub1': dados.get('sub1', 'DETALHES DA OPERAÇÃO'),
            'texto1': str(dados.get('texto1', '')).replace('\n', '<br/>'),
            'sub2': dados.get('sub2', 'ANÁLISE DO CENÁRIO'),
            'texto2': str(dados.get('texto2', '')).replace('\n', '<br/>'),
            'sub3': dados.get('sub3', 'IMPACTOS E DESDOBRAMENTOS'),
            'texto3': str(dados.get('texto3', '')).replace('\n', '<br/>'),
            'texto_conclusao': str(dados.get('texto_conclusao', '')).replace('\n', '<br/>'),
            'assinatura': f"<br><br><b>Fonte original:</b> <a href='{noticia_selecionada.link}'>{noticia_selecionada.link}</a><br><br>{BLOCO_FIXO_FINAL}"
        }

        conteudo_blogger = obter_esqueleto_html(dados_final)

        # 6. Publicação no Blogger
        post_body = {
            "title": dados_final['titulo'],
            "content": conteudo_blogger,
            "labels": [tema, "Brasil", "Notícias Atualizadas"],
            "status": "LIVE"
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=post_body).execute()
        
        # Finalização
        registrar_publicacao(noticia_selecionada.link)
        if os.path.exists(img_local): os.remove(img_local)
        
        print(f"✅ SUCESSO ABSOLUTO! Artigo publicado: {dados_final['titulo']}")

    except Exception as e:
        print(f"💥 ERRO CRÍTICO NO SISTEMA: {str(e)}")

if __name__ == "__main__":
    executar()
