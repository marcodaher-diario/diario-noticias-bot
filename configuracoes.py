# ==========================================
# CONFIGURAÇÕES GERAIS DO BLOG
# ==========================================

BLOG_ID = "7605688984374445860"


# ==========================================
# FONTES RSS
# ==========================================

RSS_FEEDS = [
    # FONTES GERAIS
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

    # ECONOMIA E FINANÇAS
    "https://g1.globo.com/rss/g1/economia/",

    # POLÍTICA E GOVERNO
    "https://www.camara.leg.br/noticias/rss/ultimas-noticias",
    "https://www.camara.leg.br/noticias/rss/dinamico/POLITICA",
    "https://www12.senado.leg.br/noticias/ultimas",
    "https://news.google.com/rss/search?q=site:metropoles.com+intitle:política&hl=pt-BR&gl=BR&ceid=BR:pt-419",

    # SAÚDE E SOCIEDADE
    "https://agenciabrasil.ebc.com.br/rss/saude/feed.xml",
    "https://agenciabrasil.ebc.com.br/rss/educacao/feed.xml",
    "https://agenciabrasil.ebc.com.br/rss/direitos-humanos/feed.xml",

    # TECNOLOGIA E CIÊNCIA
    "https://g1.globo.com/rss/g1/tecnologia/",
    "https://agenciabrasil.ebc.com.br/radioagencia-nacional/rss/pesquisa-e-inovacao/feed.xml"
]


# ==========================================
# TEMAS PARA POSTAGEM (SISTEMA DE PESOS)
# ==========================================

PESOS_POR_TEMA = {

    # --------------------------------------
    # SEGURANÇA E POLÍCIA
    # --------------------------------------

    "policial": {
        "chacina": 12,
        "homicidio": 12,
        "assassinato": 11,
        "latrocinio": 11,
        "operacao policial": 12,
        "operacao": 10,
        "prisao": 10,
        "prisoes": 10,
        "preso": 9,
        "fuzil": 10,
        "trafico": 9,
        "investigacao": 8,
        "mandado": 8,
        "flagrante": 9,
        "confronto": 8,
        "crime": 5,
        "criminoso": 6,
        "suspeito": 5,
        "delegacia": 4,
        "ocorrencia": 4,
        "policia": 5,
        "policial": 6,
        "assalto": 8,
        "roubo": 8,
        "furto": 7,
        "sequestro": 10,
        "estupro": 10,
        "violencia": 6,
        "milicia": 9,
        "faccao criminosa": 10,
        "faccao": 9,
        "batalhao": 5,
        "policia federal": 8,
        "policia civil": 8,
        "policia militar": 8,
        "policia rodoviaria": 8,
        "policia penal": 8,
        "foragido": 8,
        "receptacao": 7,
        "corrupcao policial": 9,
    },

    # --------------------------------------
    # POLÍTICA E GOVERNO
    # --------------------------------------

    "politica": {
        "stf": 12,
        "supremo": 12,
        "impeachment": 12,
        "planalto": 10,
        "congresso": 10,
        "senado": 9,
        "camara": 9,
        "ministro": 10,
        "ministra": 10,
        "votacao": 8,
        "reforma": 5,
        "partido": 5,
        "eleicao": 10,
        "eleicoes": 10,
        "governo": 6,
        "oposicao": 6,
        "politica": 5,
        "base governista": 7,
        "cpi": 11,
        "comissao parlamentar": 9,
        "deputado": 8,
        "deputada": 8,
        "presidente": 7,
        "presidencia": 8,
        "governador": 8,
        "governadora": 8,
        "prefeito": 7,
        "prefeita": 7,
        "vereador": 7,
        "vereadores": 7,
        "senador": 8,
        "senadora": 8,
        "projeto de lei": 9,
        "medida provisoria": 9,
        "veto": 8,
        "sancao presidencial": 9,
        "justica eleitoral": 8,
        "tse": 10,
    },

    # --------------------------------------
    # ECONOMIA E FINANÇAS
    # --------------------------------------

    "economia": {
        "inflacao": 12,
        "selic": 12,
        "juros": 10,
        "dolar": 11,
        "pib": 10,
        "recessao": 12,
        "bolsa": 9,
        "ibovespa": 9,
        "ipca": 11,
        "deficit": 10,
        "mercado": 7,
        "investimento": 7,
        "investimentos": 7,
        "economia": 5,
        "banco": 6,
        "consumo": 4,
        "varejo": 4,
        "empresas": 5,
        "empresarial": 5,
        "industria": 6,
        "comercio": 5,
        "exportacao": 7,
        "importacao": 7,
        "desemprego": 8,
        "salario minimo": 8,
        "renda": 6,
        "poupanca": 7,
        "credito": 7,
        "endividamento": 8,
        "divida publica": 9,
        "imposto": 7,
        "tributacao": 8,
        "receita federal": 8,
        "mercado financeiro": 9,
        "financas": 7,
        "orcamento": 8,
        "precos": 8,
    },

    # --------------------------------------
    # SAÚDE E SOCIEDADE
    # --------------------------------------

    "saude": {
        "saude": 12,
        "sus": 11,
        "ministerio da saude": 12,
        "hospital": 9,
        "hospitais": 9,
        "medico": 8,
        "medica": 8,
        "medicina": 8,
        "vacina": 10,
        "vacinacao": 11,
        "epidemia": 10,
        "pandemia": 10,
        "surto": 9,
        "dengue": 11,
        "zika": 9,
        "chikungunya": 9,
        "covid": 10,
        "gripe": 8,
        "virus": 8,
        "doenca": 8,
        "doencas": 9,
        "tratamento": 7,
        "diagnostico": 8,
        "pesquisa medica": 9,
        "saude publica": 11,
        "saude mental": 11,
        "depressao": 9,
        "ansiedade": 8,
        "alimentacao": 7,
        "nutricao": 8,
        "obesidade": 8,
        "diabetes": 9,
        "hipertensao": 9,
        "cancer": 10,
        "oncologia": 9,
        "mortalidade": 8,
        "nascimento": 7,
        "maternidade": 7,
        "envelhecimento": 7,
        "idosos": 7,
        "criancas": 7,
        "educacao": 6,
        "escolas": 6,
        "professores": 6,
        "direitos humanos": 8,
        "assistencia social": 9,
        "desigualdade social": 8,
        "violencia domestica": 9,
        "moradia": 6,
        "saneamento": 7,
        "meio ambiente": 6,
    },

    # --------------------------------------
    # TECNOLOGIA E CIÊNCIA
    # --------------------------------------

    "tecnologia": {
        "tecnologia": 10,
        "inteligencia artificial": 12,
        "ia": 9,
        "robotica": 10,
        "inovacao": 9,
        "inovacao tecnologica": 12,
        "ciencia": 10,
        "cientista": 8,
        "pesquisa cientifica": 11,
        "descoberta cientifica": 10,
        "estudo cientifico": 9,
        "universidade": 7,
        "laboratorio": 8,
        "experimento": 8,
        "espaco": 7,
        "astronomia": 9,
        "satelite": 8,
        "nasa": 8,
        "computador": 7,
        "computadores": 7,
        "smartphone": 7,
        "celular": 6,
        "aplicativo": 6,
        "aplicativos": 6,
        "software": 8,
        "hardware": 8,
        "internet": 6,
        "ciberseguranca": 10,
        "seguranca digital": 9,
        "ataque hacker": 10,
        "vazamento de dados": 10,
        "privacidade digital": 8,
        "redes sociais": 6,
        "big techs": 8,
        "google": 5,
        "apple": 5,
        "microsoft": 5,
        "nvidia": 7,
        "semicondutores": 8,
        "chip": 7,
        "chips": 7,
        "5g": 8,
        "6g": 8,
        "energia renovavel": 8,
        "biotecnologia": 9,
        "genetica": 8,
        "clima": 6,
        "mudancas climaticas": 8,
    },

    # --------------------------------------
    # OPORTUNIDADES E SERVIÇOS
    # --------------------------------------

    "oportunidades": {
        "vagas de emprego": 13,
        "vaga de emprego": 12,
        "emprego": 10,
        "empregos": 10,
        "processo seletivo": 11,
        "concurso publico": 13,
        "concursos publicos": 13,
        "concurso": 11,
        "concursos": 11,
        "edital": 9,
        "inscricoes abertas": 12,
        "inscricao": 8,
        "inscricoes": 8,
        "selecao": 8,
        "bolsa de estudos": 11,
        "bolsa de pesquisa": 10,
        "estagio": 10,
        "jovem aprendiz": 12,
        "aprendiz": 8,
        "cursos gratuitos": 13,
        "curso gratuito": 12,
        "curso online": 9,
        "cursos online": 9,
        "capacitacao": 9,
        "qualificacao profissional": 10,
        "oportunidade": 8,
        "oportunidades": 8,
        "programa social": 9,
        "programas sociais": 9,
        "beneficio": 9,
        "beneficios": 9,
        "auxilio": 9,
        "bolsa familia": 10,
        "abono salarial": 11,
        "pis pasep": 11,
        "seguro desemprego": 10,
        "cadastro unico": 10,
        "inscricao gratuita": 10,
        "servico publico": 9,
        "servicos publicos": 9,
        "atendimento ao cidadao": 8,
        "documentacao": 7,
        "carteira de trabalho": 9,
        "carteira de identidade": 8,
        "isencao": 8,
        "gratuito": 6,
        "gratuita": 6,
        "calendario de pagamentos": 10,
        "pagamento": 6,
        "pagamentos": 6,
        "prazo de inscricao": 9,
        "matricula": 8,
        "matriculas": 8,
    },

}

# ==========================================
# BLOCO FIXO FINAL - ASSINATURA
# PRESERVADO DA VERSÃO ORIGINAL
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
