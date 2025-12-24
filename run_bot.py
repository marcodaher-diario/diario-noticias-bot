import feedparser
import re
import os  # Faltava este
from datetime import datetime # Faltava este
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
# Imagem em 16:9 conforme sua preferência
IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

# ... (Mantenha seu BLOCO_FIXO_FINAL aqui) ...
BLOCO_FIXO_FINAL = """...""" 

# =============================
# AUTENTICAÇÃO E UTILITÁRIOS
# =============================

def autenticar_blogger():
    print("🔐 Autenticando no Blogger...")
    if not os.path.exists("token.json"):
        raise FileNotFoundError("O arquivo token.json não foi encontrado.")
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG):
        return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

def extrair_imagem(entry):
    if "media_content" in entry:
        return entry.media_content[0].get("url")
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0].get("url")
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    if match: return match.group(1)
    return IMAGEM_FALLBACK

def limpar_texto(html):
    if not html: return ""
    html = re.sub(r"<img[^>]*>", "", html)
    html = re.sub(r"<iframe[^>]*>.*?</iframe>", "", html, flags=re.DOTALL)
    html = re.sub(r"<[^>]+>", "", html)
    return html.strip()

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
# BUSCA E PROCESSAMENTO (CORRIGIDO)
# =============================

def buscar_noticias(tipo, limite=5): # Adicionado 'tipo' e 'limite'
    print(f"📰 Buscando notícias de {tipo} via RSS...")
    noticias = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            titulo = entry.get("title", "")
            # Corrigido de limpar_html para limpar_texto
            texto = limpar_texto(entry.get("summary", ""))
            link = entry.get("link", "")

            if ja_publicado(link): continue

            politica = eh_politica(titulo, texto)

            # Lógica de filtragem corrigida
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

def gerar_conteudo(n):
    texto_formatado = quebrar_paragrafos(n["texto"])
    return f"""
    <div style="font-family:Arial; color:#444; font-size:16px; text-align:justify;">
        <h2 style="font-size:26px; text-align:center;">{n['titulo']}</h2><br>
        <div style="text-align:center;">
            <img src="{n['imagem']}" width="680" height="383" style="max-width:100%; height:auto; margin:auto;">
        </div><br>
        <p><b>Fonte:</b> {n['fonte']}</p>
        {texto_formatado}
        <p><a href="{n['link']}" target="_blank">🔗 Leia na fonte original</a></p>
        <br>{BLOCO_FIXO_FINAL}
    </div>
    """

def publicar(service, noticia):
    try:
        service.posts().insert(
            blogId=BLOG_ID,
            body={
                "title": noticia["titulo"],
                "content": gerar_conteudo(noticia),
            }
        ).execute()
        registrar_publicacao(noticia["link"])
        print(f"✅ Publicado: {noticia['titulo']}")
    except Exception as e:
        print(f"❌ Erro ao publicar: {e}")

def executar_fluxo():
    service = autenticar_blogger()
    hora = datetime.now().hour
    
    # Define o tipo com base na hora
    tipo = "politica" if hora < 12 else "geral"
    
    noticias = buscar_noticias(tipo, limite=2)
    for n in noticias:
        publicar(service, n)

if __name__ == "__main__":
    executar_fluxo()
