import os
import requests
import datetime
import openai
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# --- CONFIGURAÇÕES ---
NEWS_API_KEY = "COLE_AQUI_SUA_CHAVE_NEWSAPI"
OPENAI_API_KEY = "COLE_AQUI_SUA_CHAVE_OPENAI"
BLOG_ID = "7605688984374445860"

openai.api_key = OPENAI_API_KEY
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def autenticar_blogger():
    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    return build("blogger", "v3", credentials=creds)

def buscar_noticias(qtd=3):
    url = (f"https://newsapi.org/v2/top-headlines?country=br&language=pt&pageSize={qtd}&apiKey={NEWS_API_KEY}")
    resp = requests.get(url)
    data = resp.json()
    return data.get("articles", [])

def gerar_texto_openai(titulo, conteudo):
    prompt = (f"Reescreva a notícia abaixo com clareza e originalidade, mantendo os fatos e criando um parágrafo de análise.\n\nTÍTULO: {titulo}\n\nTEXTO: {conteudo}\n\nRESPOSTA:")
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return resp.choices[0].message["content"]

def gerar_imagem_openai(prompt):
    resp = openai.images.generate(model="gpt-image-1", prompt=prompt, size="1024x1024", n=1)
    return resp.data[0].url

def publicar_no_blogger(service, blog_id, titulo, conteudo_html):
    post_body = {"kind": "blogger#post", "blog": {"id": blog_id}, "title": titulo, "content": conteudo_html}
    post = service.posts().insert(blogId=blog_id, body=post_body, isDraft=False).execute()
    return post

def executar_fluxo(blog_id):
    noticias = buscar_noticias()
    service = autenticar_blogger()
    for n in noticias:
        titulo = n.get("title", "Sem título")
        descricao = n.get("description", "")
        fonte = n.get("source", {}).get("name", "Desconhecida")
        texto = gerar_texto_openai(titulo, descricao)
        img_url = gerar_imagem_openai(f"Imagem jornalística de: {titulo}")
        conteudo_html = f"<h2>{titulo}</h2><img src='{img_url}'><p>{texto}</p><p><em>Fonte: {fonte}</em></p>"
        post = publicar_no_blogger(service, blog_id, titulo, conteudo_html)
        print("Publicado:", post.get("url"))

if __name__ == "__main__":
    executar_fluxo(BLOG_ID)
