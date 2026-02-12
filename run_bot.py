import os
import json
import feedparser
import time
import re
import io
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai
from google.genai import types
from PIL import Image

# --- IMPORTAÇÕES LOCAIS ---
try:
    from template_blog import obter_esqueleto_html
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    print("❌ Erro ao importar arquivos de suporte.")
    raise

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "7605688984374445860" 
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

def renovar_token():
    if not os.path.exists("token.json"): raise FileNotFoundError("token.json ausente!")
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f: f.write(creds.to_json())
    return creds

def buscar_imagem_banco_real(keyword, index):
    """ Busca imagens reais e gratuitas no Unsplash (sem precisar de API Key) """
    print(f"🔍 Buscando imagem real para: {keyword}...")
    # Usamos o Source do Unsplash que permite buscar por termos específicos
    temas = "politics,brazil,government,news"
    url = f"https://source.unsplash.com/1280x720/?{temas},{keyword.replace(' ', ',')}&sig={index}"
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            with open(f"imagem_{index}.png", 'wb') as f:
                f.write(response.content)
            return True
    except Exception as e:
        print(f"⚠️ Falha ao buscar imagem real: {e}")
    return False

def gerar_imagens_ia_ou_real(client, titulo_post):
    links_locais = []
    # Prompts para a IA
    prompts = [
        f"Realistic news photo, high quality, 16:9: {titulo_post}",
        f"Conceptual political photography, cinematic, 16:9: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        sucesso = False
        
        # PASSO 1: Tenta Gerar com IA (Plano A)
        try:
            print(f"🎨 Gerando imagem {i+1}/2 via IA...")
            res = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=p
            )
            image_parts = [part for part in res.parts if part.inline_data]
            if image_parts:
                img = Image.open(io.BytesIO(image_parts[0].inline_data.data))
                img.save(nome_arq)
                links_locais.append(nome_arq)
                print(f"✨ Sucesso com IA!")
                sucesso = True
        except:
            print(f"⏳ IA indisponível para imagem {i+1}.")

        # PASSO 2: Se IA falhou, busca IMAGEM REAL (Plano B)
        if not sucesso:
            # Extrai 2 ou 3 palavras chave do título para a busca
            keywords = " ".join(titulo_post.split()[:3]) 
            if buscar_imagem_banco_real(keywords, i):
                links_locais.append(nome_arq)
                print(f"📸 Sucesso com IMAGEM REAL!")
                sucesso = True
            else:
                print(f"⚠️ Falha total na imagem {i+1}.")
                
    return links_locais

def executar():
    print(f"🚀 Iniciando Bot - Blog ID: {BLOG_ID}")
    try:
        creds = renovar_token()
        service_blogger = build('blogger', 'v3', credentials=creds)
        service_drive = build('drive', 'v3', credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 1. Notícia
        feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
        noticia_base = feed.entries[0]
        
        # 2. Texto
        print(f"✍️ Analisando: {noticia_base.title}")
        prompt_texto = (
            f"Analise a notícia: '{noticia_base.title}'. Escreva um artigo de 850 palavras. "
            "Responda em JSON: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao, links_pesquisa."
        )
        
        res = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt_texto,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # Limpeza do JSON
        texto_raw = res.text.strip()
        match = re.search(r'\{.*\}', texto_raw, re.DOTALL)
        dados = json.loads(match.group(0)) if match else json.loads(texto_raw)
        
        # 3. Imagens (IA ou Real)
        arquivos = gerar_imagens_ia_ou_real(client, dados['titulo'])
        
        # 4. Upload para Drive
        links_drive = []
        for f in arquivos:
            file_metadata = {'name': f}
            media = MediaFileUpload(f, mimetype='image/png')
            file = service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
            service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
            links_drive.append(f"https://drive.google.com/uc?export=view&id={file.get('id')}")

        # 5. Publicação
        dados['img_topo'] = links_drive[0] if len(links_drive) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links_drive[1] if len(links_drive) > 1 else dados['img_topo']
        dados['assinatura'] = f"<br><b>Pesquisa:</b> {dados.get('links_pesquisa', 'G1')}<br><br>{BLOCO_FIXO_FINAL}"

        corpo_post = {
            'kind': 'blogger#post',
            'title': dados['titulo'],
            'content': obter_esqueleto_html(dados),
            'labels': ["Política", "Brasil", "Notícias"]
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"🎉 SUCESSO! Post publicado com imagens garantidas.")

    except Exception as e:
        print(f"💥 Erro: {e}")

if __name__ == "__main__":
    executar()
