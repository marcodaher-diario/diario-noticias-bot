import feedparser
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

# =============================
# AUTENTICAÇÃO BLOGGER
# =============================

def autenticar_blogger():
    print("🔐 Autenticando no Blogger...")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# BLOCO PADRÃO DE IMAGEM (680x383)
# =============================

def bloco_imagem(url):
    if not url:
        return ""

    return f"""
    <div style="text-align:center; margin:20px 0;">
        <img src="{url}"
             style="
                width:680px;
                height:383px;
                max-width:100%;
                object-fit:cover;
                display:block;
                margin:0 auto;
             ">
    </div>
    """

# =============================
# BUSCAR NOTÍCIAS (RSS)
# =============================

def buscar_noticias(limite_por_feed=2):
    print("📰 Buscando notícias via RSS...")
    noticias = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:limite_por_feed]:

            imagem = ""

            # tenta pegar imagem do RSS (quando existir)
            if "media_content" in entry:
                imagem = entry.media_content[0].get("url", "")
            elif "media_thumbnail" in entry:
                imagem = entry.media_thumbnail[0].get("url", "")

            noticias.append({
                "titulo": entry.get("title", "Sem título"),
                "resumo": entry.get("summary", ""),
                "link": entry.get("link", ""),
                "fonte": feed.feed.get("title", "Fonte desconhecida"),
                "imagem": imagem
            })

    print(f"✅ {len(noticias)} notícias coletadas.")
    return noticias

# =============================
# GERAR CONTEÚDO (CURADORIA)
# =============================

def gerar_conteudo(noticia):
    imagem_html = bloco_imagem(noticia.get("imagem"))

    return f"""
    <p><strong>Fonte:</strong> {noticia['fonte']}</p>

    {imagem_html}

    <p>{noticia['resumo']}</p>

    <p style="text-align:center; margin-top:20px;">
        <a href="{noticia['link']}" target="_blank">
            🔗 Leia a matéria completa na fonte original
        </a>
    </p>
    """

# =============================
# PUBLICAR NO BLOGGER
# =============================

def publicar_post(service, titulo, conteudo):
    post = {
        "kind": "blogger#post",
        "title": titulo,
        "content": conteudo,
        "status": "LIVE"
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post
    ).execute()

    print(f"🚀 Post publicado: {titulo}")

# =============================
# FLUXO PRINCIPAL
# =============================

def executar_fluxo():
    print("▶️ Fluxo iniciado")
    service = autenticar_blogger()
    noticias = buscar_noticias()

    if not noticias:
        print("⚠️ Nenhuma notícia encontrada.")
        return

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

