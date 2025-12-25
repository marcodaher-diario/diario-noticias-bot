import feedparser
import re
import os
from deep_translator import GoogleTranslator
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from configuracoes import BLOCO_FIXO_FINAL

# CONFIGURAÇÕES MD ARTE FOTO
BLOG_ID = "5852420775961497718"
RSS_FONTES = [
    "https://petapixel.com/feed/",
    "https://digital-photography-school.com/feed/",
    "https://www.thephoblographer.com/feed/"
]
ARQUIVO_LOG = "posts_foto_publicados.txt"
SCOPES = ["https://www.googleapis.com/auth/blogger"]

translator = GoogleTranslator(source='en', target='pt')

def traduzir(texto):
    try:
        if not texto: return ""
        texto_limpo = re.sub(r"<[^>]+>", "", texto)
        return translator.translate(texto_limpo[:4500])
    except: return texto

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

            print(f"📸 Traduzindo: {entry.title}")
            tit_pt = traduzir(entry.title)
            res_pt = traduzir(entry.get("summary", entry.get("description", "")))
            
            # Imagem padrão 16:9 conforme sua preferência
            imagem = "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=800"
            if "media_content" in entry: imagem = entry.media_content[0]['url']
            
            conteudo = f"""
            <div style="font-family:Arial; text-align:justify;">
                <h2 style="text-align:center;">{tit_pt}</h2>
                <div style="text-align:center; margin:20px 0;">
                    <img src="{imagem}" width="680" height="383" style="max-width:100%; border-radius:10px;">
                </div>
                <p>{res_pt}</p>
                <hr>
                {BLOCO_FIXO_FINAL}
            </div>"""

            service.posts().insert(blogId=BLOG_ID, body={
                "title": tit_pt,
                "content": conteudo,
                "labels": ["Fotografia", "Tutorial", "Dicas"],
                "status": "LIVE"
            }).execute()

            with open(ARQUIVO_LOG, "a") as f: f.write(link + "\n")
            return

if __name__ == "__main__":
    publicar_foto()
