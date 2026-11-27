
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
    # Chave original preservada: policial
    # --------------------------------------

    "policial": {
        "chacina": 12,
        "homicídio": 12,
        "homicidio": 12,
        "assassinato": 11,
        "latrocínio": 11,
        "latrocinio": 11,
        "operação policial": 12,
        "operação": 10,
        "prisão": 10,
        "prisões": 10,
        "preso": 9,
        "fuzil": 10,
        "tráfico": 9,
        "trafico": 9,
        "investigação": 8,
        "investigacao": 8,
        "mandado": 8,
        "flagrante": 9,
        "confronto": 8,
        "crime": 5,
        "criminoso": 6,
        "suspeito": 5,
        "delegacia": 4,
        "ocorrência": 4,
        "ocorrencia": 4,
        "polícia": 5,
        "policia": 5,
        "policial": 6,
        "assalto": 8,
        "roubo": 8,
        "furto": 7,
        "sequestro": 10,
        "estupro": 10,
        "violência": 6,
        "violencia": 6,
        "milícia": 9,
        "milicia": 9,
        "facção criminosa": 10,
        "faccao criminosa": 10,
        "facção": 9,
        "faccao": 9,
        "batalhão": 5,
        "batalhao": 5,
        "polícia federal": 8,
        "polícia civil": 8,
        "polícia militar": 8,
        "polícia rodoviária": 8,
        "polícia penal": 8,
        "foragido": 8,
        "receptação": 7,
        "receptacao": 7,
        "corrupção policial": 9,
    },


    # --------------------------------------
    # POLÍTICA E GOVERNO
    # Chave original preservada: politica
    # --------------------------------------

    "politica": {
        "stf": 12,
        "supremo": 12,
        "impeachment": 12,
        "planalto": 10,
        "congresso": 10,
        "senado": 9,
        "câmara": 9,
        "camara": 9,
        "ministro": 10,
        "ministra": 10,
        "votação": 8,
        "votacao": 8,
        "reforma": 5,
        "partido": 5,
        "eleição": 10,
        "eleicao": 10,
        "eleições": 10,
        "eleicoes": 10,
        "governo": 6,
        "oposição": 6,
        "oposicao": 6,
        "política": 5,
        "politica": 5,
        "base governista": 7,
        "cpi": 11,
        "comissão parlamentar": 9,
        "comissao parlamentar": 9,
        "deputado": 8,
        "deputada": 8,
        "presidente": 7,
        "presidência": 8,
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
        "medida provisória": 9,
        "medida provisoria": 9,
        "veto": 8,
        "sanção presidencial": 9,
        "sancao presidencial": 9,
        "justiça eleitoral": 8,
        "justica eleitoral": 8,
        "TSE": 10,
    },


    # --------------------------------------
    # ECONOMIA E FINANÇAS
    # Chave original preservada: economia
    # --------------------------------------

    "economia": {
        "inflação": 12,
        "inflacao": 12,
        "selic": 12,
        "juros": 10,
        "dólar": 11,
        "dolar": 11,
        "pib": 10,
        "recessão": 12,
        "recessao": 12,
        "bolsa": 9,
        "ibovespa": 9,
        "ipca": 11,
        "déficit": 10,
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
        "indústria": 6,
        "industria": 6,
        "comércio": 5,
        "comercio": 5,
        "exportação": 7,
        "exportacao": 7,
        "importação": 7,
        "importacao": 7,
        "desemprego": 8,
        "salário mínimo": 8,
        "salario minimo": 8,
        "renda": 6,
        "poupança": 7,
        "poupanca": 7,
        "crédito": 7,
        "credito": 7,
        "endividamento": 8,
        "dívida pública": 9,
        "divida publica": 9,
        "imposto": 7,
        "tributação": 8,
        "tributacao": 8,
        "receita federal": 8,
        "mercado financeiro": 9,
        "finanças": 7,
        "financas": 7,
        "orçamento": 8,
        "orcamento": 8,
        "preços": 8,
        "precos": 8
    },


    # --------------------------------------
    # SAÚDE E SOCIEDADE
    # Nova editoria
    # --------------------------------------

    "saude": {
        "saúde": 12,
        "saude": 12,
        "sus": 11,
        "ministério da saúde": 12,
        "ministerio da saude": 12,
        "hospital": 9,
        "hospitais": 9,
        "médico": 8,
        "medico": 8,
        "médica": 8,
        "medica": 8,
        "medicina": 8,
        "vacina": 10,
        "vacinação": 11,
        "vacinacao": 11,
        "epidemia": 10,
        "pandemia": 10,
        "surto": 9,
        "dengue": 11,
        "zika": 9,
        "chikungunya": 9,
        "covid": 10,
        "gripe": 8,
        "vírus": 8,
        "virus": 8,
        "doença": 8,
        "doenca": 8,
        "doenças": 9,
        "doencas": 9,
        "tratamento": 7,
        "diagnóstico": 8,
        "diagnostico": 8,
        "pesquisa médica": 9,
        "pesquisa medica": 9,
        "saúde pública": 11,
        "saude publica": 11,
        "saúde mental": 11,
        "saude mental": 11,
        "depressão": 9,
        "depressao": 9,
        "ansiedade": 8,
        "alimentação": 7,
        "alimentacao": 7,
        "nutrição": 8,
        "nutricao": 8,
        "obesidade": 8,
        "diabetes": 9,
        "hipertensão": 9,
        "hipertensao": 9,
        "câncer": 10,
        "cancer": 10,
        "oncologia": 9,
        "mortalidade": 8,
        "nascimento": 7,
        "maternidade": 7,
        "envelhecimento": 7,
        "idosos": 7,
        "crianças": 7,
        "criancas": 7,
        "educação": 6,
        "educacao": 6,
        "escolas": 6,
        "professores": 6,
        "direitos humanos": 8,
        "assistência social": 9,
        "assistencia social": 9,
        "desigualdade social": 8,
        "violência doméstica": 9,
        "violencia domestica": 9,
        "moradia": 6,
        "saneamento": 7,
        "meio ambiente": 6
    },


    # --------------------------------------
    # TECNOLOGIA E CIÊNCIA
    # Nova editoria
    # --------------------------------------

    "tecnologia": {
        "tecnologia": 10,
        "inteligência artificial": 12,
        "inteligencia artificial": 12,
        "IA": 9,
        "robótica": 10,
        "robotica": 10,
        "inovação": 9,
        "inovacao": 9,
        "inovação tecnológica": 12,
        "inovacao tecnologica": 12,
        "ciência": 10,
        "ciencia": 10,
        "cientista": 8,
        "pesquisa científica": 11,
        "pesquisa cientifica": 11,
        "descoberta científica": 10,
        "descoberta cientifica": 10,
        "estudo científico": 9,
        "estudo cientifico": 9,
        "universidade": 7,
        "laboratório": 8,
        "laboratorio": 8,
        "experimento": 8,
        "espaço": 7,
        "espaco": 7,
        "astronomia": 9,
        "satélite": 8,
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
        "cibersegurança": 10,
        "ciberseguranca": 10,
        "segurança digital": 9,
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
        "energia renovável": 8,
        "energia renovavel": 8,
        "biotecnologia": 9,
        "genética": 8,
        "genetica": 8,
        "clima": 6,
        "mudanças climáticas": 8,
        "mudancas climaticas": 8
    },


    # --------------------------------------
    # OPORTUNIDADES E SERVIÇOS
    # Nova editoria
    # --------------------------------------

    "oportunidades": {
        "vagas de emprego": 13,
        "vaga de emprego": 12,
        "emprego": 10,
        "empregos": 10,
        "processo seletivo": 11,
        "concurso público": 13,
        "concurso publico": 13,
        "concursos públicos": 13,
        "concursos publicos": 13,
        "concurso": 11,
        "concursos": 11,
        "edital": 9,
        "inscrições abertas": 12,
        "inscricoes abertas": 12,
        "inscrição": 8,
        "inscricao": 8,
        "inscrições": 8,
        "inscricoes": 8,
        "seleção": 8,
        "selecao": 8,
        "bolsa de estudos": 11,
        "bolsa de pesquisa": 10,
        "estágio": 10,
        "estagio": 10,
        "jovem aprendiz": 12,
        "aprendiz": 8,
        "cursos gratuitos": 13,
        "curso gratuito": 12,
        "curso online": 9,
        "cursos online": 9,
        "capacitação": 9,
        "capacitacao": 9,
        "qualificação profissional": 10,
        "qualificacao profissional": 10,
        "oportunidade": 8,
        "oportunidades": 8,
        "programa social": 9,
        "programas sociais": 9,
        "benefício": 9,
        "beneficio": 9,
        "benefícios": 9,
        "beneficios": 9,
        "auxílio": 9,
        "auxilio": 9,
        "bolsa família": 10,
        "bolsa familia": 10,
        "abono salarial": 11,
        "pis pasep": 11,
        "seguro-desemprego": 10,
        "seguro desemprego": 10,
        "cadastro único": 10,
        "cadastro unico": 10,
        "inscrição gratuita": 10,
        "inscricao gratuita": 10,
        "serviço público": 9,
        "servico publico": 9,
        "serviços públicos": 9,
        "servicos publicos": 9,
        "atendimento ao cidadão": 8,
        "atendimento ao cidadao": 8,
        "documentação": 7,
        "documentacao": 7,
        "carteira de trabalho": 9,
        "carteira de identidade": 8,
        "isenção": 8,
        "isencao": 8,
        "gratuito": 6,
        "gratuita": 6,
        "calendário de pagamentos": 10,
        "calendario de pagamentos": 10,
        "pagamento": 6,
        "pagamentos": 6,
        "prazo de inscrição": 9,
        "prazo de inscricao": 9,
        "matrícula": 8,
        "matricula": 8,
        "matrículas": 8,
        "matriculas": 8
    }
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
