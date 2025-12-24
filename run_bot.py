import feedparser
import re
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =============================
# CONFIGURAÇÕES
# =============================

BLOG_ID = "7605688984374445860"

RSS_POLITICA = [
    "https://g1.globo.com/rss/g1/politica/",
    "https://feeds.uol.com.br/politica.xml",
    "https://agenciabrasil.ebc.com.br/rss/politica"
]

RSS_GERAL = [
    "https://g1.globo.com/rss/g1/",
    "https://feeds.uol.com.br/home.xml",
    "https://agenciabrasil.ebc.com.br/rss"
]

SCOPES = ["https://www.googleapis.com/auth/blogger"]

# =============================
# AUTENTICAÇÃO BLOGGER
# =============================

def autenticar_blogger():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)

# =============================
# TAGS AUTOMÁTICAS (SEO)
# =============================

def gerar_tags(titulo, categoria):
    base_tags = []

    if categoria == "POLITICA":
        base_tags = [
            "Política", "Brasil", "Governo Federal",
            "Congresso", "STF", "Eleições", "Economia Política"
        ]
    else:
        base_tags = [
            "Notícias", "Brasil", "Atualidades",
            "Economia", "Sociedade", "Informação"
        ]

    palavras_titulo = re.findall(r"\b[A-ZÁÉÍÓÚÂÊÔÃÕÇ][a-záéíóúâêôãõç]+\b", titulo)
    base_tags.extend(palavras_titulo[:3])

    return limitar_tags(list(dict.fromkeys(base_tags)))

def limitar_tags(tags, max_chars=200):
    resultado = []
    total = 0

    for tag in tags:
        tamanho = len(tag) + 1
        if total + tamanho <= max_chars:
            resultado.append(tag)
            total += tamanho
        else:
            break

    return resultado

# =============================
# BUSCAR NOTÍCIAS RSS
# =============================

def buscar_noticias(feeds, limite_por_feed=2):
    noticias = []

    for feed_url in feeds:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries[:limite_por_feed]:
            noticias.append({
                "titulo": entry.get("title", "Sem título"),
                "resumo": limpar_html(entry.get("summary", "")),
                "link": entry.get("link", ""),
                "fonte": feed.feed.get("title", "Fonte desconhecida")
            })

    return noticias

def limpar_html(texto):
    return re.sub(r"<.*?>", "", texto)

# =============================
# FORMATAR TEXTO EM PARÁGRAFOS
# =============================

def dividir_paragrafos(texto, limite=450):
    palavras = texto.split()
    paragrafo = ""
    blocos = []

    for palavra in palavras:
        paragrafo += palavra + " "
        if len(paragrafo) >= limite:
            blocos.append(paragrafo.strip())
            paragrafo = ""

    if paragrafo:
        blocos.append(paragrafo.strip())

    return blocos

# =============================
# GERAR CONTEÚDO HTML
# =============================

def gerar_conteudo(noticia):
    paragrafos = dividir_paragrafos(noticia["resumo"])

    corpo = f"""
    <div style="font-family: Arial; font-size: medium; color:#444444; text-align: justify;">
        <h2 style="text-align:center;">{noticia['titulo']}</h2>
        <br>
    """

    for p in paragrafos:
        corpo += f"<p>{p}</p><br>"

    corpo += f"""
        <p><strong>Fonte:</strong> {noticia['fonte']}</p>
        <p>
            <a href="{noticia['link']}" target="_blank">
                🔗 Leia a matéria completa na fonte original
            </a>
        </p>
    </div>
    """

    return corpo + RODAPE_FIXO()

# =============================
# RODAPÉ FIXO
# =============================

def RODAPE_FIXO():
    return """<br>""" + """<div style="text-align: right;"><div><span style="font-family: arial; font-size: xx-small;"><b><i><span style="color: #073763;">Por: Marco Daher</span></i></b></span></div><div bis_skin_checked="1" style="background-color: white; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><b style="font-family: arial; font-size: x-small;"><span style="color: #073763;">Todos os Direitos Reservados</span></b></div><div bis_skin_checked="1" style="background-color: white; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="color: #073763; font-family: arial; font-size: x-small;"><b>©MarcoDaher2025<br /><br /></b></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="font-family: arial; font-size: small;"><span style="background-color: #073763; color: #073763;">___________________________________________________________________________________________________________________________________</span></b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="background-color: red; color: red; font-family: arial; font-size: small;"><br /></b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Caso queira contribuir com o BLOG e o Canal, use a&nbsp;<b><span style="color: red;">Chave PIX:</span><span style="color: #2b00fe;">&nbsp;diariodenoticiasmd@gmail.com</span></b>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;">O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.</span></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;">Aqui você encontra análise das últimas notícias e muito mais.</div><div bis_skin_checked="1" style="text-align: center;"><br />Obrigado pela Audiência.</div><div bis_skin_checked="1" style="text-align: center;">🚨 Aproveite Acesse e Inscreva-se 📌 no Canal, Não esqueça do 👍 LIKE 👍 porque isso ajuda muito a continuarmos a fazer vídeos 🎥, ative o Sininho 🔔, assim vc sempre será lembrado ⏰ quando um vídeo novo estiver no ar. Compartilhe 📢 o vídeo para mais pessoas conhecerem as informaações do canal.<br /><br /></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Muito obrigado por assistir e abraço. 🎯</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;">Veja também esses&nbsp;<b><span style="color: red;">LINKS&nbsp;</span></b>interessantes, e&nbsp;<b><span style="color: red;">INCREVA-SE</span></b>&nbsp;nos meus&nbsp;<b><span style="color: red;">CANAIS</span></b>:&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><div bis_skin_checked="1" style="font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><span style="color: #20124d;"><b>Diário de Notícias</b>:</span></div></span></div><div bis_skin_checked="1" style="font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;</span><a bis_skin_checked="1" href="https://dfbolhas.blogspot.com/" style="color: #992211; font-family: arial; text-decoration-line: none;">https://diariodenoticias-md.blogspot.com</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/@DiariodeNoticiasBrazuca" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/@DiariodeNoticiasBrazuca</a><br /><br /></div><div bis_skin_checked="1" style="text-align: center;"><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="color: #20124d; font-family: arial;"><b>Zona do Saber:&nbsp;</b></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="http://zonadosaber1.blogspot.com/" style="color: #992211; text-decoration-line: none;">http://zonadosaber1.blogspot.com</a></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCu9W8JOP1DkpmZUrrOsXpLg" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/channel/UCu9W8JOP1DkpmZUrrOsXpLg</a>&nbsp;</span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px;"><span style="font-family: arial;"><br /></span></div></div></span></div></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><span style="color: #20124d;"><b>DFBolhas</b>:</span></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;</span><a bis_skin_checked="1" href="https://dfbolhas.blogspot.com/" style="color: #992211; font-family: arial; text-decoration-line: none;">https://dfbolhas.blogspot.com/</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/marcodaher51" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/marcodaher51</a></div></span><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>FaceBook</b>:&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/mdaher51/" style="color: #992211; text-decoration-line: none;">https://www.facebook.com/mdaher51</a></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><b style="font-family: arial;"><span style="color: #20124d;">Cursos, Negócios e Oportunidades:</span></b></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="https://cursosnegocioseoportunidades.blogspot.com/" style="color: #992211; text-decoration-line: none;">https://cursosnegocioseoportunidades.blogspot.com</a></div></span><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><b>FaceBook</b>:&nbsp;<a bis_skin_checked="1" href="https://www.facebook.com/CursosNegociosOportunidades" style="color: #992211; text-decoration-line: none;">https://www.facebook.com/CursosNegociosOportunidades</a></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: justify;"><div bis_skin_checked="1" style="text-align: center;"><b style="font-family: arial;">YouTube</b><span style="font-family: arial;">:&nbsp;</span><a bis_skin_checked="1" href="https://www.youtube.com/@CursoseNegociosMD" style="color: #992211; font-family: arial; text-decoration-line: none;">https://www.youtube.com/@CursoseNegociosMD</a></div><span style="font-family: arial;"><div bis_skin_checked="1" style="text-align: center;"><br /></div></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><b style="color: #20124d; font-family: arial; font-size: 14.85px;">Relaxamento e Meditação:&nbsp;</b></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>YouTube</b>:&nbsp;<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" style="color: #992211; text-decoration-line: none;">https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ</a>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>Marco Daher:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>YouTube</b>: h<a bis_skin_checked="1" href="https://www.youtube.com/channel/UCZ1Ma5wezQUGcYS6hmpvaQQ" style="color: #992211; text-decoration-line: none;">ttps://www.youtube.com/channel/UCZ1Ma5wezQUGcYS6hmpvaQQ</a></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><br /></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>Emagrecer com Saúde:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="https://www.emagrecendo100crise.blogspot.com/" style="color: #992211; text-decoration-line: none;">https://www.emagrecendo100crise.blogspot.com</a>&nbsp;</span></div><div bis_skin_checked="1" style="background-color: white; color: #444444; text-align: center;"><span style="color: #333333; font-family: arial; font-size: 14.85px;"><b>FaceBook</b>:</span><span style="background-color: transparent; font-size: 14.85px; text-align: left;"><span style="font-family: arial;"><a href="https://www.facebook.com/marcocuidese"><span style="color: #660000;">https://www.facebook.com/marcocuidese</span><br /></a><br /></span></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="color: #20124d; font-family: arial;"><b>MD Arte Foto:&nbsp;</b></span></div><div bis_skin_checked="1" style="background-color: white; color: #333333; font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><span style="font-family: arial;"><b>Blog</b>:&nbsp;<a bis_skin_checked="1" href="http://mdartefoto.blogspot.com/" style="color: #992211; text-decoration-line: none;">http://mdartefoto.blogspot.com</a><br /><br /></span></div><div bis_skin_checked="1" style="font-family: Arial, Tahoma, Helvetica, FreeSans, sans-serif; font-size: 14.85px; text-align: center;"><div bis_skin_checked="1" style="font-size: 14.85px;"><b style="font-family: arial; font-size: small;"><span style="background-color: #073763; color: #073763;">___________________________________________________________________________________________________________________________________</span></b></div><div><b style="font-family: arial; font-size: small;"><span style="background-color: #073763; color: #073763;"><br /></span></b></div></div></div>"""  # Mantido intacto

# =============================
# PUBLICAR NO BLOGGER
# =============================

def publicar_post(service, titulo, conteudo, tags, horario=None):
    post = {
        "kind": "blogger#post",
        "title": titulo,
        "content": conteudo,
        "labels": tags
    }

    if horario:
        # Converte para RFC3339 com UTC (Z)
        post["published"] = horario.strftime("%Y-%m-%dT%H:%M:%SZ")

    service.posts().insert(
        blogId=BLOG_ID,
        body=post
    ).execute()

    print(f"✅ Publicado: {titulo}")

# =============================
# FLUXO PRINCIPAL
# =============================

____________________________________________________
def executar_fluxo():
    service = autenticar_blogger()

    agora = datetime.utcnow()

from datetime import datetime, timedelta

def proximo_horario(hour):
    agora = datetime.utcnow()
    horario = agora.replace(hour=hour, minute=0, second=0, microsecond=0)

    if horario <= agora:
        horario += timedelta(days=1)

    return horario

    # 🔥 POLÍTICA – MANHÃ
    noticias_politica = buscar_noticias(RSS_POLITICA)
    for i, noticia in enumerate(noticias_politica[:2]):
        horario = agora.replace(hour=8, minute=0) + timedelta(minutes=i*10)
        tags = gerar_tags(noticia["titulo"], "POLITICA")
        publicar_post(service, noticia["titulo"], gerar_conteudo(noticia), tags, horario)

    # 📰 GERAL – TARDE
    noticias_geral = buscar_noticias(RSS_GERAL)
    for i, noticia in enumerate(noticias_geral[:2]):
        horario = agora.replace(hour=14, minute=0) + timedelta(minutes=i*10)
        tags = gerar_tags(noticia["titulo"], "GERAL")
        publicar_post(service, noticia["titulo"], gerar_conteudo(noticia), tags, horario)

# =============================
# EXECUÇÃO
# =============================

if __name__ == "__main__":
    executar_fluxo()
