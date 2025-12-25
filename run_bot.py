import feedparser
import re
import os
from datetime import datetime
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
PALAVRAS_POLITICA = [
    "política", "governo", "presidente", "lula", "bolsonaro",
    "congresso", "senado", "stf", "eleição", "deputado", "ministro"
]
SCOPES = ["https://www.googleapis.com/auth/blogger"]
IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

# =============================
# BLOCO FIXO FINAL
# =============================

# Seu bloco fixo mantido integralmente
BLOCO_FIXO_FINAL = """<div style="text-align: right;"><div><span style="font-family: arial; font-size: xx-small;"><b><i><span style="color: #073763;">Por: Marco Daher</span></i></b></span></div><div bis_skin_checked="1" style="background-color: white; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><b style="font-family: arial; font-size: x-small;"><span style="color: #073763;">Todos os Direitos Reservados</span></b></div><div bis_skin_checked="1" style="background-color: white; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="color: #073763; font-family: arial; font-size: x-small;"><b>©MarcoDaher2025<br /><br /></b></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="font-family: arial; font-size: small;"><span style="background-color: #073763; color: #073763;">___________________________________________________________________________________________________________________________________</span></b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="background-color: red; color: red; font-family: arial; font-size: small;"><br /></b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Caso queira contribuir com o BLOG e o Canal, use a&nbsp;<b><span style="color: red;">Chave PIX:</span><span style="color: #2b00fe;">&nbsp;diariodenoticiasmd@gmail.com</span></b>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;">O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.</span></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;">Aqui você encontra análise das últimas notícias e muito mais.</div><div bis_skin_checked="1" style="text-align: center;"><br />Obrigado pela Audiência.</div><div bis_skin_checked="1" style="text-align: center;">🚨 Aproveite Acesse e Inscreva-se 📌 no Canal, Não esqueça do 👍 LIKE 👍 porque isso ajuda muito a continuarmos a fazer vídeos 🎥, ative o Sininho 🔔, assim vc sempre será lembrado ⏰ quando um vídeo novo estiver no ar. Compartilhe 📢 o vídeo para mais pessoas conhecerem as informaações do canal.<br /><br /></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Muito obrigado por assistir e abraço. 🎯</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Veja também esses&nbsp;<b><span style="color: red;">LINKS&nbsp;</span></b>interessantes, e&nbsp;<b><span style="color: red;">INCREVA-SE</span></b>&nbsp;nos meus&nbsp;<b><span style="color: red;">CANAIS</span></b>:&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><div bis_skin_checked="1" style="font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><span style="color: #20124d;"><b>Diário de Notícias</b>:</span></div></span></div><div bis_skin_checked="1" style="font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;</span><a bis_skin_checked="1" href="https://dfbolhas.blogspot.com/" style="color: #992211; font-family: arial; text-decoration-line: none;">https://diariodenoticias-md.blogspot.com</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/@DiariodeNoticiasBrazuca" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/@DiariodeNoticiasBrazuca</a><br /><br /></div><div bis_skin_checked="1" style="text-align: center;"><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="color: #20124d; font-family: arial;"><b>Zona do Saber:&nbsp;</b></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="http://zonadosaber1.blogspot.com/" style="color: #992211; text-decoration-line: none;">http://zonadosaber1.blogspot.com</a></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCu9W8JOP1DkpmZUrrOsXpLg" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/channel/UCu9W8JOP1DkpmZUrrOsXpLg</a>&nbsp;</span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><br /></span></div></div></span></div></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><span style="color: #20124d;"><b>DFBolhas</b>:</span></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;</span><a bis_skin_checked="1" href="https://dfbolhas.blogspot.com/" style="color: #992211; font-family: arial; text-decoration-line: none;">https://dfbolhas.blogspot.com/</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/marcodaher51" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/marcodaher51</a></div></span><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>FaceBook</b>:&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/mdaher51/" style="color: #992211; text-decoration-line: none;">https://www.facebook.com/mdaher51</a></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><b style="font-family: arial;"><span style="color: #20124d;">Cursos, Negócios e Oportunidades:</span></b></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="https://cursosnegocioseoportunidades.blogspot.com/" style="color: #992211; text-decoration-line: none;">https://cursosnegocioseoportunidades.blogspot.com</a></div></span><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>FaceBook</b>:&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/CursosNegociosOportunidades" style="color: #992211; text-decoration-line: none;">https://www.facebook.com/CursosNegociosOportunidades</a></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><b style="font-family: arial;">YouTube</b><span style="font-family: arial;">:&nbsp;</span><a bis_skin_checked="1" href="https://www.youtube.com/@CursoseNegociosMD" style="color: #992211; font-family: arial; text-decoration-line: none;">https://www.youtube.com/@CursoseNegociosMD</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><br /></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="color: #20124d; font-family: arial; font-size: 14.85px;">Relaxamento e Meditação:&nbsp;</b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ</a>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>Marco Daher:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>YouTube</b>: h<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCZ1Ma5wezQUGcYS6hmpvaQQ" style="color: #992211; text-decoration-line: none;">ttps://www.youtube.com/channel/UCZ1Ma5wezQUGcYS6hmpvaQQ</a></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>Emagrecer com Saúde:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="https://www.emagrecendo100crise.blogspot.com/" style="color: #992211; text-decoration-line: none;">https://www.emagrecendo100crise.blogspot.com</a>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #444444; text-align: center;"><span style="color: #333333; font-family: arial; font-size: 14.85px;"><b>FaceBook</b>:</span><span style="background-color: transparent; font-size: 14.85px; text-align: left;"><span style="font-family: arial;"><a href="https://www.facebook.com/marcocuidese"><span style="color: #660000;">https://www.facebook.com/marcocuidese</span><br /></a><br /></span></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>MD Arte Foto:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="http://mdartefoto.blogspot.com/" style="color: #992211; text-decoration-line: none;">http://mdartefoto.blogspot.com</a><br /><br /></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><div bis_skin_checked="1" style="font-size: 14.85px;"><b style="font-family: arial; font-size: small;"><span style="background-color: #073763; color: #073763;">___________________________________________________________________________________________________________________________________</span></b></div><div><b style="font-family: arial; font-size: small;"><span style="background-color: #073763; color: #073763;"><br /></span></b></div></div></div>"""

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

def limpar_texto(html):
    if not html: return ""
    # Remove imagens e iframes do texto original para não duplicar
    html = re.sub(r"<img[^>]*>", "", html)
    html = re.sub(r"<iframe[^>]*>.*?</iframe>", "", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", "", html)
    return html.strip()

def extrair_imagem(entry):
    # Tenta várias fontes de imagem no feed
    if "media_content" in entry: return entry.media_content[0].get("url")
    if "media_thumbnail" in entry: return entry.media_thumbnail[0].get("url")
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    if match: return match.group(1)
    return IMAGEM_FALLBACK

def extrair_video_youtube(link):
    """Extrai iframe do YouTube se o link for compatível."""
    video_id = None
    if "youtube.com/watch" in link:
        video_id = link.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in link:
        video_id = link.split("youtu.be/")[1]
    
    if video_id:
        return f"""
        <div style="text-align:center; margin: 20px 0;">
            <iframe width="680" height="383" 
                src="https://www.youtube.com/embed/{video_id}" 
                frameborder="0" allowfullscreen style="max-width:100%;">
            </iframe>
        </div>"""
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

def eh_politica(titulo, texto):
    conteudo = f"{titulo} {texto}".lower()
    return any(p in conteudo for p in PALAVRAS_POLITICA)

# =============================
# GERAÇÃO DE CONTEÚDO
# =============================

def gerar_conteudo(n):
    texto_limpo = quebrar_paragrafos(n["texto"])
    video_html = extrair_video_youtube(n["link"])
    
    # Se NÃO for YouTube, criamos uma área de mídia com a imagem clicável e um botão de ação
    if not video_html:
        media_html = f"""
        <div style="text-align:center; margin: 20px 0;">
            <a href="{n['link']}" target="_blank" style="text-decoration:none;">
                <img src="{n['imagem']}" width="680" height="383" 
                     style="max-width:100%; height:auto; border-radius:10px; border: 1px solid #ddd; box-shadow: 0px 4px 8px rgba(0,0,0,0.1);">
                <div style="margin-top:15px;">
                    <span style="background-color: #cc0000; color: white; padding: 12px 25px; font-weight: bold; border-radius: 5px; font-family: Arial; display: inline-block;">
                        ▶ ASSISTIR VÍDEO COMPLETO NA FONTE
                    </span>
                </div>
            </a>
        </div>
        """
    else:
        media_html = video_html

    return f"""
    <div style="font-family:Arial; color:#444; font-size:16px; text-align:justify; line-height:1.6;">
        <h2 style="font-size:26px; text-align:center; color:#073763;">{n['titulo']}</h2>
        <hr style="border: 0; border-top: 1px solid #eee;">
        
        {media_html}
        
        <p><b>Fonte da Notícia:</b> {n['fonte']}</p>
        
        <div style="margin-top:20px;">
            {texto_limpo}
        </div>

        <p style="text-align:center; margin-top:30px;">
            <a href="{n['link']}" target="_blank" style="color: #992211; font-weight: bold;">🔗 Clique aqui para ler a matéria original</a>
        </p>

        <br>{BLOCO_FIXO_FINAL}
    </div>
    """

# =============================
# FLUXO PRINCIPAL
# =============================

def buscar_noticias(tipo, limite=2):
    print(f"📰 Buscando notícias de {tipo}...")
    noticias = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            titulo = entry.get("title", "")
            texto = limpar_texto(entry.get("summary", ""))
            link = entry.get("link", "")

            if ja_publicado(link): continue
            
            politica = eh_politica(titulo, texto)
            if tipo == "politica" and not politica: continue
            if tipo == "geral" and politica: continue

            noticias.append({
                "titulo": titulo,
                "texto": texto,
                "link": link,
                "fonte": feed.feed.get("title", "Fonte"),
                "imagem": extrair_imagem(entry)
            })
            if len(noticias) >= limite: return noticias
    return noticias

def publicar(service, noticia):
    try:
        service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": noticia["titulo"],
                "content": gerar_conteudo(noticia),
                "status": "LIVE"
            }
        ).execute()
        registrar_publicacao(noticia["link"])
        print(f"✅ Publicado: {noticia['titulo']}")
    except Exception as e:
        print(f"❌ Erro ao publicar '{noticia['titulo']}': {e}")

def executar_fluxo():
    try:
        service = autenticar_blogger()
        hora = datetime.now().hour
        tipo = "politica" if hora < 12 else "geral"
        
        noticias = buscar_noticias(tipo, limite=2)
        if not noticias:
            print("📭 Nenhuma notícia nova encontrada.")
            return

        for n in noticias:
            publicar(service, n)
    except Exception as e:
        print(f"💥 Erro fatal no fluxo: {e}")

if __name__ == "__main__":
    executar_fluxo()
