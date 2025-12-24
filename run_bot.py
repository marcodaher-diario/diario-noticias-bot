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

# =============================
# BLOCO FIXO FINAL
# =============================

BLOCO_FIXO_FINAL = """<div style="text-align: right;"><span style="color: red; font-family: arial; font-size: xx-small;"><b><i><br />Por: Marco Daher</i></b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: right;"><b style="color: red; font-family: arial; font-size: x-small;">Todos os Direitos Reservados</b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: right;"><span style="color: red; font-family: arial; font-size: x-small;"><b>©MarcoDaher2025<br /><br /></b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="background-color: red; color: red; font-family: arial; font-size: small;">____________________________________________________________________________________________________________________</b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Caso queira contribuir com o BLOG e o Canal, use a&nbsp;<b><span style="color: red;">Chave PIX:</span><span style="color: #2b00fe;">&nbsp;diariodenoticiasmd@gmail.com</span></b>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;">O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.</span></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;">Aqui você encontra análise das últimas notícias e muito mais.</div><div bis_skin_checked="1" style="text-align: center;"><br />Obrigado pela Audiência.</div><div bis_skin_checked="1" style="text-align: center;">🚨 Aproveite Acesse e Inscreva-se 📌 no Canal, Não esqueça do 👍 LIKE 👍 porque isso ajuda muito a continuarmos a fazer vídeos 🎥, ative o Sininho 🔔, assim vc sempre será lembrado ⏰ quando um vídeo novo estiver no ar. Compartilhe 📢 o vídeo para mais pessoas conhecerem as informaações do canal.<br /><br /></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Muito obrigado por assistir e abraço. 🎯</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Veja também esses&nbsp;<b><span style="color: red;">LINKS&nbsp;</span></b>interessantes, e&nbsp;<b><span style="color: red;">INCREVA-SE</span></b>&nbsp;nos meus&nbsp;<b><span style="color: red;">CANAIS</span></b>:&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><div bis_skin_checked="1" style="font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><span style="color: #20124d;"><b>Diário de Notícias</b>:</span></div></span></div><div bis_skin_checked="1" style="font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;</span><a bis_skin_checked="1" href="https://dfbolhas.blogspot.com/" style="color: #992211; font-family: arial; text-decoration-line: none;">https://diariodenoticias-md.blogspot.com</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/@DiariodeNoticiasBrazuca" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/@DiariodeNoticiasBrazuca</a><br /><br /></div><div bis_skin_checked="1" style="text-align: center;"><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="color: #20124d; font-family: arial;"><b>Zona do Saber:&nbsp;</b></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="http://zonadosaber1.blogspot.com/" style="color: #992211; text-decoration-line: none;">http://zonadosaber1.blogspot.com</a></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCu9W8JOP1DkpmZUrrOsXpLg" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/channel/UCu9W8JOP1DkpmZUrrOsXpLg</a>&nbsp;</span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><br /></span></div></div></span></div></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><span style="color: #20124d;"><b>DFBolhas</b>:</span></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;</span><a bis_skin_checked="1" href="https://dfbolhas.blogspot.com/" style="color: #992211; font-family: arial; text-decoration-line: none;">https://dfbolhas.blogspot.com/</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/marcodaher51" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/marcodaher51</a></div></span><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>FaceBook</b>:&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/mdaher51/" style="color: #992211; text-decoration-line: none;">https://www.facebook.com/mdaher51</a></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><b style="font-family: arial;"><span style="color: #20124d;">Cursos, Negócios e Oportunidades:</span></b></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="https://cursosnegocioseoportunidades.blogspot.com/" style="color: #992211; text-decoration-line: none;">https://cursosnegocioseoportunidades.blogspot.com</a></div></span><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>FaceBook</b>:&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/CursosNegociosOportunidades" style="color: #992211; text-decoration-line: none;">https://www.facebook.com/CursosNegociosOportunidades</a></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><b style="font-family: arial;">YouTube</b><span style="font-family: arial;">:&nbsp;</span><a bis_skin_checked="1" href="https://www.youtube.com/@CursoseNegociosMD" style="color: #992211; font-family: arial; text-decoration-line: none;">https://www.youtube.com/@CursoseNegociosMD</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><br /></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="color: #20124d; font-family: arial; font-size: 14.85px;">Relaxamento e Meditação:&nbsp;</b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ</a>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>Marco Daher:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>YouTube</b>: h<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCZ1Ma5wezQUGcYS6hmpvaQQ" style="color: #992211; text-decoration-line: none;">ttps://www.youtube.com/channel/UCZ1Ma5wezQUGcYS6hmpvaQQ</a></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>Emagrecer com Saúde:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="https://www.emagrecendo100crise.blogspot.com/" style="color: #992211; text-decoration-line: none;">https://www.emagrecendo100crise.blogspot.com</a>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; text-align: center;"><span style="color: #333333; font-family: arial; font-size: 14.85px;"><b>FaceBook</b>:</span><span style="background-color: transparent; font-size: 14.85px; text-align: left;"><span style="font-family: arial;"><a href="https://www.facebook.com/marcocuidese"><span style="color: #660000;">https://www.facebook.com/marcocuidese</span><br /></a><br /></span></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>MD Arte Foto:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="http://mdartefoto.blogspot.com/" style="color: #992211; text-decoration-line: none;">http://mdartefoto.blogspot.com</a><br /><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="background-color: red; color: red; font-family: arial; font-size: small; text-align: right;">____________________________________________________________________________________________________________________</b></div>
"""

# =============================
# AUTENTICAÇÃO
# =============================

def autenticar_blogger():
    print("🔐 Autenticando no Blogger...")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# EXTRAIR IMAGEM DO RSS
# =============================

def extrair_imagem(entry):
    # 1️⃣ media:content
    if "media_content" in entry:
        return entry.media_content[0].get("url")

    # 2️⃣ media:thumbnail
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0].get("url")

    # 3️⃣ img dentro do summary
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    if match:
        return match.group(1)

    return None

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
# BUSCAR NOTÍCIAS
# =============================

def buscar_noticias(limite_por_feed=2):
    print("📰 Buscando notícias via RSS...")
    noticias = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:limite_por_feed]:
            imagem = extrair_imagem(entry)

            noticias.append({
                "titulo": entry.get("title", "Sem título"),
                "resumo": limpar_texto(entry.get("summary", "")),
                "link": entry.get("link", ""),
                "fonte": feed.feed.get("title", "Fonte desconhecida"),
                "imagem": imagem
            })

    print(f"✅ {len(noticias)} notícias coletadas.")
    return noticias

# =============================
# GERAR CONTEÚDO FORMATADO
# =============================

def gerar_conteudo(noticia):

    bloco_imagem = ""
    if noticia["imagem"]:
        bloco_imagem = f"""
        <div style="text-align:center;">
            <img src="{noticia['imagem']}"
                 width="680"
                 height="383"
                 style="max-width:100%; height:auto; display:block; margin:auto;" />
        </div>
        <br>
        """

    return f"""
    <div style="font-family: Arial; color:#444444; font-size:16px; text-align:justify;">

        <h2 style="font-size:26px; text-align:center;">
            {noticia['titulo']}
        </h2>

        <br>

        {bloco_imagem}

        <p><b>Fonte:</b> {noticia['fonte']}</p>

        <p>{noticia['resumo']}</p>

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
