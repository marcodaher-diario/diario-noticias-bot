# -*- coding: utf-8 -*-

import os
import re
import feedparser
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
import unicodedata

def remover_acentos(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

from configuracoes import (
    BLOG_ID,
    RSS_FEEDS,
    PESOS_POR_TEMA,
    BLOCO_FIXO_FINAL
)

from template_blog import obter_esqueleto_html
from gemini_engine import GeminiEngine
from imagem_engine import ImageEngine

import requests
from bs4 import BeautifulSoup


def extrair_imagem_noticia(entry):

    # ======================================================
    # 1️⃣ CAMPOS RSS MAIS COMUNS
    # ======================================================

    try:

        if hasattr(entry, "media_content"):
            for media in entry.media_content:
                url = media.get("url", "")
                if url:
                    return url

        if hasattr(entry, "media_thumbnail"):
            for media in entry.media_thumbnail:
                url = media.get("url", "")
                if url:
                    return url

        if hasattr(entry, "links"):
            for link in entry.links:
                if link.get("type", "").startswith("image"):
                    return link.get("href")

        if hasattr(entry, "enclosures"):
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image"):
                    return enc.get("href")

    except:
        pass


    # ======================================================
    # 2️⃣ IMAGEM DENTRO DO SUMMARY
    # ======================================================

    try:

        if hasattr(entry, "summary"):
            soup = BeautifulSoup(entry.summary, "html.parser")

            img = soup.find("img")

            if img and img.get("src"):
                return img.get("src")

    except:
        pass


    # ======================================================
    # 3️⃣ OG:IMAGE DA PÁGINA DA NOTÍCIA
    # ======================================================

    try:

        url = entry.link

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(url, headers=headers, timeout=8)

        soup = BeautifulSoup(r.text, "html.parser")

        og = soup.find("meta", property="og:image")

        if og and og.get("content"):
            return og.get("content")

        tw = soup.find("meta", attrs={"name": "twitter:image"})

        if tw and tw.get("content"):
            return tw.get("content")

    except:
        pass


    return ""

# ==========================================================
# CONFIGURAÇÃO
# ==========================================================

AGENDA_POSTAGENS = {
    "09:00": "policial",
    "13:00": "economia",
    "19:00": "politica"
}

JANELA_MINUTOS = 90
ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"
ARQUIVO_POSTS_PUBLICADOS = "posts_publicados.txt"


# ==========================================================
# UTILIDADES DE TEMPO
# ==========================================================

def obter_horario_brasilia():
    return datetime.utcnow() - timedelta(hours=3)


def horario_para_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def dentro_da_janela(min_atual, min_agenda):
    return abs(min_atual - min_agenda) <= JANELA_MINUTOS


# ==========================================================
# CONTROLE DE PUBLICAÇÃO (COM RODÍZIO DE 15 LINHAS)
# ==========================================================

def ja_postou(data_str, horario_agenda):
    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False
    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or "|" not in linha:
                continue
            partes = linha.split("|")
            if len(partes) == 2:
                data, hora = partes
                if data == data_str and hora == horario_agenda:
                    return True
    return False


def registrar_postagem(data_str, horario_agenda):
    linhas = []
    if os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
            linhas = f.readlines()

    nova_linha = f"{data_str}|{horario_agenda}\n"

    if nova_linha not in linhas:
        linhas.append(nova_linha)

    linhas = linhas[-15:]

    with open(ARQUIVO_CONTROLE_DIARIO, "w", encoding="utf-8") as f:
        f.writelines(linhas)


# ==========================================================
# CONTROLE DE LINKS
# ==========================================================

def registrar_link_publicado(link):
    linhas = []
    if os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        with open(ARQUIVO_POSTS_PUBLICADOS, "r", encoding="utf-8") as f:
            linhas = f.readlines()

    nova_linha = f"{link}\n"

    if nova_linha not in linhas:
        linhas.append(nova_linha)

    linhas = linhas[-100:]

    with open(ARQUIVO_POSTS_PUBLICADOS, "w", encoding="utf-8") as f:
        f.writelines(linhas)


def link_ja_publicado(link):
    if not os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        return False
    with open(ARQUIVO_POSTS_PUBLICADOS, "r", encoding="utf-8") as f:
        return any(link.strip() == l.strip() for l in f)


# ==========================================================
# PROTEÇÃO EXTRA CONTRA REPETIÇÃO
# ==========================================================

def gerar_id_noticia(titulo):
    texto = titulo.lower()
    texto = re.sub(r'[^a-z0-9\s]', '', texto)
    palavras = texto.split()
    return "-".join(palavras[:8])


# ==========================================================
# VERIFICAR TEMA
# ==========================================================

def verificar_assunto(titulo, texto):

    conteudo = remover_acentos(f"{titulo} {texto}".lower())

    melhor_tema = "geral"
    maior_score = 0

    for tema, palavras_chave in PESOS_POR_TEMA.items():

        score_atual = 0

        for palavra, peso in palavras_chave.items():

            palavra_norm = remover_acentos(palavra.lower())

            ocorrencias = conteudo.count(palavra_norm)

            if ocorrencias > 0:
                score_atual += peso * ocorrencias

        if score_atual > maior_score:
            maior_score = score_atual
            melhor_tema = tema

    if maior_score >= 8:
        return melhor_tema

    return "geral"


# ==========================================================
# BUSCAR NOTÍCIA (BUSCA PROGRESSIVA)
# ==========================================================

def buscar_noticia(tipo):

    tipo = remover_acentos(tipo.lower())

    palavras_peso = PESOS_POR_TEMA.get(tipo, {})

    agora = datetime.utcnow()

    janelas_busca = [6,12,24,36,48]

    for limite_horas in janelas_busca:

        noticias_validas = []

        for feed_url in RSS_FEEDS:

            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:20]:

                titulo = entry.get("title","")
                resumo = entry.get("summary","")
                link = entry.get("link","")
                imagem = extrair_imagem_noticia(entry)

                if not titulo or not link:
                    continue

                tema_detectado = verificar_assunto(titulo,resumo)

                if tema_detectado != tipo and tema_detectado != "geral":
                    continue

                if link_ja_publicado(link):
                    continue
                    
                data_publicacao = None
                
                if hasattr(entry,"published"):
                    try:
                        data_publicacao = parsedate_to_datetime(entry.published)
                
                        # normaliza timezone para evitar erro datetime
                        if data_publicacao.tzinfo is not None:
                            data_publicacao = data_publicacao.astimezone(tz=None).replace(tzinfo=None)
                
                    except:
                        pass
                

                if data_publicacao:

                    horas_passadas = (agora - data_publicacao).total_seconds() / 3600

                    if horas_passadas > limite_horas:
                        continue

                conteudo = remover_acentos(f"{titulo} {resumo}".lower())

                score = 0

                for palavra,peso in palavras_peso.items():

                    palavra_norm = remover_acentos(palavra.lower())

                    ocorrencias = conteudo.count(palavra_norm)

                    if ocorrencias > 0:
                        score += peso * ocorrencias

                noticias_validas.append({
                    "titulo":titulo,
                    "texto":resumo,
                    "link":link,
                    "imagem":imagem,
                    "score":score
                })

        if noticias_validas:

            noticia_escolhida = max(noticias_validas,key=lambda x:x["score"])

            return noticia_escolhida

    return None

# ==========================================================
# GERAR TAGS SEO - SISTEMA DE CLUSTERS (DIÁRIO DE NOTÍCIAS)
# ==========================================================

def gerar_tags_seo(titulo, texto):

    stopwords = [
        "com","como","para","porque","sobre","entre","de","do","da",
        "dos","das","em","um","uma","os","as","que","no","na","ao",
        "aos","por","mais","menos","ser","estar","ter","se","sua",
        "seu","suas","seus","também","muito","muitos","muitas"]

# ======================================================
# CLUSTERS PRINCIPAIS DE NOTÍCIAS
# Atualizado para o cenário de notícias de 2026
# ======================================================

clusters = {

    "política": [
        "governo", "governo federal", "planalto", "presidente",
        "presidência", "ministro", "ministério", "congresso",
        "congresso nacional", "senado", "senador", "câmara",
        "camara", "deputado", "deputada", "stf", "supremo",
        "supremo tribunal federal", "tse", "tribunal superior eleitoral",
        "eleição", "eleições", "eleitoral", "candidatura",
        "candidato", "candidata", "campanha", "voto", "votação",
        "pesquisa eleitoral", "intenção de voto", "primeiro turno",
        "segundo turno", "presidencial", "governador",
        "governador interino", "prefeito", "prefeita",
        "vice-presidente", "oposição", "base governista",
        "aliado", "aliados", "bolsonarismo", "petismo",
        "direita", "esquerda", "partido", "pl", "pt",
        "psd", "mdb", "união brasil", "reforma política",
        "impeachment", "emenda constitucional", "pec",
        "projeto de lei", "pl", "medida provisória", "mp"
    ],

    "eleições_2026": [
        "eleição 2026", "eleições 2026", "eleições presidenciais",
        "eleição presidencial", "corrida presidencial",
        "disputa presidencial", "candidatura presidencial",
        "candidato à presidência", "candidata à presidência",
        "primeiro turno", "segundo turno", "pesquisa eleitoral",
        "pesquisa presidencial", "intenção de voto",
        "datafolha", "quaest", "paraná pesquisas",
        "ibope", "instituto de pesquisa", "debate eleitoral",
        "campanha eleitoral", "horário eleitoral",
        "tse", "justiça eleitoral", "ficha limpa",
        "registro de candidatura", "registro de candidatura presidencial",
        "lula", "flávio bolsonaro", "jair bolsonaro",
        "tarcísio", "caiado", "ratinho jr",
        "simone tebet", "romeu zema"
    ],

    "economia": [
        "economia", "econômico", "econômica", "inflação",
        "inflacao", "ipca", "igp-m", "inpc", "selic",
        "taxa selic", "juros", "juros básicos", "copom",
        "banco central", "bacen", "dólar", "dolar",
        "euro", "câmbio", "cambio", "pib", "crescimento",
        "recessão", "recessao", "mercado", "mercado financeiro",
        "ibovespa", "ações", "acoes", "bolsa", "investimento",
        "investimentos", "renda fixa", "poupança", "poupanca",
        "tesouro direto", "crédito", "credito", "financiamento",
        "empréstimo", "emprestimo", "endividamento",
        "inadimplência", "inadimplencia", "dívida pública",
        "divida publica", "resultado fiscal", "déficit",
        "deficit", "superávit", "superavit", "arcabouço fiscal",
        "meta fiscal", "contas públicas", "contas publicas"
    ],

    "impostos_e_tributos": [
        "imposto", "impostos", "tributo", "tributos",
        "tributação", "tributacao", "reforma tributária",
        "reforma tributaria", "taxa", "taxação", "taxacao",
        "isenção", "isencao", "icms", "ipi", "iss",
        "pis", "cofins", "irpf", "imposto de renda",
        "irpj", "simples nacional", "mei", "receita federal",
        "receita", "fisco", "arrecadação", "arrecadacao",
        "taxa das blusinhas", "compras internacionais",
        "importação", "importacao", "exportação", "exportacao"
    ],

    "segurança": [
        "segurança", "seguranca", "segurança pública",
        "seguranca publica", "polícia", "policia", "policial",
        "polícia federal", "pf", "polícia civil", "policia civil",
        "polícia militar", "policia militar", "crime",
        "criminalidade", "assassinato", "homicídio", "homicidio",
        "latrocínio", "latrocinio", "roubo", "furto",
        "sequestro", "estupro", "violência", "violencia",
        "violência contra a mulher", "feminicídio", "feminicidio",
        "tráfico", "trafico", "narcotráfico", "narcotrafico",
        "facção", "facção criminosa", "faccoes",
        "crime organizado", "organização criminosa",
        "milícia", "milicia", "presídio", "presidio",
        "prisão", "prisao", "preso", "suspeito",
        "investigação", "investigacao", "operação policial",
        "operação", "operacao", "mandado", "apreensão",
        "apreensao", "armas", "drogas", "narcotráfico",
        "terrorismo", "terrorista"
    ],

    "justiça": [
        "justiça", "justica", "judiciário", "judiciario",
        "tribunal", "tribunais", "juiz", "juíza", "juiza",
        "ministro do stf", "sentença", "decisão judicial",
        "decisao judicial", "processo", "ação judicial",
        "acao judicial", "acusação", "acusacao", "denúncia",
        "denuncia", "investigação", "investigacao",
        "inquérito", "inquerito", "mandado", "liminar",
        "recurso", "condenação", "condenacao", "absolvição",
        "absolvicao", "réu", "reu", "réus", "reus",
        "julgamento", "julgamento virtual", "habeas corpus",
        "ficha limpa", "stf", "tse", "stj", "tribunal superior",
        "procuradoria", "pgr", "ministério público",
        "ministerio publico", "mpf", "advocacia-geral da união",
        "agu"
    ],

    "stf": [
        "stf", "supremo", "supremo tribunal federal",
        "alexandre de moraes", "moraes", "barroso",
        "luís roberto barroso", "luis roberto barroso",
        "edson fachin", "fachin", "gilmar mendes",
        "cármen lúcia", "carmen lucia", "luiz fux", "fux",
        "flávio dino", "flavio dino", "andre mendonça",
        "andré mendonça", "cristiano z anin", "z anin",
        "julgamento no stf", "decisão do stf", "decisao do stf",
        "ministro do supremo", "ministra do supremo",
        "plenário do stf", "plenario do stf",
        "supremo tribunal"
    ],

    "internacional": [
        "internacional", "exterior", "mundo", "guerra",
        "conflito", "ataque", "ofensiva", "invasão", "invasao",
        "sanções", "sancoes", "otan", "nato", "onu",
        "conselho de segurança", "oriente médio", "oriente medio",
        "ucrânia", "ucrania", "rússia", "russia",
        "israel", "irã", "ira", "palestina", "gaza",
        "hamas", "hezbollah", "síria", "siria",
        "china", "taiwan", "coreia do norte",
        "coreia do sul", "japão", "japao",
        "europa", "união europeia", "uniao europeia",
        "eua", "estados unidos", "américa latina",
        "america latina", "venezuela", "argentina",
        "méxico", "mexico"
    ],

    "brasil_eua": [
        "brasil eua", "brasil estados unidos",
        "brasil-estados unidos", "relações brasil-eua",
        "relacoes brasil-eua", "trump", "donald trump",
        "governo trump", "casa branca", "washington",
        "tarifas americanas", "tarifas dos eua",
        "tarifaço", "tarifaco", "tarifas sobre produtos brasileiros",
        "produtos brasileiros", "comércio exterior",
        "comercio exterior", "sanções americanas",
        "sancoes americanas", "embaixada americana",
        "embaixada dos estados unidos", "marco rubio",
        "secretário de estado", "secretario de estado"
    ],

    "trabalho": [
        "trabalho", "emprego", "empregos", "desemprego",
        "mercado de trabalho", "trabalhador", "trabalhadores",
        "salário", "salario", "salário mínimo", "salario minimo",
        "renda", "carteira assinada", "clt", "fgts",
        "férias", "ferias", "13º salário", "13 salario",
        "jornada de trabalho", "escala 6x1", "fim da escala 6x1",
        "40 horas", "44 horas", "horas trabalhadas",
        "trabalho remoto", "home office", "informalidade",
        "trabalhador informal", "uber", "motorista de aplicativo",
        "aplicativo", "uberização", "uberizacao"
    ],

    "previdência": [
        "previdência", "previdencia", "inss",
        "aposentadoria", "aposentado", "aposentados",
        "pensão", "pensao", "benefício", "beneficio",
        "benefícios", "beneficios", "bpc",
        "auxílio-doença", "auxilio-doenca",
        "auxílio", "auxilio", "segurado", "contribuição",
        "contribuicao", "tempo de contribuição",
        "tempo de contribuicao", "reforma da previdência",
        "reforma da previdencia", "idade mínima",
        "idade minima", "perícia", "pericia",
        "salário de benefício", "salario de beneficio"
    ],

    "saúde": [
        "saúde", "saude", "sus", "ministério da saúde",
        "ministerio da saude", "hospital", "hospitais",
        "médico", "medico", "médicos", "medicos",
        "doença", "doenca", "epidemia", "pandemia",
        "vírus", "virus", "vacina", "vacinação",
        "vacinacao", "dengue", "covid", "influenza",
        "gripe", "câncer", "cancer", "tratamento",
        "medicamento", "remédio", "remedio",
        "anvisa", "oms", "obesidade", "diabetes",
        "hipertensão", "hipertensao"
    ],

    "educação": [
        "educação", "educacao", "ensino", "escola", "escolas",
        "professor", "professores", "aluno", "alunos",
        "universidade", "faculdade", "enem", "sisu",
        "prouni", "fies", "vestibular", "mec",
        "ministério da educação", "ministerio da educacao",
        "ensino superior", "ensino médio", "ensino medio",
        "educação infantil", "educacao infantil",
        "escola integral", "ensino integral"
    ],

    "tecnologia": [
        "tecnologia", "inteligência artificial",
        "inteligencia artificial", "ia", "chatgpt",
        "gemini", "openai", "google", "microsoft",
        "apple", "meta", "amazon", "nvidia",
        "robô", "robo", "robôs", "robos", "software",
        "hardware", "aplicativo", "aplicativos",
        "internet", "redes sociais", "cibersegurança",
        "ciberseguranca", "hacker", "dados", "privacidade",
        "5g", "6g", "semicondutores", "chips"
    ],

    "meio_ambiente": [
        "meio ambiente", "ambiental", "amazônia", "amazonia",
        "desmatamento", "queimada", "queimadas", "incêndio",
        "incendio", "incêndios", "incendios", "clima",
        "mudanças climáticas", "mudancas climaticas",
        "aquecimento global", "chuva", "enchente",
        "enchentes", "alagamento", "seca", "estiagem",
        "rios", "floresta", "ibama", "icmbio",
        "licenciamento ambiental", "emissões", "emissoes",
        "energia renovável", "energia renovavel"
    ],

    "energia": [
        "energia", "energia elétrica", "energia eletrica",
        "eletricidade", "aneel", "usina", "hidrelétrica",
        "hidreletrica", "termelétrica", "termeletrica",
        "energia solar", "energia eólica", "energia eolica",
        "petróleo", "petroleo", "gás natural", "gas natural",
        "combustíveis", "combustiveis", "gasolina", "diesel",
        "etanol", "preço dos combustíveis",
        "preco dos combustiveis", "petrobras"
    ],

    "agropecuária": [
        "agronegócio", "agronegocio", "agro", "agricultura",
        "pecuária", "pecuaria", "produtor rural",
        "produtores rurais", "soja", "milho", "café", "cafe",
        "carne bovina", "carne", "gado", "boi",
        "exportação agrícola", "exportacao agricola",
        "safra", "colheita", "conab", "embrapa",
        "mst", "terra", "reforma agrária", "reforma agraria"
    ],

    "infraestrutura": [
        "infraestrutura", "rodovia", "rodovias", "estrada",
        "estradas", "ferrovia", "ferrovias", "metrô", "metro",
        "aeroporto", "portos", "porto", "saneamento",
        "água", "agua", "esgoto", "habitação", "habitacao",
        "minha casa minha vida", "obras públicas",
        "obras publicas", "concessão", "concessao",
        "privatização", "privatizacao", "pedágio", "pedagio"
    ],

    "empresas_e_mercado": [
        "empresa", "empresas", "companhia", "companhias",
        "mercado", "varejo", "varejista", "banco", "bancos",
        "fintech", "startup", "falência", "falencia",
        "recuperação judicial", "recuperacao judicial",
        "fusão", "fusao", "aquisição", "aquisicao",
        "petrobras", "vale", "embraer", "magalu",
        "americanas", "itau", "itaú", "bradesco",
        "bradesco", "santander", "nubank"
    ],

    "esportes": [
        "futebol", "futebol brasileiro", "brasileirão",
        "brasileirao", "libertadores", "copa do brasil",
        "seleção brasileira", "selecao brasileira",
        "cbf", "flamengo", "corinthians", "palmeiras",
        "são paulo", "sao paulo", "vasco", "botafogo",
        "fluminense", "grêmio", "gremio", "internacional",
        "cruzeiro", "atlético", "atletico", "nba",
        "fórmula 1", "formula 1", "olimpíadas", "olimpiadas"
    ]
}


# ======================================================
# ENTIDADES IMPORTANTES
# ======================================================

entidades = {

    # Governo e instituições
    "stf": "Supremo Tribunal Federal",
    "supremo": "Supremo Tribunal Federal",
    "tse": "Tribunal Superior Eleitoral",
    "stj": "Superior Tribunal de Justiça",
    "senado": "Senado Federal",
    "senado federal": "Senado Federal",
    "câmara": "Câmara dos Deputados",
    "camara": "Câmara dos Deputados",
    "câmara dos deputados": "Câmara dos Deputados",
    "congresso": "Congresso Nacional",
    "congresso nacional": "Congresso Nacional",
    "planalto": "Palácio do Planalto",
    "presidência da república": "Presidência da República",

    # Segurança e Justiça
    "polícia federal": "Polícia Federal",
    "policia federal": "Polícia Federal",
    "pf": "Polícia Federal",
    "ministério público": "Ministério Público",
    "ministerio publico": "Ministério Público",
    "pgr": "Procuradoria-Geral da República",
    "agu": "Advocacia-Geral da União",

    # Economia
    "banco central": "Banco Central do Brasil",
    "bacen": "Banco Central do Brasil",
    "ibovespa": "Ibovespa",
    "petrobras": "Petrobras",
    "vale": "Vale",
    "embraer": "Embraer",
    "receita federal": "Receita Federal",
    "tesouro nacional": "Tesouro Nacional",
    "copom": "Comitê de Política Monetária",

    # Organismos internacionais
    "onu": "Organização das Nações Unidas",
    "otan": "Organização do Tratado do Atlântico Norte",
    "oms": "Organização Mundial da Saúde",
    "união europeia": "União Europeia",
    "uniao europeia": "União Europeia",

    # Tecnologia
    "openai": "OpenAI",
    "google": "Google",
    "microsoft": "Microsoft",
    "meta": "Meta",
    "nvidia": "NVIDIA",
    "apple": "Apple",
    "amazon": "Amazon"
}

# ======================================================
# PESSOAS IMPORTANTES
# ======================================================

pessoas = {

    # Brasil - Governo
    "lula": "Luiz Inácio Lula da Silva",
    "luiz inácio lula da silva": "Luiz Inácio Lula da Silva",
    "jair bolsonaro": "Jair Bolsonaro",
    "bolsonaro": "Jair Bolsonaro",
    "flávio bolsonaro": "Flávio Bolsonaro",
    "flavio bolsonaro": "Flávio Bolsonaro",
    "eduardo bolsonaro": "Eduardo Bolsonaro",
    "carlos bolsonaro": "Carlos Bolsonaro",
    "michelle bolsonaro": "Michelle Bolsonaro",
    "janja": "Janja da Silva",

    # STF / Judiciário
    "moraes": "Alexandre de Moraes",
    "alexandre de moraes": "Alexandre de Moraes",
    "barroso": "Luís Roberto Barroso",
    "luís roberto barroso": "Luís Roberto Barroso",
    "luis roberto barroso": "Luís Roberto Barroso",
    "fachin": "Edson Fachin",
    "edson fachin": "Edson Fachin",
    "gilmar mendes": "Gilmar Mendes",
    "cármen lúcia": "Cármen Lúcia",
    "carmen lucia": "Cármen Lúcia",
    "luiz fux": "Luiz Fux",
    "fux": "Luiz Fux",
    "flávio dino": "Flávio Dino",
    "flavio dino": "Flávio Dino",
    "andre mendonça": "André Mendonça",
    "andré mendonça": "André Mendonça",

    # Política / Eleições
    "tarcísio": "Tarcísio de Freitas",
    "tarcísio de freitas": "Tarcísio de Freitas",
    "caiado": "Ronaldo Caiado",
    "ronaldo caiado": "Ronaldo Caiado",
    "ratinho jr": "Ratinho Júnior",
    "ratinho junior": "Ratinho Júnior",
    "romeu zema": "Romeu Zema",
    "simone tebet": "Simone Tebet",

    # Internacional
    "trump": "Donald Trump",
    "donald trump": "Donald Trump",
    "putin": "Vladimir Putin",
    "vladimir putin": "Vladimir Putin",
    "netanyahu": "Benjamin Netanyahu",
    "benjamin netanyahu": "Benjamin Netanyahu",
    "xi": "Xi Jinping",
    "xi jinping": "Xi Jinping",
    "marco rubio": "Marco Rubio"
}

# ======================================================
# PALAVRAS DO TÍTULO
# ======================================================

palavras_titulo = re.findall(r'\b[a-zà-ÿ]{4,}\b', titulo.lower())

conteudo = f"{titulo} {texto[:200]}"
palavras_texto = re.findall(r'\b[a-zà-ÿ]{4,}\b', conteudo.lower())

texto_total = conteudo.lower()

tags = []

    # ======================================================
    # TAGS DO TÍTULO (PRIORIDADE)
    # ======================================================

    for p in palavras_titulo:
        if p not in stopwords and p.capitalize() not in tags:
            tags.append(p.capitalize())

    # ======================================================
    # TAGS DO TEXTO
    # ======================================================

    for p in palavras_texto:
        if p not in stopwords and p.capitalize() not in tags:
            tags.append(p.capitalize())

    # ======================================================
    # ENTIDADES IMPORTANTES
    # ======================================================

    for chave, entidade in entidades.items():
        if chave in texto_total and entidade not in tags:
            tags.append(entidade)

    # ======================================================
    # PESSOAS IMPORTANTES
    # ======================================================

    for chave, nome in pessoas.items():
        if chave in texto_total and nome not in tags:
            tags.append(nome)

    # ======================================================
    # CLUSTERS
    # ======================================================

    for cluster, palavras in clusters.items():
        for palavra in palavras:
            if palavra in texto_total:
                cluster_formatado = cluster.capitalize()
                if cluster_formatado not in tags:
                    tags.append(cluster_formatado)
                break

    # ======================================================
    # TAGS FIXAS DO BLOG
    # ======================================================

    tags_fixas = [
        "Diário de Notícias",
        "Notícias",
        "Brasil",
        "Atualidades"
    ]

    for tf in tags_fixas:
        if tf not in tags:
            tags.append(tf)

    # ======================================================
    # LIMITADOR DE 200 CARACTERES
    # ======================================================
    
    resultado = []
    tamanho_atual = 0
    
    for tag in tags:
    
        # evita palavras muito curtas ou ruins
        if len(tag) < 4:
            continue
    
        tamanho_tag = len(tag)
    
        if tamanho_atual + tamanho_tag + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += tamanho_tag + 2
        else:
            break
    
    # limite adicional de segurança
    resultado = resultado[:15]
    
    return resultado

# ==========================================================
# MODO TESTE
# ==========================================================

def executar_modo_teste(tema_forcado=None, publicar=False):

    print("=== MODO TESTE ATIVADO ===")

    if not tema_forcado:
        tema_forcado = "policial"

    noticia = buscar_noticia(tema_forcado)

    if not noticia:
        print("Nenhuma notícia encontrada para teste.")
        return

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    texto_ia = gemini.gerar_analise_jornalistica(
        noticia["titulo"],
        noticia["texto"],
        tema_forcado
    )

    query_visual = gemini.gerar_query_visual(
        noticia["titulo"],
        noticia["texto"]
    )

    texto_total = (noticia["titulo"] + " " + noticia["texto"]).lower()

    if "stf" in texto_total or "supremo" in texto_total:
        query_visual = "Supremo Tribunal Federal Brasília Brazil building"
    elif "senado" in texto_total:
        query_visual = "Senado Federal Brasília Brazil congress building"
    elif "câmara" in texto_total or "camara" in texto_total:
        query_visual = "Câmara dos Deputados Brasília Brazil congress building"
    elif "planalto" in texto_total:
        query_visual = "Palácio do Planalto Brasília Brazil government palace"
    elif "khamenei" in texto_total or "irã" in texto_total or "ira" in texto_total:
        query_visual = "Khamenei Iran supreme leader portrait Tehran"

    imagem_final = imagem_engine.obter_imagem(
        noticia,
        tema_forcado,
        query_ia=query_visual
    )

    dados = {
        "titulo": noticia["titulo"],
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    # validação de segurança
    if not html or len(html.strip()) < 50:
        raise Exception("HTML inválido ou vazio.")

    tags = gerar_tags_seo(noticia["titulo"], texto_ia)

    if not tags or not isinstance(tags, list):
        tags = ["Noticias"]

    tags = [str(t).strip() for t in tags if str(t).strip()]

    if not tags:
        tags = ["Noticias"]

    titulo_final = noticia["titulo"]

    if not titulo_final or len(titulo_final.strip()) < 5:
        titulo_final = "Notícia Atual"

    print("Título:", titulo_final)
    print("Tags:", tags)
    print("Tamanho do HTML:", len(html))

    if not publicar:
        print("Modo teste sem publicação.")
        return

    creds = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=creds)

    service.posts().insert(
        blogId=BLOG_ID,
        body={
            "title": titulo_final,
            "content": html,
            "labels": tags
        },
        isDraft=False
    ).execute()

    print("Postagem publicada com sucesso.")

    return noticia


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if __name__ == "__main__":


    if os.getenv("TEST_MODE") == "true":

        tema_teste = os.getenv("TEST_TEMA","policial")

        publicar_teste = os.getenv("TEST_PUBLICAR","false") == "true"

        executar_modo_teste(
            tema_forcado=tema_teste,
            publicar=publicar_teste
        )

        exit()

    agora = obter_horario_brasilia()

    print("Bot iniciado:", agora)

    min_atual = agora.hour * 60 + agora.minute

    data_hoje = agora.strftime("%Y-%m-%d")

    print("Horário atual:", agora)

    print("Minuto atual:", min_atual)

    horario_escolhido = None

    tema_escolhido = None

    for horario_agenda,tema in AGENDA_POSTAGENS.items():

        min_agenda = horario_para_minutos(horario_agenda)

        if dentro_da_janela(min_atual,min_agenda):

            if not ja_postou(data_hoje,horario_agenda):
                horario_escolhido = horario_agenda
                tema_escolhido = tema
                break

    if not horario_escolhido:
        print("Fora da janela de postagem.")
        exit()

    noticia = buscar_noticia(tema_escolhido)

    if not noticia:
        print("Nenhuma notícia encontrada.")
        exit()

    executar_modo_teste(tema_escolhido, True)

    registrar_postagem(data_hoje, horario_escolhido)

    registrar_link_publicado(noticia["link"])

    registrar_link_publicado(gerar_id_noticia(noticia["titulo"]))

    print(f"Post publicado com sucesso: {noticia['titulo']}")
