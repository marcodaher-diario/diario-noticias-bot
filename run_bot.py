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
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos", "o", "a", "e"]
    conteudo = f"{titulo} {texto_completo[:300]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    tags_fixas = ["Emagrecer", "Saúde", "Marco Daher"]
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

def upload_para_drive(service_drive, caminho_arquivo, nome_arquivo):
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    file = service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

def gerar_imagens_ia(client, titulo_post):
    links_locais = []
    # Modelo corrigido para a nomenclatura estável de 2026
    modelo_img = 'imagen-3.0-generate-001'
    
    prompts = [
        f"Professional news photojournalism, cinematic wide shot, 16:9 aspect ratio, high quality: {titulo_post}",
        f"Conceptual political illustration, deep blue tones, 16:9 aspect ratio, digital art: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        for tentativa in range(3):
            try:
                print(f"🎨 Gerando imagem {i+1}/2 (Tentativa {tentativa+1})...")
                # Em 2026, algumas contas exigem o uso da função generate_images diretamente
                response = client.models.generate_images(
                    model=modelo_img,
                    prompt=p,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio="16:9"
                    )
                )
                if response.generated_images:
                    response.generated_images[0].image.save(nome_arq)
                    links_locais.append(nome_arq)
                    break
            except Exception as e:
                print(f"⏳ Erro imagem {i}: {e}")
                time.sleep(12)
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
        dados = None
        for t in range(3):
            try:
                print(f"✍️ Gerando texto (Tentativa {t+1})...")
                prompt = (f"Atue como analista político. Notícia: '{noticia_base.title}'. "
                         "Gere JSON: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao, links_pesquisa.")
                res = client.models.generate_content(
                    model="gemini-2.0-flash", # Atualizado para o modelo estável mais recente
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                dados = json.loads(res.text)
                break
            except Exception as e:
                print(f"⏳ Erro IA: {e}. Aguardando...")
                time.sleep(15)

        if not dados: raise Exception("IA Indisponível.")

        # 3. Tags SEO
        tags_geradas = gerar_tags_seo(dados['titulo'], dados['texto1'])
        print(f"🏷️ Tags: {', '.join(tags_geradas)}")

        # 4. Imagens
        arquivos = gerar_imagens_ia(client, dados['titulo'])
        links = [upload_para_drive(service_drive, f, f) for f in arquivos]

        # 5. Organização
        dados['img_topo'] = links[0] if len(links) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links[1] if len(links) > 1 else dados['img_topo']
        dados['assinatura'] = f"<div style='margin-top:25px;'>{dados.get('links_pesquisa', '')}</div>{BLOCO_FIXO_FINAL}"

        # 6. Publicação
        html_final = obter_esqueleto_html(dados)
        corpo_post = {
            'kind': 'blogger#post',
            'title': dados['titulo'],
            'content': html_final,
            'labels': tags_geradas
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO TOTAL! Postado no Blog.")

    except Exception as e:
        print(f"💥 Falha: {e}")

if __name__ == "__main__":
    executar()
