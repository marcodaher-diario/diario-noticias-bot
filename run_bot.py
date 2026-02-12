Código completo ORIGINAL do ROBO Diário de Notícias (quase funcional)

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
    "https://rss.uol.com.br/feed/noticias.xml",
    "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://agenciabrasil.ebc.com.br/rss",
    "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.gazetadopovo.com.br/feed/rss/brasil.xml",
    "https://reporterbrasil.org.br/feed/",
    "https://www.cnnbrasil.com.br/feed/",
    "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
    "https://g1.globo.com/rss/g1/economia/"
]

PALAVRAS_POLITICA = ["política", "governo", "presidente", "lula", "bolsonaro", "congresso", "senado", "stf", "eleição", "moraes", "toffoli", "fux", "Dino", "flavio", "eduardo", "depoimento", "magistrados", "juízes", "ex-presidente", "corrupção", "vereadores", "deputado", "senador", "PGR", "ministério público"]
PALAVRAS_ECONOMIA = ["economia", "pib", "dólar", "euro", "inflação", "selic", "mercado", "bolsa de valores", "banco central"]

SCOPES = ["https://www.googleapis.com/auth/blogger"]
IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

# ====================================
#      ASSINATURA COM BANNER E REDES 
# ====================================

BLOCO_FIXO_FINAL = """
<div class="footer-marco-daher" style="background-color: #e1f5fe; border-radius: 15px; border: 1px solid rgb(179, 229, 252); color: #073763; font-family: Arial, Helvetica, sans-serif; line-height: 1.4; margin-top: 10px; padding: 25px; text-align: center;">
  
  <p style="font-size: x-small; font-weight: bold; margin-top: 0px; text-align: right;">
    <i>Por: Marco Daher<br />Todos os Direitos Reservados<br />©MarcoDaher2026</i>
  </p>

  <div class="separator" style="clear: both; margin: 15px 0px; text-align: center;">
    <a href="https://s.shopee.com.br/9zs5JZLPNm">
      <img border="0" height="132" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhHYBTRiztv4UNKBsiwX8nQn1M00BUz-LtO58gTZ6hEsU3VPClePhQwPWw0NyUJGqXvm3vWbRPP6LPQS6m5iyI0UQBBKmdIkNYNuXmGaxv5eMac9R6i2e9MIU7_YmWeMKntQ1ZWlzplYlDYNJr5lGHiUvwJ1CuvQOLzbOT61kF3LQ0-nD4j3Xo4HJWeOG4/w640-h132/Banner%20Shopee%20Rodap%C3%A9.gif" style="height: auto; max-width: 100%;" width="640" />
    </a>
  </div>

  <div style="margin-bottom: 20px;">
    <p style="font-weight: bold; margin-bottom: 10px;">🚀 Gostou deste conteúdo? Não guarde só para você!</p>
    <a href="https://api.whatsapp.com/send?text=Confira este artigo incrível no blog do Marco Daher!" style="background-color: #25d366; border-radius: 5px; color: white; display: inline-block; font-weight: bold; padding: 10px 20px; text-decoration: none;" target="_blank">
        Compartilhar no WhatsApp
    </a>
  </div>

  <p style="font-size: 16px; font-weight: bold; margin-bottom: 20px;">
    O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.
  </p>

  <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 20px 0px;">
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Zona do Saber</div>
      <a href="http://zonadosaber1.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" title="Blogger" /></a>&nbsp;<a href="https://www.youtube.com/@ZonadoSaber51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" title="YouTube" /></a>&nbsp;<a href="https://www.facebook.com/profile.php?id=61558194825166" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" title="Facebook" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">MD Arte Foto</div>
      <a href="https://mdartefoto.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">DF Bolhas</div>
      <a href="https://dfbolhas.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/marcodaher51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Marco Daher</div>
      <a href="https://www.youtube.com/@MarcoDaher" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/MarcoDaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Diário de Notícias</div>
      <a href="https://diariodenoticias-md.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/@DiariodeNoticiasBrazuca" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Emagrecer com Saúde</div>
      <a href="https://emagrecendo100crise.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/@Saude-Bem-Estar-51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/marcocuidese" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" title="Facebook" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Relaxamento</div>
      <a href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Cursos e Negócios</div>
      <a href="https://cursosnegocioseoportunidades.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/@CursoseNegociosMD" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/CursosNegociosOportunidades" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
  </div>

  <hr style="border-bottom: 0px; border-image: initial; border-left: 0px; border-right: 0px; border-top: 1px solid rgba(7, 55, 99, 0.133); border: 0px; margin: 20px 0px;" />
  <p style="font-size: 14px; font-weight: bold; margin-bottom: 10px;">Caso queira contribuir com o meu Trabalho, use a CHAVE PIX abaixo:</p>
  <button style="background-color: #0288d1; border-radius: 8px; border: none; box-shadow: rgba(0, 0, 0, 0.2) 0px 2px 4px; color: white; cursor: pointer; font-size: 14px; font-weight: bold; padding: 12px 20px;">
    Chave PIX: marco.caixa104@gmail.com
  </button>
</div>
</div></div>
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


# =======================================
#      GERAR TAGS RELACIONADAS 200 CHAR
# =======================================

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

# ====================================
#      GERAR IMAGENS E VÍDEOS
# ====================================

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

# ====================================
#      QUEBRAR PARAGRAFOS 
# ====================================

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

def buscar_noticias(tipo_alvo, limite=4):
    print(f"📰 Buscando notícias do tipo: {tipo_alvo}...")
    noticias = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")

        for entry in feed.entries:
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

    # 🔀 embaralha todas as fontes
    random.shuffle(noticias)

    # ✂️ corta no limite desejado
    return noticias[:limite]
if __name__ == "__main__":
    executar_fluxo()


