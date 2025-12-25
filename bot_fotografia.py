import feedparser
import os
import google.generativeai as genai
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from configuracoes import BLOCO_FIXO_FINAL

# --- CONFIGURAÇÕES ---
BLOG_ID = "5852420775961497718"
# Substitua 'SUA_CHAVE_AQUI' pela sua chave do Gemini depois
genai.configure(api_key="AIzaSyA3tfsYn-cxO5DQ013b2YUy837LuNWHpUI")
model = genai.GenerativeModel('gemini-1.5-flash')

RSS_FONTES = ["https://petapixel.com/feed/", "https://digital-photography-school.com/feed/"]
ARQUIVO_LOG = "posts_foto_publicados.txt"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

def criar_resenha_ia(titulo, link, resumo_original):
    prompt = f"""
    Aja como um especialista em fotografia. Leia este título: {titulo} 
    e este resumo: {resumo_original}.
    Escreva uma resenha curta e inédita em português (Brasil) para um blog. 
    Não copie o texto original. Explique por que isso é importante para fotógrafos.
    Use um tom profissional e amigável. Máximo de 3 parágrafos.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Erro ao gerar resenha."

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

            print(f"🤖 IA Criando resenha para: {entry.title}")
            resenha_pt = criar_resenha_ia(entry.title, link, entry.get("summary", ""))
            
            imagem = "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"
            if "media_content" in entry: imagem = entry.media_content[0]['url']
            
            conteudo = f"""
            <div style="font-family: Verdana, sans-serif; color: #002b36; background: transparent;">
                <h1 style="color: #004d40; text-align: center;">{entry.title}</h1>
                <div style="text-align: center; margin: 20px 0;">
                    <img src="{imagem}" style="width: 100%; max-width: 680px; border-radius: 15px; border: 3px solid #004d40;">
                </div>
                <div style="font-size: 16px; text-align: justify;">
                    {resenha_pt.replace('\n', '<br>')}
                </div>
                <hr style="border: 0; border-top: 1px solid #004d40; margin: 30px 0;">
                {BLOCO_FIXO_FINAL}
            </div>"""

            service.posts().insert(blogId=BLOG_ID, body={
                "title": entry.title, # O título pode ser traduzido também se preferir
                "content": conteudo,
                "status": "LIVE"
            }).execute()

            with open(ARQUIVO_LOG, "a") as f: f.write(link + "\n")
            return

if __name__ == "__main__":
    publicar_foto()
