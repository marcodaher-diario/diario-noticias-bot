# =========================================================
# IMPORTS
# =========================================================
import feedparser
import re
import os
import time
import random
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =========================================================
# CONFIGURAÇÕES
# =========================================================
BLOG_ID = "7605688984374445860"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

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

IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

PALAVRAS_POLITICA = [
    "política", "governo", "presidente", "lula", "bolsonaro",
    "congresso", "senado", "stf", "eleição"
]

PALAVRAS_ECONOMIA = [
    "economia", "pib", "dólar", "inflação", "selic",
    "mercado", "bolsa", "banco central"
]

# =========================================================
# AUTENTICAÇÃO
# =========================================================
def autenticar_blogger():
    if not os.path.exists("token.json"):
        raise FileNotFoundError("token.json não encontrado")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =========================================================
# CONTROLE DE DUPLICAÇÃO
# =========================================================
def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG):
        return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# =========================================================
# SEO / TAGS
# =========================================================
def gerar_tags_seo(titulo, texto):
    stopwords = {"com","de","do","da","em","para","uma","que","na","no"}
    palavras = re.findall(r"\b\w{4,}\b", f"{titulo} {texto}".lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p.capitalize() not in tags:
            tags.append(p.capitalize())
    return tags[:15] + ["Notícias", "Marco Daher"]

# =========================================================
# EXTRAÇÃO DE MÍDIA
# =========================================================
def extrair_imagem(entry):
    if "media_content" in entry:
        return entry.media_content[0].get("url")
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0].get("url")
    match = re.search(r'<img[^>]+src="([^">]+)"', entry.get("summary", ""))
    return match.group(1) if match else IMAGEM_FALLBACK

def extrair_video_youtube(link):
    if "youtube.com/watch" in link:
        return link.split("watch?v=")[1].split("&")[0]
    if "youtu.be/" in link:
        return link.split("youtu.be/")[1]
    return None

def gerar_video_embed(video_id):
    if not video_id:
        return None
    return f"""
    <div class="auto-video">
        <iframe
            src="https://www.youtube.com/embed/{video_id}"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
            loading="lazy"></iframe>
    </div>
    """

# =========================================================
# TEXTO
# =========================================================
def quebrar_paragrafos(texto):
    frases = re.split(r'(?<=[.!?]) +', texto)
    return "".join(f"<p>{' '.join(frases[i:i+2])}</p>" for i in range(0, len(frases), 2))

def verificar_assunto(titulo, texto):
    base = f"{titulo} {texto}".lower()
    if any(p in base for p in PALAVRAS_POLITICA):
        return "politica"
    if any(p in base for p in PALAVRAS_ECONOMIA):
        return "economia"
    return "geral"

def noticia_recente(entry, horas=48):
    data = entry.get("published_parsed") or entry.get("updated_parsed")
    if not data:
        return False
    return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)

# =============================
# BLOCO FIXO FINAL
# =============================

BLOCO_FIXO_FINAL = """<div style="text-align: right;">
    <span style="color: #073763; font-family: arial; font-size: xx-small;"><b><i><br /></i></b></span>
  </div>
  <div style="text-align: right;">
    <span style="font-family: arial;"><div bis_skin_checked="1" class="footer-header" style="background-color: white; color: #073763; font-family: Arial, Helvetica, sans-serif; font-size: 18px; line-height: 1.3; text-align: justify;">
        <p style="font-size: x-small; font-weight: bold; line-height: 1.3; text-align: right;">
          <i>Por: Marco Daher&nbsp;<br />Todos os Direitos Reservados<br />©MarcoDaher2025</i>
        </p>
      </div>
      <p style="background-color: white; color: #073763; font-family: Arial, Helvetica, sans-serif; font-weight: bold; line-height: 1.3; text-align: center;">
        <span style="font-family: arial;">Veja também esses LINKS interessantes, e INSCREVA-SE nos meus
          CANAIS:</span>
      </p>
      <div bis_skin_checked="1" class="footer-grid" style="background-color: white; font-family: Arial, Helvetica, sans-serif; line-height: 1.3; text-align: justify;">
        <div bis_skin_checked="1" class="footer-item" style="line-height: 1.7;">
          <h4 style="margin: 0px; position: relative;">
            <p style="line-height: 1.7; text-align: center;">
              <span style="font-family: arial;"><span style="color: #990000;">Zona do Saber</span></span><span style="color: #073763; font-family: arial;">
                ⇨&nbsp;<a bis_skin_checked="1" href="http://zonadosaber1.blogspot.com/" style="color: #1962dd; text-decoration-line: none;" target="_blank">Blog</a>&nbsp;-&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/@ZonadoSaber51" style="color: #1962dd; text-decoration-line: none;" target="_blank">Canal Youtube</a>&nbsp;-&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/profile.php?id=61558194825166" style="color: #1962dd; text-decoration-line: none;" target="_blank">FaceBook</a></span>
            </p>
            <p style="line-height: 1.7; text-align: center;">
              <span style="font-family: arial;"><span style="color: #990000;">DFBolhas</span></span><span style="color: #073763; font-family: arial;">&nbsp;⇨&nbsp;<a bis_skin_checked="1" href="https://dfbolhas.blogspot.com/" style="color: #1962dd; text-decoration-line: none;" target="_blank">BLOG</a>&nbsp;-&nbsp;&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/marcodaher51" style="color: #1962dd; text-decoration-line: none;" target="_blank">Canal Youtube</a>&nbsp;-&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/mdaher51/" style="color: #1962dd; text-decoration-line: none;" target="_blank">Facebook</a></span>
            </p>
            <p style="line-height: 1.7; text-align: center;">
              <span style="font-family: arial;"><span style="color: #990000;">Cursos, Negócios e Oportunidades</span></span><span style="color: #073763; font-family: arial;">
                &nbsp;⇨&nbsp;&nbsp;<a bis_skin_checked="1" href="https://cursosnegocioseoportunidades.blogspot.com/" style="color: #1962dd; text-decoration-line: none;" target="_blank">Blog</a>&nbsp;&nbsp;-&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/CursosNegociosOportunidades" style="color: #1962dd; text-decoration-line: none;" target="_blank">FaceBook</a></span>
            </p>
            <p style="line-height: 1.7; text-align: center;">
              <span style="font-family: arial;"><span style="color: #990000;">Marco Daher&nbsp;</span></span><span style="color: #073763; font-family: arial;">⇨&nbsp;&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/@MarcoDaher" style="color: #1962dd; text-decoration-line: none;" target="_blank">Canal Youtube</a></span>
            </p>
            <p style="line-height: 1.7; text-align: center;">
              <span style="font-family: arial;"><span style="color: #990000;">Emagrecer com Saúde&nbsp;</span></span><span style="color: #073763; font-family: arial;">⇨&nbsp;&nbsp;<a bis_skin_checked="1" href="https://emagrecendo100crise.blogspot.com/" style="color: #1962dd; text-decoration-line: none;" target="_blank">BLOG</a>&nbsp;-&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/@Saude-Bem-Estar-51" style="color: #1962dd; text-decoration-line: none;" target="_blank">Canal YouTube</a>&nbsp;-&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/marcocuidese" style="color: #1962dd; text-decoration-line: none;" target="_blank">FaceBook</a></span>
            </p>
            <p style="line-height: 1.7; text-align: center;">
              <span style="font-family: arial; white-space-collapse: preserve;"><span style="color: #990000;">MD Arte Foto </span></span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">⇨ </span><a bis_skin_checked="1" href="https://mdartefoto.blogspot.com/" style="color: #1962dd; font-family: arial; text-decoration-line: none; white-space-collapse: preserve;" target="_blank">Blog</a>
            </p>
            <p style="line-height: 1.7; text-align: center;">
              <span style="font-family: arial; white-space-collapse: preserve;"><span style="color: #990000;">Relaxamento e Meditação</span><span style="color: #073763;"> </span></span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">⇨ </span><a bis_skin_checked="1" href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" style="color: #1962dd; font-family: arial; text-decoration-line: none; white-space-collapse: preserve;" target="_blank">Canal YouTube</a>
            </p>
            <p style="line-height: 1.7; text-align: center;">
              <span style="color: #073763; font-family: arial; white-space-collapse: preserve;">Caso queira contribuir com o Canal, use a Chave PIX: </span><span style="font-family: arial; white-space-collapse: preserve;"><span style="color: #990000;">marco.caixa104@gmail.com</span></span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">
              </span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">O conhecimento é o combustível para o Sucesso. Não pesa e não </span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">ocupa espaço. 
</span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">🚨 Aproveite e Inscreva-se no Canal 📌, deixe o LIKE 👍 e ative </span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">o Sininho 🔔. 
</span><span style="color: #073763; font-family: arial; white-space-collapse: preserve;">Muito obrigado por assistir e abraço. 🎯</span>
            </p>
          </h4>
        </div>
      </div></span>
  </div>
</div>
<p></p>
<div bis_skin_checked="1" class="footer-grid" style="background-color: white; color: #686868; font-family: Arial, Helvetica, sans-serif; font-size: 18px; line-height: 1.3; text-align: justify;">
  <div bis_skin_checked="1" class="footer-item" style="line-height: 1.3;">
    <h4 style="margin: 0px; position: relative;"></h4>
  </div>
</div>
"""

# =========================================================
# CONTEÚDO FINAL
# =========================================================
def gerar_conteudo(n):
    texto_limpo = quebrar_paragrafos(re.sub(r"<[^>]+>", "", n["texto"]))
    video_html = gerar_video_embed(n["video_id"])

    media_html = video_html if video_html else f"""
    <div class="auto-media">
        <a href="{n['link']}" target="_blank">
            <img src="{n['imagem']}" alt="{n['titulo']}">
            <span class="auto-btn">▶ ASSISTIR NA FONTE</span>
        </a>
    </div>
    """

    return f"""
    <div class="auto-post">
        <h2>{n['titulo']}</h2>
        {media_html}
        <p><b>Fonte:</b> {n['fonte']}</p>
        {texto_limpo}
        <p style="text-align:center;">
            <a href="{n['link']}" target="_blank">🔗 Leia a matéria original</a>
        </p>
        {BLOCO_FIXO_FINAL}
    </div>
    """

# =========================================================
# BUSCA DE NOTÍCIAS
# =========================================================
def buscar_noticias(tipo, limite=5):
    noticias = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")
        for entry in feed.entries:
            if not noticia_recente(entry):
                continue
            titulo = entry.get("title", "")
            texto = entry.get("summary", "")
            link = entry.get("link", "")
            if not titulo or ja_publicado(link):
                continue
            if verificar_assunto(titulo, texto) != tipo:
                continue
            noticias.append({
                "titulo": titulo,
                "texto": texto,
                "link": link,
                "fonte": fonte,
                "imagem": extrair_imagem(entry),
                "video_id": extrair_video_youtube(link),
                "labels": gerar_tags_seo(titulo, texto)
            })
    random.shuffle(noticias)
    return noticias[:limite]

# =========================================================
# 🔧 CORREÇÃO AUTOMÁTICA DE POSTS ANTIGOS
# =========================================================
def corrigir_posts_antigos(service, limite=20):
    posts = service.posts().list(blogId=BLOG_ID, maxResults=limite).execute()
    for post in posts.get("items", []):
        content = post["content"]

        # remove width, height e styles inline de imagens
        content = re.sub(r'\s(width|height|style)="[^"]*"', '', content)

        # corrige iframe quebrado
        content = re.sub(r'<iframe[^>]*></iframe>', '', content)

        service.posts().update(
            blogId=BLOG_ID,
            postId=post["id"],
            body={"content": content}
        ).execute()

        print(f"🔧 Corrigido: {post['title']}")

# =========================================================
# FLUXO PRINCIPAL
# =========================================================
def executar():
    service = autenticar_blogger()
    hora = datetime.now().hour
    tipo = "politica" if hora < 12 else "geral" if hora < 18 else "economia"

    noticias = buscar_noticias(tipo)
    for n in noticias:
        service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": n["titulo"],
                "content": gerar_conteudo(n),
                "labels": n["labels"],
                "status": "LIVE"
            }
        ).execute()
        registrar_publicacao(n["link"])
        print(f"✅ Publicado: {n['titulo']}")

    # ativa correção automática
    corrigir_posts_antigos(service)

if __name__ == "__main__":
    executar()
