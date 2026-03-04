# ==========================================
# CONFIGURAÇÕES GERAIS DO BLOG
# ==========================================

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
    "https://g1.globo.com/rss/g1/economia/",
    "https://www.camara.leg.br/noticias/rss/ultimas-noticias",
    "https://www.camara.leg.br/noticias/rss/dinamico/POLITICA",
    "https://www12.senado.leg.br/noticias/ultimas",
    "https://news.google.com/rss/search?q=site:metropoles.com+intitle:política&hl=pt-BR&gl=BR&ceid=BR:pt-419"
]

# ==========================================
# TEMAS PARA POSTAGEM (SISTEMA DE PESOS)
# ==========================================

PESOS_POR_TEMA = {
    "policial": {
        "chacina": 12, "homicídio": 12, "assassinato": 11, "latrocínio": 11,
        "operação": 10, "prisão": 10, "preso": 9, "fuzil": 10, "tráfico": 9,
        "investigação": 8, "mandado": 8, "flagrante": 9, "confronto": 8,
        "crime": 5, "suspeito": 5, "delegacia": 4, "ocorrência": 4, "polícia": 5
    },
    "politica": {
        "stf": 12, "supremo": 12, "impeachment": 12, "planalto": 10, 
        "congresso": 10, "senado": 9, "câmara": 9, "ministro": 10,
        "votação": 8, "reforma": 9, "partido": 7, "eleição": 10,
        "governo": 6, "oposição": 6, "política": 5, "base": 4, "cpi": 11
    },
    "economia": {
        "inflação": 12, "selic": 12, "juros": 10, "dólar": 11, 
        "pib": 10, "recessão": 12, "bolsa": 9, "ibovespa": 9,
        "ipca": 11, "deficit": 10, "mercado": 7, "investimento": 7,
        "economia": 5, "banco": 6, "consumo": 4, "varejo": 4
    }
}

# ==========================================
# CONFIGURAÇÃO DE CONTROLE
# ==========================================

ARQUIVO_CONTROLE_AGENDAMENTO = "controle_agendamentos.txt"
ARQUIVO_CONTROLE_TEMAS = "controle_temas_usados.txt"
ARQUIVO_CONTROLE_IMAGENS = "controle_imagens.txt"

DIAS_BLOQUEIO_TEMA = 20
DIAS_BLOQUEIO_IMAGEM = 30

# ==========================================
# CONFIGURAÇÃO GEMINI
# ==========================================

MODELO_GEMINI = "gemini-3-flash-preview"

# Parâmetros de Redação
MIN_PALAVRAS = 600
MAX_PALAVRAS = 800

# Parâmetros de Resiliência (Evitar erro 429 - Muitos Acessos)
MAX_TENTATIVAS = 4          # Tenta 4 vezes antes de desistir do modelo atual
TEMPO_ESPERA_SEGUNDOS = 30  # Espera 30 segundos entre cada tentativa

# ==========================================
# BLOCO FIXO FINAL -  ASSINATURA
# ==========================================

BLOCO_FIXO_FINAL = """
<div class="footer-marco-daher" style="background-color: #e1f5fe; border-radius: 15px; border: 1px solid rgb(179, 229, 252); color: #073763 !important; font-family: Arial, Helvetica, sans-serif !important; font-size: 14px !important; font-weight: normal !important; line-height: 1.4 !important; margin-top: 10px; padding: 25px; text-align: center;">
  
  <p style="font-size: x-small !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; color: #073763 !important; margin-top: 0px; text-align: right;">
    <i>Por: Marco Daher<br />Todos os Direitos Reservados<br />©MarcoDaher2026</i>
  </p>

  <div class="separator" style="clear: both; margin: 15px 0px; text-align: center;">
    <a href="https://s.shopee.com.br/9zs5JZLPNm" target="_blank">
      <img border="0" height="132" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhHYBTRiztv4UNKBsiwX8nQn1M00BUz-LtO58gTZ6hEsU3VPClePhQwPWw0NyUJGqXvm3vWbRPP6LPQS6m5iyI0UQBBKmdIkNYNuXmGaxv5eMac9R6i2e9MIU7_YmWeMKntQ1ZWlzplYlDYNJr5lGHiUvwJ1CuvQOLzbOT61kF3LQ0-nD4j3Xo4HJWeOG4/w640-h132/Banner%20Shopee%20Rodap%C3%A9.gif" style="height: auto; max-width: 100%;" width="640" />
    </a>
  </div>

  <div style="margin-bottom: 20px; text-align: center;">
    <p style="font-weight: bold !important; font-size: 15px !important; font-family: Arial, Helvetica, sans-serif !important; color: #073763 !important; margin-bottom: 10px; text-align: center;">🚀 Gostou deste conteúdo? Não guarde só para você!</p>
    <a href="https://api.whatsapp.com/send?text=Confira este artigo incrível no blog do Marco Daher!" style="background-color: #25d366; border-radius: 5px; color: white !important; display: inline-block; font-weight: bold !important; font-size: 14px !important; font-family: Arial, Helvetica, sans-serif !important; padding: 10px 20px; text-decoration: none;" target="_blank">
        Compartilhar no WhatsApp
    </a>
  </div>

  <p style="font-size: 16px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; color: #073763 !important; margin-bottom: 20px; text-align: center;">
    O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.
  </p>

  <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 20px 0px;">

    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">Zona do Saber</div>
      <a href="http://zonadosaber1.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/@ZonadoSaber51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/profile.php?id=61558194825166" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>

    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">MD Arte Foto</div>
      <a href="https://mdartefoto.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>

    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">DF Bolhas</div>
      <a href="https://dfbolhas.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/marcodaher51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>

    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">Marco Daher</div>
      <a href="https://www.youtube.com/@MarcoDaher" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/MarcoDaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>

    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">Diário de Notícias</div>
      <a href="https://diariodenoticias-md.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/@DiariodeNoticiasBrazuca" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
    </div>

    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">Emagrecer com Saúde</div>
      <a href="https://emagrecendo100crise.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/@Saude-Bem-Estar-51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/marcocuidese" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>

    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">Relaxamento</div>
      <a href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
    </div>

    <div style="min-width: 120px; padding: 10px;">
      <div style="color: #b45f06 !important; font-size: 13px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; margin-bottom: 5px;">Cursos e Negócios</div>
      <a href="https://cursosnegocioseoportunidades.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.youtube.com/@CursoseNegociosMD" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
      <a href="https://www.facebook.com/CursosNegociosOportunidades" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>

  </div>

  <hr style="border-top: 1px solid rgba(7, 55, 99, 0.133); margin: 20px 0px;" />

  <p style="font-size: 14px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; color: #073763 !important; margin-bottom: 10px;">
    Caso queira contribuir com o meu Trabalho, use a CHAVE PIX abaixo:
  </p>

  <button onclick="navigator.clipboard.writeText('marco.caixa104@gmail.com'); alert('Chave PIX copiada!');" style="background-color: #0288d1; border-radius: 8px; border: none; box-shadow: rgba(0, 0, 0, 0.2) 0px 2px 4px; color: white !important; cursor: pointer; font-size: 14px !important; font-weight: bold !important; font-family: Arial, Helvetica, sans-serif !important; padding: 12px 20px; transition: 0.3s;">
    Copiar Chave PIX: marco.caixa104@gmail.com
  </button>

</div>
<hr style="text-align: justify;" />
<h2 style="text-align: justify;"><br /></h2>
"""
