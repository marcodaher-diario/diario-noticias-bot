import feedparser
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =============================
# CONFIGURAÇÕES
# =============================

BLOG_ID = "7605688984374445860"

RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/",
    "https://feeds.uol.com.br/home.xml",
    "https://agenciabrasil.ebc.com.br/rss"
]

SCOPES = ["https://www.googleapis.com/auth/blogger"]

IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"

# =============================
# BLOCO FIXO FINAL
# =============================

BLOCO_FIXO_FINAL = """COLE AQUI O SEU BLOCO FIXO EXATAMENTE COMO VOCÊ ENVIOU"""

# =============================
# AUTENTICAÇÃO
# =============================

def autenticar_blogger():
    print("🔐 Autenticando no Blogger...")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# EXTRAIR IMAGEM
# =============================

def extrair_imagem(entry):
    if "media_content" in entry:
        return entry.media_content[0].get("url")

    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0].get("url")

    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    if match:
        return match.group(1)

    return IMAGEM_FALLBACK

# =============================
# EXTRAIR VÍDEO YOUTUBE
# =============================

def extrair_video(link):
    if "youtube.com/watch" in link or "youtu.be/" in link:
        video_id = None

        if "watch?v=" in link:
            video_id = link.split("watch?v=")[1].split("&")[0]
        elif "youtu.be/" in link:
            video_id = link.split("youtu.be/")[1]

        if video_id:
            return f"""
            <div style="text-align:center;">
                <iframe width="680" height="383"
                    src="https://www.youtube.com/embed/{video_id}"
                    frameborder="0"
                    allowfullscreen>
                </iframe>
            </div>
            <br>
            """
    return ""

# =============================
# LIMPAR TEXTO
# =============================

def limpar_texto(html):
    if not html:
        return ""
    html = re.sub(r"<img[^>]*>", "", html)
    html = re.sub(r"<iframe[^>]*>.*?</iframe>", "", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", "", html)
    return html.strip()

# =============================
# QUEBRAR TEXTO EM PARÁGRAFOS
# =============================

def quebrar_paragrafos(texto):
    frases = re.split(r'(?<=[.!?]) +', texto)
    paragrafos = []
    bloco = []

    for frase in frases:
        bloco.append(frase)
        if len(bloco) >= 2:
            paragrafos.append(" ".join(bloco))
            bloco = []

    if bloco:
        paragrafos.append(" ".join(bloco))

    return "".join(f"<p>{p}</p><br>" for p in paragrafos)

# =============================
# BUSCAR NOTÍCIAS
# =============================

def buscar_noticias(limite_por_feed=2):
    print("📰 Buscando notícias via RSS...")
    noticias = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:limite_por_feed]:
            noticias.append({
                "titulo": entry.get("title", "Sem título"),
                "texto": limpar_texto(entry.get("summary", "")),
                "link": entry.get("link", ""),
                "fonte": feed.feed.get("title", "Fonte desconhecida"),
                "imagem": extrair_imagem(entry),
                "video": extrair_video(entry.get("link", ""))
            })

    print(f"✅ {len(noticias)} notícias coletadas.")
    return noticias

# =============================
# GERAR CONTEÚDO
# =============================

def gerar_conteudo(noticia):

    bloco_midia = noticia["video"]

    if not bloco_midia:
        bloco_midia = f"""
        <div style="text-align:center;">
            <img src="{noticia['imagem']}"
                 width="680"
                 height="383"
                 style="max-width:100%; height:auto; display:block; margin:auto;" />
        </div>
        <br>
        """

    texto_formatado = quebrar_paragrafos(noticia["texto"])

    return f"""
    <div style="font-family: Arial; color:#444444; font-size:16px; text-align:justify;">

        <h2 style="font-size:26px; text-align:center;">
            {noticia['titulo']}
        </h2>

        <br>

        {bloco_midia}

        <p><b>Fonte:</b> {noticia['fonte']}</p>

        {texto_formatado}

        <p>
            <a href="{noticia['link']}" target="_blank">
                🔗 Leia a matéria completa na fonte original
            </a>
        </p>

        <br><br>

        {BLOCO_FIXO_FINAL}

    </div>
    """

# =============================
# PUBLICAR
# =============================

def publicar_post(service, titulo, conteudo):
    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "kind": "blogger#post",
            "title": titulo,
            "content": conteudo,
            "status": "LIVE"
        }
    ).execute()

    print(f"🚀 Post publicado: {titulo}")

# =============================
# FLUXO PRINCIPAL
# =============================

def executar_fluxo():
    print("▶️ Fluxo iniciado")
    service = autenticar_blogger()
    noticias = buscar_noticias()

    for noticia in noticias:
        publicar_post(
            service,
            noticia["titulo"],
            gerar_conteudo(noticia)
        )

    print("🏁 Fluxo finalizado com sucesso")

# =============================
# EXECUÇÃO
# =============================

if __name__ == "__main__":
    executar_fluxo()
