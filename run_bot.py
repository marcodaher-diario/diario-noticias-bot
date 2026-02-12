import os
import json
import feedparser
import time
import re
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
from google.genai import types
from PIL import Image

# --- CONFIGURAÇÕES E FONTES (PONTO 1) ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "7605688984374445860" 
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
    from template_blog import obter_esqueleto_html
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    print("❌ Erro ao importar arquivos locais.")
    raise

# --- LÓGICA DE AGENDA (PONTO 1) ---
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
    print(f"🔍 [PONTO 1] Pesquisando {tema} nos portais...")
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
    return random.choice(noticias_candidatas) if noticias_candidatas else feedparser.parse(RSS_FEEDS[0]).entries[0]

# --- TAGS SEO ORIGINAIS (PONTO 4) ---
def gerar_tags_seo(titulo, texto):
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos"]
    conteudo = f"{titulo} {texto[:100]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    tags_fixas = ["Notícias", "Diário de Notícias", "Marco Daher"]
    for tf in tags_fixas:
        if tf not in tags: tags.append(tf)
    resultado = []
    tamanho_atual = 0
    for tag in tags:
        if tamanho_atual + len(tag) + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += len(tag) + 2
        else: break
    return resultado

# --- IMAGENS HÍBRIDAS (PONTO 3) ---
def buscar_imagem_reserva(index):
    print(f"📸 [PONTO 3] Buscando imagem real/banco para reserva...")
    url = f"https://loremflickr.com/1280/720/news,politics/all?lock={index + int(time.time()) % 100}"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            with open(f"imagem_{index}.png", "wb") as f: f.write(res.content)
            return True
    except: return False

def gerar_imagens(client, titulo_post):
    links_locais = []
    # Modelo específico para imagem conforme documentação
    model_nome = "imagen-3.0-generate-001"
    prompts = [
        f"Professional photojournalism, 16:9, realistic: {titulo_post}",
        f"News scene photography, 16:9, cinematic lighting: {titulo_post}"
    ]
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        sucesso = False
        try:
            print(f"🎨 [PONTO 3] Gerando imagem IA {i+1}...")
            response = client.models.generate_content(model=model_nome, contents=[p])
            for part in response.parts:
                if part.inline_data:
                    img = Image.open(io.BytesIO(part.inline_data.data))
                    img.save(nome_arq)
                    links_locais.append(nome_arq)
                    sucesso = True
                    break
        except: pass
        if not sucesso:
            if buscar_imagem_reserva(i): links_locais.append(nome_arq)
    return links_locais

# --- CORE ---
def executar():
    print(f"🚀 Iniciando Bot - Blog ID: {BLOG_ID}")
    try:
        creds = Credentials.from_authorized_user_info(json.load(open("token.json")), SCOPES)
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open("token.json", "w") as f: f.write(creds.to_json())
            
        service_blogger = build('blogger', 'v3', credentials=creds)
        service_drive = build('drive', 'v3', credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'})

        # 1. RSS POR HORÁRIO
        tema, keywords = definir_tema_por_horario()
        noticia = buscar_noticia_por_tema(tema, keywords)
        
        # 2. TEXTO AUTORAL (NOME DO MODELO ATUALIZADO)
        print(f"✍️ [PONTO 2] Gerando artigo autoral sobre: {noticia.title}")
        prompt_txt = f"Escreva um artigo jornalístico autoral, sem plágio, entre 700 e 900 palavras. Responda em JSON: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao, links_pesquisa. Tema: {noticia.title}"
        
        # Usando o nome de modelo estável da biblioteca genai
        res_txt = client.models.generate_content(
            model="gemini-1.5-flash-002", 
            contents=prompt_txt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # Garante a extração correta do JSON
        dados = json.loads(re.search(r'\{.*\}', res_txt.text, re.DOTALL).group(0))

        # 3. IMAGENS REALISTAS 16:9 (Mantido seu código de upload)
        arquivos = gerar_imagens(client, dados['titulo'])
        links_drive = []
        for f in arquivos:
            media = MediaFileUpload(f, mimetype='image/png')
            file = service_drive.files().create(body={'name': f}, media_body=media, fields='id').execute()
            service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
            links_drive.append(f"https://drive.google.com/uc?export=view&id={file.get('id')}")

        # --- FUSÃO COM A LÓGICA DO EMAGRECER (RESOLVE LARGURA E POSTAGEM) ---
        
        # Limpeza de texto para não estufar a largura (O SEGREDO DO EMAGRECER)
        dados_post = {
            'titulo': dados['titulo'],
            'img_topo': links_drive[0] if len(links_drive) > 0 else "",
            'img_meio': links_drive[1] if len(links_drive) > 1 else (links_drive[0] if len(links_drive) > 0 else ""),
            'intro': dados.get('intro', '').replace('\n', '<br/>'),
            'sub1': dados.get('sub1', 'Destaque'),
            'texto1': dados.get('texto1', '').replace('\n', '<br/>'),
            'sub2': dados.get('sub2', 'Saiba Mais'),
            'texto2': dados.get('texto2', '').replace('\n', '<br/>'),
            'sub3': dados.get('sub3', 'Dica Prática'),
            'texto3': dados.get('texto3', '').replace('\n', '<br/>'),
            'texto_conclusao': dados.get('texto_conclusao', '').replace('\n', '<br/>'),
            'assinatura': f"<br><b>Fontes:</b> {dados.get('links_pesquisa', 'G1')}<br><br>{BLOCO_FIXO_FINAL}"
        }

        html_final = obter_esqueleto_html(dados_post)
        tags_geradas = gerar_tags_seo(dados['titulo'], f"{dados['intro']} {dados['texto1']}")

        # PUBLICAÇÃO COM ESTRUTURA DO EMAGRECER
        corpo_post = {
            "kind": "blogger#post",
            "title": dados['titulo'].upper(),
            "content": html_final,
            "labels": tags_geradas,
            "status": "LIVE"
        }
        
        service_blogger.posts().insert(
            blogId=BLOG_ID, 
            isDraft=False, 
            body=corpo_post
        ).execute()
        
        print(f"🎉 [FIM] Post publicado com sucesso! Largura protegida e IA ativa.")

    except Exception as e:
        print(f"💥 Erro: {e}")

if __name__ == "__main__":
    executar()
