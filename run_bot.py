# =============================================================
# RUN_BOT.PY — BLOGGER NEWS BOT (FINAL / SAFE / PROFESSIONAL)
# =============================================================

import feedparser
import re
import os
import time
import random
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from openai import OpenAI

# =============================
# CONFIGURAÇÕES GERAIS
# =============================

BLOG_ID = "7605688984374445860"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

RSS_FEEDS = [
    "https://g1.globo.com/rss/g1/",
    "https://feeds.uol.com.br/home.xml",
    "https://rss.uol.com.br/feed/noticias.xml",
    "https://feeds.folha.uol.com.br/emcimadahora/rss091.xml",
    "https://agenciabrasil.ebc.com.br/rss",
    "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "https://www.estadao.com.br/arc/outboundfeeds/rss/category/brasil/",
    "https://www.camara.leg.br/noticias/rss/politica", 
    "https://www12.senado.leg.br/noticias/rss", 
    "https://www.infomoney.com.br/mercado/feed/", 
    "https://br.investing.com/rss/news.rss", 
    "https://portal.stf.jus.br/noticias/rss.asp", 
    "https://www.canalrural.com.br/feed/"
]

IMAGEM_FALLBACK = "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/News_icon.svg/800px-News_icon.svg.png"
ARQUIVO_LOG = "posts_publicados.txt"

PALAVRAS_POLITICA = ["Lula", "Bolsonaro", "Eleições 2026", "STF", "Congresso Nacional", "Pesquisa eleitoral", "Corrupção", "Inflação", "Reforma tributária", "Orçamento", "Segurança pública", "Senado", "Câmara dos Deputados", "Tarcísio de Freitas", "Alexandre de Moraes", "Governo Federal", "Direita", "Esquerda", "Polarização", "Fake news"]
PALAVRAS_ECONOMIA = ["Inflação", "Selic", "Dólar", "PIB", "IPCA", "Boletim Focus", "Reforma Tributária", "Bolsa de Valores", "Ibovespa", "Preço dos combustíveis", "Imposto de Renda 2026", "Salário Mínimo", "Juros", "Dívida Pública", "Câmbio", "Cesta Básica", "Corte de Gastos", "Mercado Financeiro", "Arrecadação", "Renda Fixa"]

# =============================
# AUTENTICAÇÃO BLOGGER
# =============================

def autenticar_blogger():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# CONTROLE DE DUPLICAÇÃO
# =============================

def ja_publicado(link):
    if not os.path.exists(ARQUIVO_LOG):
        return False
    with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
        return link in f.read()

def registrar_publicacao(link):
    with open(ARQUIVO_LOG, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# ===============================
# TAGS — LIMITE 200 CARACTERES
# ===============================

def gerar_tags_blogger(tags, limite=200):
    tags_limpas = []
    total = 0
    for tag in tags:
        tag = tag.strip()
        if not tag or tag.lower() in [t.lower() for t in tags_limpas]:
            continue
        if total + len(tag) > limite:
            break
        tags_limpas.append(tag)
        total += len(tag)
    return tags_limpas

# =============================
# EXTRAÇÃO DE IMAGEM
# =============================

def extrair_imagem(entry):
    if hasattr(entry, "media_content"):
        return entry.media_content[0].get("url")
    if hasattr(entry, "media_thumbnail"):
        return entry.media_thumbnail[0].get("url")
    summary = entry.get("summary", "")
    match = re.search(r'<img[^>]+src="([^">]+)"', summary)
    return match.group(1) if match else None

# =============================
# DETECÇÃO DE CONTEÚDO FRACO
# =============================

def conteudo_invalido(texto):
    texto_limpo = re.sub(r"<[^>]+>", "", texto).strip()
    if len(texto_limpo) < 150:
        return True
    if "<iframe" in texto.lower() or "youtube" in texto.lower():
        return True
    return False

# =============================
# CLASSIFICAÇÃO
# =============================

def classificar_noticia(titulo, texto):
    base = f"{titulo} {texto}".lower()
    if any(p in base for p in PALAVRAS_POLITICA):
        return "politica"
    if any(p in base for p in PALAVRAS_ECONOMIA):
        return "economia"
    return "geral"

# =============================
# IA — GERAÇÃO DE TEXTO
# =============================

def gerar_texto_ia(titulo, categoria):
    try:
        client = OpenAI()

        resposta = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um jornalista imparcial que escreve notícias informativas e claras."
                },
                {
                    "role": "user",
                    "content": f"Escreva um texto jornalístico imparcial sobre o tema: {titulo}. Categoria: {categoria}."
                }
            ],
            max_tokens=300
        )

        return resposta.choices[0].message.content.strip()

    except Exception as e:
        print(f"⚠️ IA indisponível: {e}")
        return f"<p>Matéria em atualização sobre: <b>{titulo}</b>.</p>"

# ===============================
# FORMATAÇÃO HTML (JUSTIFICADO)
# ===============================

def formatar_texto(texto):
    frases = re.split(r'(?<=[.!?])\s+', texto)
    blocos = []
    temp = []
    for frase in frases:
        temp.append(frase)
        if len(temp) >= 2:
            blocos.append(" ".join(temp))
            temp = []
    if temp:
        blocos.append(" ".join(temp))
    return "".join(
        f"<p style='text-align:justify; font-size:16px; line-height:1.6;'>{b}</p>"
        for b in blocos
    )


# ==========================================
# FUNÇÃO — ASSINATURA COM ÍCONES + PIX
# ==========================================

def obter_assinatura():
    # A variável começa sem espaços extras antes das aspas triplas
    assinatura_html = """<div class="footer-marco-daher" style="color: #073763; font-family: Arial, Helvetica, sans-serif; line-height: 1.4; margin-top: 30px; text-align: center; background-color: #e1f5fe; padding: 25px; border-radius: 15px; border: 1px solid #b3e5fc;">
  <p style="font-size: x-small; font-weight: bold; text-align: right; margin-top: 0;">
    <i>Por: Marco Daher<br />Todos os Direitos Reservados<br />©MarcoDaher2025</i>
  </p>
  <p style="font-size: 16px; font-weight: bold; margin-bottom: 20px;">
    O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.
  </p>
  <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 20px 0;">
    <div style="text-align: center; padding: 10px; border-right: 1px solid #07376333; min-width: 120px;">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #b45f06;">Zona do Saber</div>
      <a href="http://zonadosaber1.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" title="Blogger" /></a>
      <a href="https://www.youtube.com/@ZonadoSaber51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" title="YouTube" /></a>
      <a href="https://www.facebook.com/profile.php?id=61558194825166" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" title="Facebook" /></a>
    </div>
    <div style="text-align: center; padding: 10px; border-right: 1px solid #07376333; min-width: 120px;">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #b45f06;">MD Arte Foto</div>
      <a href="https://mdartefoto.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="text-align: center; padding: 10px; border-right: 1px solid #07376333; min-width: 120px;">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #b45f06;">DF Bolhas</div>
      <a href="https://dfbolhas.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/marcodaher51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="text-align: center; padding: 10px; border-right: 1px solid #07376333; min-width: 120px;">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #b45f06;">Marco Daher</div>
      <a href="https://www.youtube.com/@MarcoDaher" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/MarcoDaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="text-align: center; padding: 10px; border-right: 1px solid #07376333; min-width: 120px;">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #b45f06;">Emagrecer com Saúde</div>
      <a href="https://emagrecendo100crise.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/@Saude-Bem-Estar-51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/marcocuidese" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="text-align: center; padding: 10px; border-right: 1px solid #07376333; min-width: 120px;">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #b45f06;">Relaxamento</div>
      <a href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="text-align: center; padding: 10px; min-width: 120px;">
      <div style="font-size: 13px; font-weight: bold; margin-bottom: 5px; color: #b45f06;">Cursos e Negócios</div>
      <a href="https://cursosnegocioseoportunidades.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/@CursoseNegociosMD" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a> 
      <a href="https://www.facebook.com/CursosNegociosOportunidades" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
  </div>
  <hr style="border: 0; border-top: 1px solid #07376322; margin: 20px 0;">
  <p style="font-size: 14px; font-weight: bold; margin-bottom: 10px;">
    Caso queira contribuir com o meu Trabalho, use a CHAVE PIX abaixo:
  </p>
  <button onclick="navigator.clipboard.writeText('marco.caixa104@gmail.com'); alert('Chave PIX copiada!');" style="background-color: #0288d1; border-radius: 8px; border: none; color: white; cursor: pointer; font-size: 14px; font-weight: bold; padding: 12px 20px; transition: 0.3s; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
    Copiar Chave PIX: marco.caixa104@gmail.com
  </button>
</div>"""

    return assinatura_html


# =============================
# BUSCA DE NOTÍCIAS
# =============================

def noticia_recente(entry, horas=48):
    data = entry.get("published_parsed") or entry.get("updated_parsed")
    if not data:
        return False
    return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)

def buscar_noticias():
    noticias = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        fonte = feed.feed.get("title", "Fonte")
        for entry in feed.entries:
            if not noticia_recente(entry):
                continue

            titulo = entry.get("title", "").strip()
            resumo = entry.get("summary", "")
            link = entry.get("link", "")

            if not titulo or not link or ja_publicado(link):
                continue

            categoria = classificar_noticia(titulo, resumo)

            if conteudo_invalido(resumo):
                if categoria in ["politica", "economia"]:
                    texto = gerar_texto_ia(titulo, categoria)
                else:
                    continue
            else:
                texto = re.sub(r"<[^>]+>", "", resumo)

            imagem = extrair_imagem(entry) or IMAGEM_FALLBACK

            noticias.append({
                "titulo": titulo,
                "texto": texto,
                "link": link,
                "fonte": fonte,
                "imagem": imagem,
                "categoria": categoria
            })
    random.shuffle(noticias)
    return noticias[:3]

# =============================
# GERAÇÃO DO POST
# =============================

def gerar_html(n):
    return f"""
<h2 style="text-align:center;">{n['titulo']}</h2>

<div style="text-align:center; margin:20px 0;">
    <img src="{n['imagem']}" alt="{n['titulo']}" style="max-width:100%;">
</div>

<p style="text-align:center; font-size:14px;">
<b>Fonte:</b> {n['fonte']}
</p>

{formatar_texto(n['texto'])}

<p style="text-align:center;">
<a href="{n['link']}" target="_blank">Leia a matéria original</a>
</p>

{gerar_assinatura()}
"""

# =============================
# EXECUÇÃO
# =============================

def executar():
    service = autenticar_blogger()
    noticias = buscar_noticias()

    for n in noticias:
        try:
            service.posts().insert(
                blogId=BLOG_ID,
                body={
                    "title": n["titulo"],
                    "content": gerar_html(n),
                    "labels": gerar_tags_blogger(
                        n["titulo"].lower().split()
                    ),
                    "status": "LIVE"
                }
            ).execute()

            registrar_publicacao(n["link"])
            print(f"✅ Publicado: {n['titulo']}")

        except Exception as e:
            print(f"❌ Erro ao publicar: {e}")

if __name__ == "__main__":
    executar()
