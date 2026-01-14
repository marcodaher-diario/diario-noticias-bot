# =========================================================
# IMPORTS
# =========================================================
import feedparser
import re
import os
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import random
import time
from datetime import datetime, timedelta

# =============================
# CONFIGURAÇÕES
# =============================
BLOG_ID = "7605688984374445860"
RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/",
    "https://feeds.uol.com.br/home.xml",
    "https://rss.uol.com.br/feed/noticias.xml",
    "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://agenciabrasil.ebc.com.br/rss",
    "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.gazetadopovo.com.br/feed/rss/brasil.xml",
    "https://reporterbrasil.org.br/feed/",
    "https://www.cnnbrasil.com.br/feed/",
    "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
    "https://g1.globo.com/rss/g1/economia/",
    "https://www.metropoles.com/feed/"
]

PALAVRAS_POLITICA = ["política", "mundo", "governo", "presidente", "lula", "bolsonaro", "congresso", "senado", "stf", "eleição", "moraes", "toffoli", "fux", "Dino", "flavio", "eduardo", "depoimento", "magistrados", "juízes", "ex-presidente", "corrupção", "vereadores", "deputado", "senador", "PGR", "ministério público"]
PALAVRAS_ECONOMIA = ["economia", "pib", "dólar", "euro", "inflação", "selic", "mercado", "bolsa de valores", "banco central", "presidente", "aumento", "real"]

SCOPES = ["https://www.googleapis.com/auth/blogger"]
IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

# =============================
# BLOCO FIXO FINAL
# =============================

BLOCO_FIXO_FINAL = """<p></p>
<div style="text-align: right;">
  <b><span style="color: #073763; font-family: arial; font-size: xx-small;"><i>Por: Marco Daher</i></span>
</b></div>
<div style="text-align: right;">
  <b><span style="color: #073763; font-family: arial; font-size: xx-small;"><i>Todos os Direitos Reservados</i></span>
</b></div>
<div style="text-align: right;">
  <b><span style="color: #073763; font-family: arial; font-size: xx-small;"><i>©MarcoDaher2025</i></span>
</b></div>
<span style="color: #073763;"><br /></span>
<div style="text-align: center;">
  <span style="font-size: medium;"><span style="font-family: arial;"><span style="color: #073763;">Veja também esses <b>LINKS </b>interessantes, e <b>INSCREVA-SE</b> nos
      meus <b>CANAIS</b>:</span></span>
</span></div>
<span style="font-size: medium;"><span style="color: #073763;"><br /></span>
</span><div style="text-align: center;">
  <span style="font-size: medium;"><span style="color: #073763;"><span style="font-family: arial;">Zona do Saber ⇨ </span><b><a href="http://zonadosaber1.blogspot.com/" style="font-family: arial;">Blog</a><span style="font-family: arial;"> - </span><a href="https://www.youtube.com/@ZonadoSaber51" style="font-family: arial;">Canal Youtube</a><span style="font-family: arial;"> - </span><a href="https://www.facebook.com/profile.php?id=61558194825166" style="font-family: arial;">FaceBook</a></b></span>
</span></div>
<span style="font-size: medium;"><span style="color: #073763;"><span style="font-family: arial;"><div style="text-align: center;"><br /></div>
    <div style="text-align: center;">
      DFBolhas ⇨
      <b><a href="https://dfbolhas.blogspot.com/">Blog</a> -
        <a href="https://www.youtube.com/marcodaher51">Canal Youtube</a> -
        <a href="https://www.facebook.com/mdaher51/">Facebook</a></b>
    </div>
    <div style="text-align: center;"><br /></div>
    <div style="text-align: center;">
      Cursos, Negócios e Oportunidades ⇨
      <b><a href="https://cursosnegocioseoportunidades.blogspot.com/">Blog</a> -
        <a href="https://www.youtube.com/@CursoseNegociosMD">Canal Youtube</a> -
        <a href="https://www.facebook.com/CursosNegociosOportunidades">FaceBook</a></b>
    </div>
    <div style="text-align: center;"><br /></div>
    <div style="text-align: center;">
      Emagrecer com Saúde ⇨
      <b><a href="https://emagrecendo100crise.blogspot.com/">Blog</a> -
        <a href="https://www.youtube.com/@Saude-Bem-Estar-51">Canal YouTube</a>
        - <a href="https://www.facebook.com/marcocuidese">FaceBook</a></b>
    </div>
    <div style="text-align: center;"><br /></div>
    <div style="text-align: center;">
      Marco Daher ⇨
      <b><a href="https://www.youtube.com/@MarcoDaher">Canal Youtube</a> -
        <a href="https://www.facebook.com/MarcoDaher51/">FaceBook</a></b>
    </div>
    <div style="text-align: center;"><br /></div>
    <div style="text-align: center;">
      Relaxamento e Meditação ⇨
      <a href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ"><b>Canal YouTube</b></a>
    </div>
    <div style="text-align: center;"><br /></div>
    <div style="text-align: center;">
      MD Arte Foto ⇨ <a href="https://mdartefoto.blogspot.com/"><b>Blog</b></a>
    </div></span><br /></span>
</span><div style="text-align: center;">
  <span style="font-size: medium;"><span style="font-family: arial;"><span style="color: #073763;">Caso queira contribuir com o Canal, use a Chave PIX:
      <b>marco.caixa104@gmail.com</b></span></span>
</span></div>
<span style="color: #073763; font-family: arial; font-size: medium;"><div style="text-align: center;">
    O conhecimento é o combustível para o Sucesso. Não pesa e nãoocupa espaço.
  </div>
  <div style="text-align: center;">
    🚨 Aproveite e Inscreva-se no Canal 📌, deixe o LIKE 👍 e ative o Sininho
    🔔.
  </div>
  <div style="text-align: center;">
    Muito obrigado por assistir e abraço. 🎯
  </div></span>
<p></p>
<div bis_skin_checked="1" class="footer-grid" style="background-color: white; color: #686868; font-family: Arial, Helvetica, sans-serif; font-size: 18px; line-height: 1.7; text-align: justify;">
  <div bis_skin_checked="1" class="footer-item" style="line-height: 1.7;">
    <h4 style="margin: 0px; position: relative;"></h4>
  </div>
</div>
"""

# =============================
# FUNÇÕES DE APOIO
# =============================

def autenticar_blogger():
    print("🔐 Autenticando no Blogger...")
    if not os.path.exists("token.json"):
        raise FileNotFoundError("Erro: 'token.json' não encontrado!")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG): return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def gerar_tags_seo(titulo, texto):
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos"]
    conteudo = f"{titulo} {texto[:100]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    
    tags_fixas = ["Notícias", "Diário de Notícias", "Marco Daher"]
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

def extrair_imagem(entry):
    if "media_content" in entry: return entry.media_content[0].get("url")
    if "media_thumbnail" in entry: return entry.media_thumbnail[0].get("url")
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    if match: return match.group(1)
    return IMAGEM_FALLBACK

def extrair_video_youtube(link):
    video_id = None
    if "youtube.com/watch" in link:
        video_id = link.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in link:
        video_id = link.split("youtu.be/")[1]
    
    if video_id:
        return f'<div style="text-align:center; margin: 20px 0;"><iframe width="680" height="383" src="https://www.youtube.com/embed/{video_id}" frameborder="0" allowfullscreen style="max-width:100%;"></iframe></div>'
    return None

def quebrar_paragrafos(texto):
    frases = re.split(r'(?<=[.!?]) +', texto)
    paragrafos = []
    bloco = []
    for frase in frases:
        bloco.append(frase)
        if len(bloco) >= 2:
            paragrafos.append(" ".join(bloco))
            bloco = []
    if bloco: paragrafos.append(" ".join(bloco))
    return "".join(f"<p>{p}</p><br>" for p in paragrafos)

def verificar_assunto(titulo, texto):
    conteudo = f"{titulo} {texto}".lower()
    if any(p in conteudo for p in PALAVRAS_POLITICA): return "politica"
    if any(p in conteudo for p in PALAVRAS_ECONOMIA): return "economia"
    return "geral"

import time
from datetime import datetime, timedelta

def noticia_recente(entry, horas=48):
    data_entry = None

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        data_entry = entry.published_parsed
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        data_entry = entry.updated_parsed
    else:
        return False  # sem data = descarta

    data_noticia = datetime.fromtimestamp(time.mktime(data_entry))
    limite = datetime.now() - timedelta(hours=horas)

    return data_noticia >= limite


# =============================
# GERAÇÃO DE CONTEÚDO
# =============================

def gerar_conteudo(n):
    texto_limpo = quebrar_paragrafos(re.sub(r"<[^>]+>", "", n["texto"]))
    video_html = extrair_video_youtube(n["link"])
    
    if not video_html:
        media_html = f"""
        <div style="text-align:center; margin: 20px 0;">
            <a href="{n['link']}" target="_blank" style="text-decoration:none;">
                <img src="{n['imagem']}" width="680" height="383" style="max-width:100%; height:auto; border-radius:10px; border: 1px solid #ddd;">
                <div style="margin-top:15px;">
                    <span style="background-color: #cc0000; color: white; padding: 12px 25px; font-weight: bold; border-radius: 5px; font-family: Arial; display: inline-block;">▶ ASSISTIR VÍDEO COMPLETO NA FONTE</span>
                </div>
            </a>
        </div>"""
    else:
        media_html = video_html

    return f"""<div style="font-family:Arial; color:#444; font-size:16px; text-align:justify; line-height:1.6;"><h2 style="font-size:26px; text-align:center; color:#073763;">{n['titulo']}</h2><hr style="border: 0; border-top: 1px solid #eee;">{media_html}<p><b>Fonte:</b> {n['fonte']}</p><div style="margin-top:20px;">{texto_limpo}</div><p style="text-align:center; margin-top:30px;"><a href="{n['link']}" target="_blank" style="color: #992211; font-weight: bold;">🔗 Clique aqui para ler a matéria original</a></p><br>{BLOCO_FIXO_FINAL}</div>"""

# =============================
# FLUXO PRINCIPAL
# =============================

import random
import time
from datetime import datetime, timedelta

def noticia_recente(entry, horas=48):
    data_entry = None

    if hasattr(entry, "published_parsed") and entry.published_parsed:
        data_entry = entry.published_parsed
    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
        data_entry = entry.updated_parsed
    else:
        return False

    data_noticia = datetime.fromtimestamp(time.mktime(data_entry))
    limite = datetime.now() - timedelta(hours=horas)

    return data_noticia >= limite


def buscar_noticias(tipo_alvo, limite=4):
    print(f"📰 Buscando notícias do tipo: {tipo_alvo}...")
    noticias = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")

        for entry in feed.entries:
            if not noticia_recente(entry, horas=48):
                continue

            titulo = entry.get("title", "")
            texto = entry.get("summary", "")
            link = entry.get("link", "")

            if not titulo or not link:
                continue

            if ja_publicado(link):
                continue

            tipo_detectado = verificar_assunto(titulo, texto)
            if tipo_detectado != tipo_alvo:
                continue

            noticias.append({
                "titulo": titulo,
                "texto": texto,
                "link": link,
                "fonte": fonte,
                "imagem": extrair_imagem(entry),
                "labels": gerar_tags_seo(titulo, texto)
            })

    random.shuffle(noticias)
    return noticias[:limite]


def executar_fluxo():
    try:
        service = autenticar_blogger()
        # Define o assunto baseado na hora de Brasília (considerando que o server é UTC, ajustamos no YAML)
        hora = datetime.now().hour
        
        if hora < 12: tipo = "politica"
        elif 12 <= hora < 18: tipo = "geral"
        else: tipo = "economia"

        noticias = buscar_noticias(tipo, limite=10)
        for n in noticias:
            service.posts().insert(blogId=BLOG_ID, body={"title": n["titulo"], "content": gerar_conteudo(n), "labels": n["labels"], "status": "LIVE"}).execute()
            registrar_publicacao(n["link"])
            print(f"✅ Publicado [{tipo}]: {n['titulo']}")
    except Exception as e: print(f"💥 Erro: {e}")

if __name__ == "__main__":
    executar_fluxo()
