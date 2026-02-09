import os
import json
import feedparser
import time
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

def upload_para_drive(service_drive, caminho_arquivo, nome_arquivo):
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    file = service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

def gerar_imagens_ia(client, titulo_post):
    links_locais = []
    modelo_img = 'imagen-3.0-generate-001'
    prompts = [
        f"Professional news photojournalism, cinematic wide shot, 16:9 aspect ratio: {titulo_post}",
        f"Conceptual political illustration, deep blue and gold tones, 16:9 aspect ratio: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        for tentativa in range(3): # Tenta 3 vezes se o modelo estiver ocupado
            try:
                print(f"🎨 Gerando imagem {i+1}/2 (Tentativa {tentativa+1})...")
                response = client.models.generate_images(
                    model=modelo_img,
                    prompt=p,
                    config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
                )
                response.generated_images[0].image.save(nome_arq)
                links_locais.append(nome_arq)
                break 
            except Exception as e:
                print(f"⚠️ Erro imagem {i}: {e}. Aguardando...")
                time.sleep(10)
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
        
        # 2. Texto com Retry para erro 503
        dados = None
        for t in range(3):
            try:
                print(f"✍️ Solicitando texto (Tentativa {t+1})...")
                prompt_texto = (
                    f"Atue como analista político. Notícia: '{noticia_base.title}'. "
                    "Gere JSON: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao, links_pesquisa."
                )
                res_texto = client.models.generate_content(
                    model="gemini-3-flash-preview", 
                    contents=prompt_texto,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                dados = json.loads(res_texto.text)
                break
            except Exception as e:
                if "503" in str(e) or "overloaded" in str(e):
                    print("⏳ Modelo sobrecarregado. Esperando 15s...")
                    time.sleep(15)
                else: raise e

        if not dados: raise Exception("Não foi possível obter dados da IA após 3 tentativas.")

        # 3. Imagens
        arquivos_fotos = gerar_imagens_ia(client, dados['titulo'])
        links_finais_fotos = [upload_para_drive(service_drive, f, f) for f in arquivos_fotos]

        # 4. Template
        dados['img_topo'] = links_finais_fotos[0] if len(links_finais_fotos) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links_finais_fotos[1] if len(links_finais_fotos) > 1 else dados['img_topo']
        dados['assinatura'] = f"""
            <div style="margin-top: 25px; border-top: 1px solid #eee; padding-top: 15px;">
                {dados.get('links_pesquisa', '')}
            </div>
            {BLOCO_FIXO_FINAL}
        """

        # 5. Postar
        html_final = obter_esqueleto_html(dados)
        corpo_post = {'kind': 'blogger#post', 'title': dados['titulo'], 'content': html_final}
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO! Artigo '{dados['titulo']}' publicado.")

    except Exception as e:
        print(f"💥 Falha: {e}")

if __name__ == "__main__":
    executar()
