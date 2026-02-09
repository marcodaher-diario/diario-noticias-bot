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
BLOG_ID = "7605688984374445860" 
SCOPES = [
    "https://www.googleapis.com/auth/blogger", 
    "https://www.googleapis.com/auth/drive.file"
]

# --- FUNÇÕES DE APOIO ---

def renovar_token():
    """Autentica o bot usando o token.json salvo."""
    if not os.path.exists("token.json"):
        raise FileNotFoundError("O arquivo token.json não foi encontrado!")
    
    with open("token.json", "r") as f:
        info = json.load(f)
    
    creds = Credentials.from_authorized_user_info(info, SCOPES)
    
    if creds.expired and creds.refresh_token:
        print("🔄 Renovando acesso ao Google Services...")
        creds.refresh(Request())
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return creds

def upload_para_drive(service_drive, caminho_arquivo, nome_arquivo):
    """Sobe a imagem para o Drive e retorna o link direto para o Blogger."""
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    
    # Cria o arquivo no Drive
    file = service_drive.files().create(
        body=file_metadata, 
        media_body=media, 
        fields='id'
    ).execute()
    
    # Dá permissão de leitura pública para que a imagem apareça no blog
    service_drive.permissions().create(
        fileId=file.get('id'), 
        body={'type': 'anyone', 'role': 'reader'}
    ).execute()
    
    # Retorna o link de visualização direta (formato uc?export=view)
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

def gerar_imagens_ia(client, titulo_post):
    """Gera duas imagens 16:9 usando a Imagen 3."""
    links_locais = []
    # Prompts focados no estilo 16:9 solicitado
    prompts = [
        f"Professional news photojournalism, cinematic wide shot, high resolution: {titulo_post}",
        f"Conceptual political illustration, clean and modern, deep blue tones, symbolic: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        print(f"🎨 Gerando imagem {i+1}/2 via Imagen 3...")
        try:
            response = client.models.generate_images(
                model='imagen-3.0-generate-002',
                prompt=p,
                config=types.GenerateImagesConfig(
                    number_of_images=1, 
                    aspect_ratio="16:9"
                )
            )
            # Salva localmente para o upload posterior
            response.generated_images[0].image.save(nome_arq)
            links_locais.append(nome_arq)
        except Exception as e:
            print(f"⚠️ Erro ao gerar imagem {i}: {e}")
            
    return links_locais

# --- NÚCLEO DO BOT ---

def executar():
    print(f"🚀 Iniciando Bot Diário de Notícias - Blog ID: {BLOG_ID}")
    
    try:
        # 1. Autenticação e Setup
        creds = renovar_token()
        service_blogger = build('blogger', 'v3', credentials=creds)
        service_drive = build('drive', 'v3', credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 2. Captura da Notícia (G1 Política)
        feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
        if not feed.entries:
            print("⚠️ Feed RSS vazio.")
            return
        
        noticia_base = feed.entries[0]
        print(f"📰 Notícia Base: {noticia_base.title}")

        # 3. Geração do Texto Estruturado (Gemini 3 Flash)
        print("✍️ Solicitando análise analítica ao Gemini 3...")
        prompt_texto = (
            f"Atue como um analista político. Com base na notícia '{noticia_base.title}', "
            "escreva um artigo profundo em português. "
            "Responda APENAS com um objeto JSON puro usando estas chaves: "
            "titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao."
        )
        
        res_texto = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_texto,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # Converte a resposta JSON da IA em dicionário Python
        dados = json.loads(res_texto.text)

        # 4. Geração e Upload de Imagens
        arquivos_fotos = gerar_imagens_ia(client, dados['titulo'])
        links_finais_fotos = []
        
        for arq in arquivos_fotos:
            print(f"☁️ Subindo {arq} para o Google Drive...")
            url_drive = upload_para_drive(service_drive, arq, arq)
            links_finais_fotos.append(url_drive)

        # 5. Organização dos dados para o Template MD
        # Preenche os campos de imagem no dicionário
        dados['img_topo'] = links_finais_fotos[0] if len(links_finais_fotos) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links_finais_fotos[1] if len(links_finais_fotos) > 1 else dados['img_topo']
        
        # Cria a assinatura com o link original
        dados['assinatura'] = (
            f"<hr><p style='text-align:right; font-size:small;'>"
            f"Fonte Original: <a href='{noticia_base.link}'>G1 Política</a><br>"
            f"Análise gerada por Inteligência Artificial em 2026</p>"
        )

        # 6. Renderização do HTML e Publicação
        print("🏗️ Renderizando template e enviando para o Blogger...")
        html_final = obter_esqueleto_html(dados)

        corpo_post = {
            'kind': 'blogger#post',
            'title': dados['titulo'],
            'content': html_final
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO! Artigo '{dados['titulo']}' publicado com imagens 16:9.")

    except Exception as e:
        print(f"💥 Falha crítica na execução: {e}")

if __name__ == "__main__":
    executar()
