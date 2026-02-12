import os
import json
import feedparser
import time
import re
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai
from google.genai import types

# --- IMPORTAÇÕES ---
try:
    from template_blog import obter_esqueleto_html
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError as e:
    print(f"❌ ERRO de Importação: {e}")
    raise

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "7605688984374445860" 
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

def renovar_token():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("O arquivo token.json não foi encontrado!")
    with open("token.json", "r") as f:
        info = json.load(f)
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def gerar_tags_seo(titulo, texto_completo):
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos", "o", "a", "e", "dos", "das"]
    conteudo = f"{titulo} {texto_completo[:500]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    tags_fixas = ["Emagrecer", "Saúde", "Marco Daher", "Política", "Brasil"]
    for tf in tags_fixas:
        if tf not in tags: tags.append(tf)
    return tags[:15]

def upload_para_drive(service_drive, caminho_arquivo, nome_arquivo):
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    file = service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

def gerar_imagens_ia(client, titulo_post):
    links_locais = []
    modelo_img = 'imagen-3' 
    
    prompts = [
        f"Cinematic wide shot, professional political journalism photo, 16:9 aspect ratio, high resolution: {titulo_post}",
        f"High quality professional illustration for news blog, 16:9 aspect ratio, blue tones: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        try:
            print(f"🎨 Gerando imagem {i+1}/2...")
            response = client.models.generate_images(
                model=modelo_img,
                prompt=p,
                config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
            )
            if response.generated_images:
                response.generated_images[0].image.save(nome_arq)
                links_locais.append(nome_arq)
                print(f"✨ Imagem {i+1} salva!")
        except Exception as e:
            print(f"⚠️ Erro imagem {i}: {e}")
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
        
        # 2. Conteúdo Longo (600-900 palavras)
        dados = None
        print(f"✍️ Gerando artigo detalhado...")
        
        prompt = (
            f"Atue como um analista político experiente. Com base na notícia: '{noticia_base.title}'. "
            "Escreva um artigo profundo, com tom jornalístico sério, contendo entre 600 e 900 palavras. "
            "Estruture o texto para que cada seção (texto1, texto2, texto3) seja longa e rica em detalhes. "
            "Responda estritamente em JSON com as chaves: "
            "titulo, intro (mínimo 100 palavras), sub1, texto1 (mínimo 200 palavras), "
            "sub2, texto2 (mínimo 200 palavras), sub3, texto3 (mínimo 200 palavras), "
            "texto_conclusao (mínimo 100 palavras), links_pesquisa."
        )

        try:
            res = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            dados = json.loads(res.text)
            print(f"✅ Texto longo gerado com sucesso!")
        except Exception as e:
            print(f"❌ Erro na geração do texto: {e}")
            return

        # 3. SEO e Imagens
        tags_geradas = gerar_tags_seo(dados['titulo'], dados['texto1'])
        arquivos = gerar_imagens_ia(client, dados['titulo'])
        links = [upload_para_drive(service_drive, f, f) for f in arquivos]

        # 4. Organização do Conteúdo
        dados['img_topo'] = links[0] if len(links) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links[1] if len(links) > 1 else dados['img_topo']
        
        # Links de pesquisa + Assinatura fixa
        links_html = f"<br><br><b>Fontes para pesquisa:</b><br>{dados.get('links_pesquisa', 'G1, Folha, CNN Brasil')}"
        dados['assinatura'] = f"{links_html}<br><br>{BLOCO_FIXO_FINAL}"

        # 5. Publicação
        html_final = obter_esqueleto_html(dados)
        corpo_post = {
            'kind': 'blogger#post',
            'title': dados['titulo'],
            'content': html_final,
            'labels': tags_geradas
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO TOTAL! Artigo publicado com {len(html_final.split())} palavras estimadas.")

    except Exception as e:
        print(f"💥 Erro na execução: {e}")

if __name__ == "__main__":
    executar()
