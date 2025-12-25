import feedparser
import os
from google.genai import Client
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from configuracoes import BLOCO_FIXO_FINAL

# --- CONFIGURAÇÕES ---
BLOG_ID = "5852420775961497718"
# Certifique-se de colocar sua chave entre as aspas abaixo
MINHA_CHAVE = "AIzaSyA3tfsYn-cxO5DQ013b2YUy837LuNWHpUI" 
client = Client(api_key=MINHA_CHAVE)

RSS_FONTES = ["https://petapixel.com/feed/", "https://digital-photography-school.com/feed/"]
ARQUIVO_LOG = "posts_foto_publicados.txt"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def criar_resenha_ia(titulo, resumo_original):
    prompt = f"Aja como um crítico de fotografia. Escreva uma resenha curta (2 parágrafos) em português sobre: {titulo}. Baseie-se nisto: {resumo_original}. Não copie, seja original."
    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        return response.text
    except Exception as e:
        print(f"Erro na IA: {e}")
        return "Confira os detalhes no site original."

def publicar_foto():
    if not os.path.exists("token.json"): return
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("blogger", "v3", credentials=creds)

    for url in RSS_FONTES:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            link = entry.link
            if os.path.exists(ARQUIVO_LOG):
                with open(ARQUIVO_LOG, "r") as f:
                    if link in f.read(): continue

            print(f"🤖 Criando conteúdo para: {entry.title}")
            
            # Criando a resenha e o título em português
            resenha_pt = criar_resenha_ia(entry.title, entry.get("summary", ""))
            resenha_html = resenha_pt.replace('\n', '<br>')
            
            # Imagem 16:9
            imagem = "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"
            if "media_content" in entry: imagem = entry.media_content[0]['url']
            
            conteudo = f"""
            <div style="font-family: Verdana, sans-serif; color: #002b36; background: transparent;">
                <h1 style="color: #004d40; text-align: center;">{entry.title}</h1>
                <div style="text-align: center; margin: 20px 0;">
                    <img src="{imagem}" style="width: 100%; max-width: 680px; border-radius: 15px; border: 3px solid #004d40;">
                </div>
                <div style="font-size: 16px; text-align: justify;">
                    {resenha_html}
                </div>
                <hr style="border: 0; border-top: 1px solid #004d40; margin: 30px 0;">
                {BLOCO_FIXO_FINAL}
            </div>"""

            service.posts().insert(blogId=BLOG_ID, body={
                "title": entry.title,
                "content": conteudo,
                "status": "LIVE"
            }).execute()

            with open(ARQUIVO_LOG, "a") as f: f.write(link + "\n")
            print("✅ Postado com sucesso!")
            return

if __name__ == "__main__":
    publicar_foto()
