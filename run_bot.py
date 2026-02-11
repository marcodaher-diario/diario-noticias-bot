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

# --- IMPORTAÇÕES DE TEMPLATE E CONFIGURAÇÕES ---
try:
    from template_blog import obter_esqueleto_html
    from configuracoes import BLOCO_FIXO_FINAL
except ImportError as e:
    print(f"❌ ERRO: Certifique-se que 'template_blog.py' e 'configuracoes.py' estão na mesma pasta. {e}")
    raise

# --- CONFIGURAÇÕES GERAIS ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BLOG_ID = "7605688984374445860" 
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

def renovar_token():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("O arquivo token.json não foi encontrado! Rode o script de autenticação primeiro.")
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
    conteudo = f"{titulo} {texto_completo[:400]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    
    # Tags estratégicas do Marco
    tags_fixas = ["Emagrecer", "Saúde", "Marco Daher", "Política", "Análise"]
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
    print(f"☁️ Fazendo upload de {nome_arquivo} para o Drive...")
    file_metadata = {'name': nome_arquivo}
    media = MediaFileUpload(caminho_arquivo, mimetype='image/png')
    file = service_drive.files().create(body=file_metadata, media_body=media, fields='id').execute()
    service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
    return f"https://drive.google.com/uc?export=view&id={file.get('id')}"

def gerar_imagens_ia(client, titulo_post):
    links_locais = []
    # Modelos recomendados para Fev/2026
    modelos_img = ['gemini-2.5-flash-image', 'imagen-3.0-generate-001']
    
    prompts = [
        f"Professional news photojournalism, cinematic wide shot, 16:9 aspect ratio, high definition: {titulo_post}",
        f"Political analysis conceptual illustration, elegant dark blue theme, 16:9 aspect ratio: {titulo_post}"
    ]
    
    for i, p in enumerate(prompts):
        nome_arq = f"imagem_{i}.png"
        sucesso_img = False
        
        for m in modelos_img:
            if sucesso_img: break
            try:
                print(f"🎨 Gerando imagem {i+1}/2 (Modelo: {m})...")
                response = client.models.generate_images(
                    model=m,
                    prompt=p,
                    config=types.GenerateImagesConfig(
                        number_of_images=1,
                        aspect_ratio="16:9" # Configuração 16:9 obrigatória do Marco
                    )
                )
                if response.generated_images:
                    response.generated_images[0].image.save(nome_arq)
                    links_locais.append(nome_arq)
                    sucesso_img = True
                    print(f"✨ Imagem {i+1} criada com sucesso!")
            except Exception as e:
                print(f"⚠️ Erro no modelo {m}: {e}")
                time.sleep(5)
                
    return links_locais

def executar():
    print(f"🚀 Iniciando Bot - Blog ID: {BLOG_ID}")
    try:
        creds = renovar_token()
        service_blogger = build('blogger', 'v3', credentials=creds)
        service_drive = build('drive', 'v3', credentials=creds)
        client = genai.Client(api_key=GEMINI_API_KEY)

        # 1. CAPTURA DA NOTÍCIA
        print("📰 Buscando notícias no G1...")
        feed = feedparser.parse("https://g1.globo.com/rss/g1/politica/")
        if not feed.entries:
            raise Exception("Não foi possível ler o RSS do G1.")
        noticia_base = feed.entries[0]
        
        # 2. GERAÇÃO DO CONTEÚDO (Gemini 3 Flash)
        dados = None
        modelos_texto = ["gemini-3-flash-preview", "gemini-2.5-flash"]
        
        for m in modelos_texto:
            if dados: break
            try:
                print(f"✍️ Gerando texto com o modelo {m}...")
                prompt = (f"Atue como um analista político sênior. Baseado na notícia: '{noticia_base.title}'. "
                         "Crie um artigo profundo e engajador. Responda APENAS em JSON com as chaves: "
                         "titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao, links_pesquisa.")
                
                res = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json")
                )
                dados = json.loads(res.text)
                print(f"✅ Texto gerado com sucesso via {m}!")
            except Exception as e:
                print(f"⚠️ Falha no modelo {m}: {e}")
                time.sleep(10)

        if not dados: raise Exception("IA Indisponível (Cota esgotada em todos os modelos).")

        # 3. TAGS SEO
        tags_geradas = gerar_tags_seo(dados['titulo'], dados['texto1'])
        print(f"🏷️ Tags: {', '.join(tags_geradas)}")

        # 4. IMAGENS 16:9
        arquivos = gerar_imagens_ia(client, dados['titulo'])
        links_drive = []
        for f in arquivos:
            links_drive.append(upload_para_drive(service_drive, f, f))

        # 5. MONTAGEM DO POST
        dados['img_topo'] = links_drive[0] if len(links_drive) > 0 else "https://via.placeholder.com/1280x720"
        dados['img_meio'] = links_drive[1] if len(links_drive) > 1 else (links_drive[0] if links_drive else "")
        
        # Assinatura e links de pesquisa
        rodape_html = f"<div style='margin-top:30px; font-size: 0.9em; color: #555;'><b>Fontes e Pesquisa:</b><br>{dados.get('links_pesquisa', 'G1 Política, Google News')}</div>"
        dados['assinatura'] = f"{rodape_html}{BLOCO_FIXO_FINAL}"

        # 6. PUBLICAÇÃO NO BLOGGER
        print("📤 Enviando para o Blogger...")
        html_final = obter_esqueleto_html(dados)
        
        corpo_post = {
            'kind': 'blogger#post',
            'blog': {'id': BLOG_ID},
            'title': dados['titulo'],
            'content': html_final,
            'labels': tags_geradas
        }
        
        request = service_blogger.posts().insert(blogId=BLOG_ID, body=corpo_post)
        request.execute()
        print(f"🎉 SUCESSO TOTAL! O artigo '{dados['titulo']}' está no ar.")

    except Exception as e:
        print(f"💥 ERRO CRÍTICO: {e}")

if __name__ == "__main__":
    executar()
