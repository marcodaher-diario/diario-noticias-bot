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

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "7605688984374445860" 
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

# Importações locais
try:
    from template_blog import obter_esqueleto_html
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError:
    print("❌ Erro ao importar arquivos locais.")
    raise

def renovar_token():
    with open("token.json", "r") as f:
        creds = Credentials.from_authorized_user_info(json.load(f), SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f: f.write(creds.to_json())
    return creds

def buscar_imagem_reserva(index):
    """ Banco de dados reserva INFALÍVEL (LoremFlickr) """
    print(f"📸 IA falhou. Buscando foto real de política (Reserva {index+1})...")
    url = f"https://loremflickr.com/1280/720/politics,brazil/all?lock={index + int(time.time()) % 100}"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code == 200:
            with open(f"imagem_{index}.png", "wb") as f:
                f.write(res.content)
            return True
    except: pass
    return False

def gerar_imagens(client, titulo_post):
    links_locais = []
    # Usando os novos modelos da documentação
    model_nome = "gemini-2.5-flash-image" 
    prompts = [
        f"A professional photojournalism shot about: {titulo_post}. High quality, 16:9 aspect ratio.",
        f"A cinematic political setting illustration, 16:9 aspect ratio, professional lighting."
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        sucesso = False
        
        try:
            print(f"🎨 Tentando gerar imagem {i+1} com {model_nome}...")
            # Seguindo EXATAMENTE o exemplo da documentação que você enviose
            response = client.models.generate_content(
                model=model_nome,
                contents=[p],
            )
            
            for part in response.parts:
                if part.inline_data is not None:
                    # Usa o método part.as_image() ou processa os bytes
                    image = Image.open(io.BytesIO(part.inline_data.data))
                    image.save(nome_arq)
                    links_locais.append(nome_arq)
                    print(f"✨ Sucesso total com a IA!")
                    sucesso = True
                    break
        except Exception as e:
            print(f"⏳ IA ocupada ({e}). Partindo para banco de imagens real...")

        if not sucesso:
            if buscar_imagem_reserva(i):
                links_locais.append(nome_arq)
            else:
                print(f"⚠️ Falha crítica na imagem {i+1}.")
                
    return links_locais

def executar():
    print(f"🚀 Iniciando Bot - Blog ID: {BLOG_ID}")
    try:
        creds = renovar_token()
        service_blogger = build('blogger', 'v3', credentials=creds)
        service_drive = build('drive', 'v3', credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 1. RSS
        feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
        noticia = feed.entries[0]
        
        # 2. Texto (Gemini 3 Flash para Texto)
        print(f"✍️ Analisando: {noticia.title}")
        prompt_txt = f"Escreva um artigo de 850 palavras em JSON (titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao, links_pesquisa) sobre: {noticia.title}"
        res_txt = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_txt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        dados = json.loads(re.search(r'\{.*\}', res_txt.text, re.DOTALL).group(0))

        # 3. Imagens (Gemini 2.5 Flash Image para Imagem)
        arquivos = gerar_imagens(client, dados['titulo'])
        
        # 4. Upload Drive
        links_drive = []
        for f in arquivos:
            media = MediaFileUpload(f, mimetype='image/png')
            file = service_drive.files().create(body={'name': f}, media_body=media, fields='id').execute()
            service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
            links_drive.append(f"https://drive.google.com/uc?export=view&id={file.get('id')}")

        # 5. Montagem e Post
        dados['img_topo'] = links_drive[0] if len(links_drive) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links_drive[1] if len(links_drive) > 1 else dados['img_topo']
        dados['assinatura'] = f"<br><b>Fontes:</b> {dados.get('links_pesquisa', 'G1')}<br><br>{BLOCO_FIXO_FINAL}"

        html = obter_esqueleto_html(dados)
        service_blogger.posts().insert(blogId=BLOG_ID, body={
            'title': dados['titulo'],
            'content': html,
            'labels': ["Política", "Brasil"]
        }).execute()
        
        print(f"🎉 SUCESSO! Post publicado.")

    except Exception as e:
        print(f"💥 Erro: {e}")

if __name__ == "__main__":
    executar()
