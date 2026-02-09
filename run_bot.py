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

# --- IMPORTAÇÃO DO SEU TEMPLATE ---
try:
    from template_blog import obter_esqueleto_html
except ImportError:
    print("❌ ERRO: Arquivo 'template_blog.py' não encontrado.")
    raise

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "3884849132228514800"
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

# --- FUNÇÕES AUXILIARES ---
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
    # Link direto para visualização no Blogger
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

def gerar_imagens_ia(client, titulo_noticia):
    links_fotos = []
    prompts = [
        f"Professional photojournalism, cinematic wide shot for news header: {titulo_noticia}. 16:9 aspect ratio, high resolution.",
        f"Detailed modern illustration or realistic scene representing: {titulo_noticia}. 16:9 aspect ratio, professional lighting."
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"img_post_{i}.png"
        print(f"🎨 Gerando imagem IA {i+1}/2...")
        try:
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=p,
                config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
            )
            for img in response.generated_images:
                img.image.save(nome_arq)
                links_fotos.append(nome_arq)
        except Exception as e:
            print(f"⚠️ Falha ao gerar imagem {i}: {e}")
    return links_fotos

# --- NÚCLEO DO BOT ---
def executar():
    print("🚀 Iniciando Bot Diário de Notícias...")
    creds = renovar_token()
    service_blogger = build('blogger', 'v3', credentials=creds)
    service_drive = build('drive', 'v3', credentials=creds)
    client = genai.Client(api_key=GEMINI_API_KEY)

    # 1. Busca Notícia RSS
    feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
    if not feed.entries:
        print("Nenhuma notícia disponível.")
        return
    
    noticia = feed.entries[0]
    print(f"📰 Notícia: {noticia.title}")

    # 2. IA gera o conteúdo estruturado em JSON para o seu Template
    prompt_json = f"""
    Com base na notícia '{noticia.title}', escreva um artigo jornalístico analítico.
    O texto deve ser profissional e imparcial.
    Responda APENAS com um objeto JSON puro neste formato:
    {{
        "titulo": "título chamativo em letras maiúsculas",
        "intro": "parágrafo introdutório",
        "sub1": "Subtítulo da primeira parte",
        "texto1": "desenvolvimento da primeira parte",
        "sub2": "Subtítulo da segunda parte",
        "texto2": "desenvolvimento da segunda parte",
        "sub3": "Consequências e Futuro",
        "texto3": "desenvolvimento da terceira parte",
        "texto_conclusao": "parágrafo de encerramento"
    }}
    """
    
    print("✍️ Gerando texto estruturado...")
    res_texto = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt_json,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    
    # Converte texto para dicionário Python
    dados = json.loads(res_texto.text)

    # 3. Gerar Imagens e Fazer Upload
    arquivos_locais = gerar_imagens_ia(client, dados['titulo'])
    links_drive = []
    
    for arq in arquivos_locais:
        print(f"☁️ Subindo {arq} para o Drive...")
        url = upload_para_drive(service_drive, arq, arq)
        links_drive.append(url)

    # Preenche o restante do dicionário 'dados' para o seu template
    dados['img_topo'] = links_drive[0] if len(links_drive) > 0 else "https://via.placeholder.com/1280x720"
    dados['img_meio'] = links_drive[1] if len(links_drive) > 1 else dados['img_topo']
    dados['assinatura'] = f"<hr><p style='text-align:right;'><i>Fonte: <a href='{noticia.link}'>G1 Política</a> | Gerado por Inteligência Artificial</i></p>"

    # 4. Montar HTML e Publicar
    print("🏗️ Renderizando Template MD...")
    html_final = obter_esqueleto_html(dados)

    corpo_post = {
        'kind': 'blogger#post',
        'title': dados['titulo'],
        'content': html_final
    }
    
    print("📤 Enviando para o Blogger...")
    service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
    print(f"✅ SUCESSO! Postado: {dados['titulo']}")

if __name__ == "__main__":
    executar()
