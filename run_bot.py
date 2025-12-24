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

BLOCO_FIXO_FINAL = """<div style="text-align: center;"><br /></div><div style="text-align: 
center;"><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, 
Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: right;"><span style="color: red; 
font-family: arial; font-size: x-small;"><i><b>Por: Marco Daher</b></i></span></div><div bis_skin_checked="1" 
style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; 
font-size: 14.85px; text-align: right;"><b style="color: red; font-family: arial; font-size: x-small;">Todos os Direitos Reservados</b></div><div bis_skin_checked="1" 
style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: right;"><span style="color: red; 
font-family: arial; font-size: x-small;"><b>©MarcoDaher2025<br /><br /></b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; 
font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><b style="background-color: red; color: red; 
font-family: arial; font-size: small; 
text-align: right;">________________________________________________________________ ___________________________________________</b></div>
<div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; 
text-align: right;"><br /></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, 
sans-serif; font-size: 14.85px;"><span style="font-family: arial;">Caso queira contribuir com o BLOG e o Canal, use a&nbsp;<b>
<span style="color: red;">Chave PIX:</span><span style="color: #2b00fe;">&nbsp;diariodenoticiasmd@gmail.com</span></b>&nbsp;</span></div><div bis_skin_checked="1" 
style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" 
style="text-align: center;"><span style="font-family: arial;">O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.</span></div>
<span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;">Aqui você encontra análise das últimas notícias e muito mais.</div><div bis_skin_checked="1" 
style="text-align: center;"><br />Obrigado pela Audiência.</div><div bis_skin_checked="1" 
style="text-align: center;">🚨 Aproveite Acesse e Inscreva-se 📌 no Canal, Não esqueça do 👍 LIKE 👍 porque isso ajuda muito a continuarmos a fazer vídeos 🎥, ative o Sininho 🔔, 
assim vc sempre será lembrado ⏰ quando um vídeo novo estiver no ar. Compartilhe 📢 o vídeo para mais pessoas conhecerem as informaações do canal.<br /><br /></div></span></div>
<div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;">
<span style="font-family: arial;">Muito obrigado por assistir e abraço. 🎯</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; 
font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><br /></span></div>
<div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;">
<span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, 
FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;">Veja também esses&nbsp;<b><span style="color: red;">LINKS&nbsp;</span></b>interessantes, 
e&nbsp;<b><span style="color: red;">INCREVA-SE</span></b>&nbsp;nos meus&nbsp;<b><span style="color: red;">CANAIS</span></b>:&nbsp;</span></div><div bis_skin_checked="1" 
"""

# =============================
# AUTENTICAÇÃO BLOGGER
# =============================

def autenticar_blogger():
    print("🔐 Autenticando no Blogger...")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# LIMPAR HTML DO RSS
# =============================

def limpar_html(texto):
    if not texto:
        return ""
    texto = re.sub(r"<img[^>]*>", "", texto)
    texto = re.sub(r"<iframe[^>]*>.*?</iframe>", "", texto, flags=re.DOTALL)
    texto = re.sub(r"<[^>]+>", "", texto)
    return texto.strip()

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
                "resumo": limpar_html(entry.get("summary", "")),
                "link": entry.get("link", ""),
                "fonte": feed.feed.get("title", "Fonte desconhecida")
            })

    print(f"✅ {len(noticias)} notícias coletadas.")
    return noticias

# =============================
# GERAR CONTEÚDO FORMATADO
# =============================

def gerar_conteudo(noticia):
    return f"""
    <div style="font-family: Arial; color:#444444; font-size:16px; text-align:justify;">

        <h2 style="font-size:26px; text-align:center;">
            {noticia['titulo']}
        </h2>

        <div style="height:1em;"></div>

        <div style="text-align:center;">
            <iframe 
                width="680" 
                height="383" 
                src="" 
                frameborder="0" 
                allowfullscreen
                style="max-width:100%;">
            </iframe>
        </div>

        <div style="height:1em;"></div>

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
# PUBLICAR POST
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
