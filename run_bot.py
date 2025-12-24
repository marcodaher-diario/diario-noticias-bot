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

def buscar_noticias(qtd=1):
    url = (
        "https://newsapi.org/v2/top-headlines?"
        f"country=br&language=pt&pageSize={qtd}&apiKey={NEWS_API_KEY}"
    )
    response = requests.get(url, timeout=30)
    data = response.json()
    return data.get("articles", [])


# =========================
# GERAR CONTEÚDO
# =========================

def gerar_conteudo(noticia):
    prompt = (
        "Reescreva a notícia abaixo com linguagem jornalística original, "
        "sem copiar o texto, e faça uma breve análise.\n\n"
        f"Título: {noticia.get('title', '')}\n"
        f"Descrição: {noticia.get('description', '')}"
    )

    resposta = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é um jornalista profissional."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6
    )

    texto = resposta["choices"][0]["message"]["content"]
    return f"<p>{texto.replace(chr(10), '</p><p>')}</p>"


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
