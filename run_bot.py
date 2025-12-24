import requests
import openai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# =========================
# CONFIGURAÇÕES
# =========================

BLOG_ID = 7605688984374445860

NEWS_API_KEY = "d5a632c8259648eaab341a5e26fa9568"
OPENAI_API_KEY = "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"

SCOPES = ["https://www.googleapis.com/auth/blogger"]

openai.api_key = OPENAI_API_KEY


# =========================
# AUTENTICAÇÃO BLOGGER
# =========================

def autenticar_blogger():
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    return build("blogger", "v3", credentials=creds)


# =========================
# BUSCAR NOTÍCIAS
# =========================

def buscar_noticias(qtd=3):
    """
    Busca notícias em português com fallback automático.
    Prioriza estabilidade no plano FREE da NewsAPI.
    """

    urls = [
        # FONTE 1 – MAIS ESTÁVEL (everything)
        (
            "https://newsapi.org/v2/everything?"
            f"q=Brasil OR política OR economia OR sociedade&"
            f"language=pt&sortBy=publishedAt&pageSize={qtd}&"
            f"apiKey={NEWS_API_KEY}"
        ),

        # FONTE 2 – fallback (top-headlines)
        (
            "https://newsapi.org/v2/top-headlines?"
            f"country=br&language=pt&pageSize={qtd}&"
            f"apiKey={NEWS_API_KEY}"
        )
    ]

    for i, url in enumerate(urls, start=1):
        try:
            print(f"Tentativa {i}: buscando notícias...")
            resposta = requests.get(url, timeout=15).json()

            if resposta.get("status") == "ok":
                artigos = resposta.get("articles", [])
                if artigos:
                    print(f"{len(artigos)} notícias encontradas.")
                    return artigos

            print("Nenhuma notícia retornada nesta tentativa.")

        except Exception as e:
            print(f"Erro ao buscar notícias (tentativa {i}): {e}")

    print("Todas as fontes falharam. Nenhuma notícia disponível.")
    return []

# =========================
# GERAR CONTEÚDO
# =========================

from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

def gerar_conteudo(titulo, descricao):
    try:
        prompt = f"""
        Escreva uma notícia jornalística em português, clara, objetiva e bem estruturada,
        com título, introdução e desenvolvimento, baseada no tema abaixo.

        TEMA: {titulo}

        CONTEXTO:
        {descricao}
        """

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

        texto = response.output_text.strip()
        return texto

    except Exception as e:
        print(f"Erro ao gerar conteúdo: {e}")
        return None

# =========================
# PUBLICAR POST
# =========================

def publicar_post(service, titulo, conteudo):
    post = {
        "title": titulo,
        "content": conteudo,
        "status": "LIVE"
    }

    service.posts().insert(
        blogId=BLOG_ID,
        body=post
    ).execute()

def executar_fluxo():
    print("Fluxo iniciado")

    # 1️⃣ Autenticar no Blogger
    print("Autenticando no Blogger...")
    service = autenticar_blogger()

    # 2️⃣ Buscar notícias
    print("Buscando notícias...")
    noticias = buscar_noticias(qtd=3)

    if not noticias:
        print("Nenhuma notícia encontrada. Encerrando fluxo.")
        return

    # 3️⃣ Processar e publicar cada notícia
    for idx, noticia in enumerate(noticias, start=1):
        titulo = noticia.get("title", "").strip()

        if not titulo:
            print(f"Notícia {idx} sem título. Pulando.")
            continue

        print(f"[{idx}] Gerando conteúdo para: {titulo}")

        try:
            conteudo = gerar_conteudo(noticia)
        except Exception as e:
            print(f"Erro ao gerar conteúdo: {e}")
            continue

        try:
            print(f"[{idx}] Publicando no Blogger...")
            publicar_post(service, titulo, conteudo)
            print(f"[{idx}] Post publicado com sucesso!")
        except Exception as e:
            print(f"Erro ao publicar no Blogger: {e}")

    print("Fluxo finalizado com sucesso.")

if __name__ == "__main__":
    executar_fluxo()
