import feedparser
import re
import os
import json
import time
import io
import requests
import random
import pytz
from datetime import datetime
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google import genai
from PIL import Image

# =============================
# CONFIGURAÇÕES BÁSICAS
# =============================
BLOG_ID = "7605688984374445860"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
ARQUIVO_LOG = "posts_publicados.txt"
SCOPES = ["https://www.googleapis.com/auth/blogger", "https://www.googleapis.com/auth/drive.file"]

RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/", "https://feeds.uol.com.br/home.xml",
    "https://rss.uol.com.br/feed/noticias.xml", "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://agenciabrasil.ebc.com.br/rss", "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.gazetadopovo.com.br/feed/rss/brasil.xml", "https://reporterbrasil.org.br/feed/",
    "https://www.cnnbrasil.com.br/feed/", "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
    "https://g1.globo.com/rss/g1/economia/"
]

# Importação do seu Bloco Fixo e Template
try:
    from configuracoes import BLOCO_FIXO_FINAL
    from template_blog import obter_esqueleto_html
except:
    BLOCO_FIXO_FINAL = "<footer>Diário de Notícias</footer>" # Fallback

# =============================
# FUNÇÕES DE APOIO (DO ORIGINAL)
# =============================
def autenticar_google():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("Erro: 'token.json' não encontrado!")
    creds_data = json.load(open("token.json"))
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open("token.json", "w") as f: f.write(creds.to_json())
    return creds

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG): return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def definir_tema_por_horario():
    fuso = pytz.timezone('America/Sao_Paulo')
    hora = datetime.now(fuso).hour
    if 5 <= hora <= 11: return "Policial", "notícias policiais, polícia militar, polícia civil, investigação criminal, operação policial, flagrante, prisão em flagrante, mandado de prisão, mandado de busca e apreensão, operação da PF, polícia federal, crime organizado, tráfico de drogas, apreensão de drogas, apreensão de armas, homicídio, tentativa de homicídio, latrocínio, assalto à mão armada, roubo, furto, sequestro, cárcere privado, estelionato, golpe virtual, fraude eletrônica, violência doméstica, lei maria da penha, feminicídio, tribunal do júri, audiência de custódia"
    elif 12 <= hora <= 17: return "Economia", "economia brasileira, notícias de economia, mercado financeiro, bolsa de valores, Ibovespa hoje, dólar hoje, cotação do dólar, euro hoje, inflação no Brasil, IPCA acumulado, taxa Selic, juros do Banco Central, Banco Central do Brasil, PIB brasileiro, crescimento econômico, recessão econômica, desemprego no Brasil, taxa de desemprego, geração de empregos, reforma tributária, carga tributária, impostos no Brasil, imposto de renda, orçamento federal, déficit público, superávit primário, dívida pública, gastos do governo, política fiscal, política monetária"
    else: return "Política", "notícias de política, política brasileira, congresso nacional, câmara dos deputados, senado federal, planalto, presidência da república, governo federal, oposição política, base aliada, votação no plenário, sessão deliberativa, projeto de lei, proposta de emenda à constituição, medida provisória, decreto presidencial, reforma administrativa, reforma tributária, reforma política, comissão parlamentar de inquérito, CPI no congresso, tribunal superior eleitoral, supremo tribunal federal, ministério público, decisões do STF, eleições municipais, eleições presidenciais, campanha eleitoral, propaganda partidária, pesquisa eleitoral, intenção de voto, coligações partidárias, partidos políticos, crise política, articulação política, impeachment"

# =============================
# GERAÇÃO DE IMAGENS (IMAGEN 3)
# =============================
def gerar_imagens_ia(client, titulo):
    arquivos = []
    # Prompt focado em 16:9 como você solicitou
    prompt = f"Professional journalistic photography, 16:9 aspect ratio, high resolution, realistic style for news: {titulo}"
    
    for i in range(1): # Gera 1 imagem principal
        nome_f = f"temp_img_{i}.png"
        try:
            # Chama o modelo Imagen 3 que você pagou
            res = client.models.generate_content(model="imagen-3.0-generate-001", contents=[prompt])
            for part in res.parts:
                if part.inline_data:
                    img = Image.open(io.BytesIO(part.inline_data.data))
                    img.save(nome_f)
                    arquivos.append(nome_f)
                    break
        except Exception as e:
            print(f"⚠️ Erro Imagen 3: {e}. Usando fallback.")
            res_backup = requests.get(f"https://loremflickr.com/1280/720/news?lock={random.randint(1,999)}")
            with open(nome_f, "wb") as f: f.write(res_backup.content)
            arquivos.append(nome_f)
    return arquivos

# =============================
# FLUXO PRINCIPAL (FUSÃO)
# =============================
def executar():
    print(f"🚀 Iniciando Bot Diário de Notícias...")
    
    try:
        # 1. Autenticação
        creds = autenticar_google()
        service_blogger = build("blogger", "v3", credentials=creds)
        service_drive = build("drive", "v3", credentials=creds)
        # FORÇANDO V1 PARA EVITAR ERRO 404
        client = genai.Client(api_key=GEMINI_API_KEY, http_options={'api_version': 'v1'})

        # 2. Busca de Notícia (Lógica do seu Original)
        tema, keywords = definir_tema_por_horario()
        print(f"🔍 Buscando notícias de {tema}...")
        feed = feedparser.parse(random.choice(RSS_FEEDS))
        noticia_selecionada = None
        
        for entry in feed.entries:
            if not ja_publicado(entry.link):
                noticia_selecionada = entry
                break
        
        if not noticia_selecionada:
            print("Nenhuma notícia nova encontrada.")
            return

        # 3. IA: Geração de Texto Longo (700-900 palavras)
        print(f"✍️ Gerando artigo autoral sobre: {noticia_selecionada.title}")
        prompt_texto = (
            f"Escreva um artigo jornalístico profissional, autoral e detalhado com 800 palavras. "
            f"Use um tom sério. Divida em introdução, três subtítulos e conclusão. "
            f"Responda APENAS em JSON com as chaves: titulo, intro, sub1, texto1, sub2, texto2, sub3, texto3, texto_conclusao. "
            f"Tema: {noticia_selecionada.title}"
        )
        
        res_ai = client.models.generate_content(model="gemini-1.5-flash", contents=prompt_texto)
        dados = json.loads(re.search(r'\{.*\}', res_ai.text, re.DOTALL).group(0))

        # 4. IA: Gerar Imagem 16:9
        imgs_locais = gerar_imagens_ia(client, dados['titulo'])
        links_drive = []
        for img_p in imgs_locais:
            media = MediaFileUpload(img_p, mimetype='image/png')
            file = service_drive.files().create(body={'name': img_p}, media_body=media, fields='id').execute()
            service_drive.permissions().create(fileId=file.get('id'), body={'type': 'anyone', 'role': 'reader'}).execute()
            links_drive.append(f"https://drive.google.com/uc?export=view&id={file.get('id')}")

        # 5. Montagem do Post (Respeitando a LARGURA do Blog)
        # O .replace('\n', '<br/>') é essencial para não estourar o layout
        dados_final = {
            'titulo': dados['titulo'],
            'img_topo': links_drive[0] if links_drive else "",
            'img_meio': links_drive[0] if links_drive else "",
            'intro': str(dados['intro']).replace('\n', '<br/>'),
            'sub1': dados['sub1'],
            'texto1': str(dados['texto1']).replace('\n', '<br/>'),
            'sub2': dados['sub2'],
            'texto2': str(dados['texto2']).replace('\n', '<br/>'),
            'sub3': dados['sub3'],
            'texto3': str(dados['texto3']).replace('\n', '<br/>'),
            'texto_conclusao': str(dados['texto_conclusao']).replace('\n', '<br/>'),
            'assinatura': f"<br><b>Fonte:</b> {noticia_selecionada.link}<br><br>{BLOCO_FIXO_FINAL}"
        }

        html_conteudo = obter_esqueleto_html(dados_final)
        
        # 6. Publicação
        corpo = {
            "title": dados['titulo'].upper(),
            "content": html_conteudo,
            "labels": [tema, "Notícias", "Brasil"],
            "status": "LIVE"
        }
        
        service_blogger.posts().insert(blogId=BLOG_ID, body=corpo).execute()
        registrar_publicacao(noticia_selecionada.link)
        print(f"✅ SUCESSO! Post '{dados['titulo']}' publicado.")

    except Exception as e:
        print(f"💥 ERRO: {e}")

if __name__ == "__main__":
    executar()
