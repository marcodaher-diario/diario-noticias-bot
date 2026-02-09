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

# --- IMPORTAÇÕES SEM ALTERAR NOMES ---
try:
    from template_blog import obter_esqueleto_html
    from configuracoes import BLOCO_FIXO_FINAL  # Importando com o nome correto
except ImportError as e:
    print(f"❌ ERRO de Importação: {e}")
    raise

# --- CONFIGURAÇÕES ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "7605688984374445860" 
SCOPES = [
    "https://www.googleapis.com/auth/blogger", 
    "https://www.googleapis.com/auth/drive.file"
]

# --- FUNÇÕES DE APOIO (MANTIDAS) ---

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

#----------------------------------------------------------------------
#      GERAR IMAGENS
#----------------------------------------------------------------------

def gerar_imagens_ia(client, titulo_post):
    links_locais = []
    # Usando o nome do modelo estável conforme o manual atualizado
    modelo_imagem = 'imagen-3.0-generate-001' 
    
    prompts = [
        f"Professional news photojournalism, cinematic wide shot, 16:9 aspect ratio: {titulo_post}",
        f"Conceptual political illustration, deep blue and gold tones, 16:9 aspect ratio: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        try:
            print(f"🎨 Gerando imagem {i+1}/2...")
            response = client.models.generate_images(
                model=modelo_imagem,
                prompt=p,
                config=types.GenerateImagesConfig(
                    number_of_images=1, 
                    aspect_ratio="16:9",
                    add_watermark=False # Opcional, dependendo da sua conta
                )
            )
            response.generated_images[0].image.save(nome_arq)
            links_locais.append(nome_arq)
        except Exception as e:
            print(f"⚠️ Erro ao gerar imagem {i} com {modelo_imagem}: {e}")
            # Fallback para o nome genérico se o específico falhar
            if "404" in str(e):
                try:
                    print("🔄 Tentando modelo fallback 'imagen-3'...")
                    response = client.models.generate_images(
                        model='imagen-3',
                        prompt=p,
                        config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
                    )
                    response.generated_images[0].image.save(nome_arq)
                    links_locais.append(nome_arq)
                except Exception as e2:
                    print(f"❌ Falha total na imagem: {e2}")
    return links_locais

#-----------------------
# --- NÚCLEO DO BOT ---
#----------------------

def executar():
    print(f"🚀 Iniciando Bot - Blog ID: {BLOG_ID}")
    
    try:
        creds = renovar_token()
        service_blogger = build('blogger', 'v3', credentials=creds)
        service_drive = build('drive', 'v3', credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 1. Captura da Notícia
        feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
        noticia_base = feed.entries[0]
        
        # 2. Geração do Texto e Links de Pesquisa
        prompt_texto = (
            f"Com base na notícia '{noticia_base.title}', escreva um artigo analítico. "
            "Responda APENAS com um JSON usando estas chaves: "
            "titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao, links_pesquisa. "
            "Em 'links_pesquisa', crie uma lista HTML <ul> com 3 links de termos relacionados para busca no Google."
        )
        
        res_texto = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=prompt_texto,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        dados = json.loads(res_texto.text)

        # 3. Geração de Imagens
        arquivos_fotos = gerar_imagens_ia(client, dados['titulo'])
        links_finais_fotos = []
        for arq in arquivos_fotos:
            url = upload_para_drive(service_drive, arq, arq)
            links_finais_fotos.append(url)

        # 4. Organização dos dados para o Template
        dados['img_topo'] = links_finais_fotos[0] if len(links_finais_fotos) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links_finais_fotos[1] if len(links_finais_fotos) > 1 else dados['img_topo']
        
        # Montagem da assinatura: Links de Pesquisa + Bloco Fixo (da sua configuração)
        dados['assinatura'] = f"""
            <div style="margin-top: 25px; border-top: 1px solid #eee; padding-top: 15px;">
                <p style="font-weight: bold; color: #003366;">Links para pesquisa e aprofundamento:</p>
                {dados.get('links_pesquisa', '')}
            </div>
            {BLOCO_FIXO_FINAL}
        """

        # 5. Publicação
        html_final = obter_esqueleto_html(dados)
        corpo_post = {
            'kind': 'blogger#post', 
            'title': dados['titulo'], 
            'content': html_final
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post).execute()
        print(f"✅ SUCESSO! Postado com a assinatura completa de configuracoes.py")

    except Exception as e:
        print(f"💥 Falha: {e}")

if __name__ == "__main__":
    executar()
