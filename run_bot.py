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
    conteudo = f"{titulo} {texto_completo[:500]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = [p.capitalize() for p in palavras if p not in stopwords]
    tags_fixas = ["Emagrecer", "Saúde", "Marco Daher", "Política"]
    for tf in tags_fixas:
        if tf not in tags: tags.append(tf)
    return list(dict.fromkeys(tags))[:15]

def upload_para_drive(service_drive, caminho_arquivo, nome_arquivo):
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    file = service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

def gerar_imagens_ia(client, titulo_post):
    links_locais = []
    prompts = [
        f"Professional news photojournalism image, cinematic wide shot, 16:9 ratio: {titulo_post}",
        f"Political analysis conceptual illustration, professional blue tones, 16:9 ratio: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        sucesso = False
        
        # TENTATIVA 1: Modelo PRO
        try:
            print(f"🎨 Gerando imagem {i+1}/2 com Gemini 3 Pro...")
            res = client.models.generate_content(
                model="gemini-3-pro-image-preview",
                contents=p,
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(aspect_ratio="16:9", image_size="2K")
                )
            )
            image_parts = [part for part in res.parts if part.inline_data]
            if image_parts:
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(image_parts[0].inline_data.data))
                img.save(nome_arq)
                links_locais.append(nome_arq)
                sucesso = True
        except:
            pass

        # TENTATIVA 2: Modelo FLASH (Resiliente)
        if not sucesso:
            try:
                print(f"🎨 Gerando imagem {i+1}/2 com Gemini 3 Flash...")
                res = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=f"{p}. Ensure the image is in 16:9 widescreen format."
                )
                image_parts = [part for part in res.parts if part.inline_data]
                if image_parts:
                    from PIL import Image
                    import io
                    img = Image.open(io.BytesIO(image_parts[0].inline_data.data))
                    img.save(nome_arq)
                    links_locais.append(nome_arq)
                    sucesso = True
            except Exception as e:
                print(f"⚠️ Falha na imagem {i}: {e}")
                
    return links_locais

def executar():
    print(f"🚀 Iniciando Bot - Blog ID: {BLOG_ID}")
    try:
        creds = renovar_token()
        service_blogger = build('blogger', 'v3', credentials=creds)
        service_drive = build('drive', 'v3', credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 1. Busca Notícia
        feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
        noticia_base = feed.entries[0]
        
        # 2. Gera Artigo com RETRY para erro 503
        print(f"✍️ Analisando: {noticia_base.title}")
        prompt_texto = (
            f"Analise a notícia: '{noticia_base.title}'. Escreva um artigo de 850 palavras. "
            "Seja profundo e acadêmico-jornalístico. Responda em JSON: "
            "titulo, intro (150 palavras), sub1, texto1 (250 palavras), "
            "sub2, texto2 (250 palavras), sub3, texto3 (150 palavras), "
            "texto_conclusao (100 palavras), links_pesquisa."
        )
        
        dados = None
        for tentativa in range(3):
            try:
                res = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=prompt_texto,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                dados = json.loads(res.text)
                print(f"✅ Artigo longo gerado.")
                break
            except Exception as e:
                if "503" in str(e):
                    print(f"⏳ Servidor lotado (503). Tentativa {tentativa+1}/3 em 10s...")
                    time.sleep(10)
                else:
                    raise e

        if not dados: raise Exception("Google Gemini indisponível no momento.")

        # 3. Imagens
        arquivos = gerar_imagens_ia(client, dados['titulo'])
        links_drive = [upload_para_drive(service_drive, f, f) for f in arquivos]

        # 4. Tags
        tags = gerar_tags_seo(dados['titulo'], dados['texto1'])

        # 5. Publicação
        dados['img_topo'] = links_drive[0] if len(links_drive) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links_drive[1] if len(links_drive) > 1 else dados['img_topo']
        dados['assinatura'] = f"<br><b>Pesquisa:</b> {dados.get('links_pesquisa', 'G1')}<br><br>{BLOCO_FIXO_FINAL}"

        html_final = obter_esqueleto_html(dados)
        corpo_post = {'kind': 'blogger#post', 'title': dados['titulo'], 'content': html_final, 'labels': tags}
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"🎉 SUCESSO TOTAL!")

    except Exception as e:
        print(f"💥 Erro: {e}")

if __name__ == "__main__":
    executar()
