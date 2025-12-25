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
            
            # Código adaptado para fundo transparente e contraste com verde água
            conteudo = f"""
            <div style="font-family: 'Verdana', sans-serif; color: #002b36; line-height: 1.6; background: transparent;">
                
                <h1 style="color: #004d40; text-align: center; font-size: 26px; border-bottom: 2px solid #004d40; padding-bottom: 10px;">
                    {tit_pt}
                </h1>
                
                <div style="text-align: center; margin: 25px 0;">
                    <img src="{imagem}" style="width: 100%; max-width: 680px; height: auto; border-radius: 15px; border: 3px solid #004d40;">
                </div>

                <div style="margin-bottom: 30px; padding: 10px;">
                    <p style="font-size: 18px; color: #00332e; font-weight: bold; text-shadow: 1px 1px 0px rgba(255,255,255,0.3);">
                        {res_pt}
                    </p>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" target="_blank" style="background-color: #004d40; color: white; padding: 12px 25px; text-decoration: none; border-radius: 50px; font-weight: bold; font-size: 14px; box-shadow: 2px 2px 5px rgba(0,0,0,0.2);">
                        LER TUTORIAL ORIGINAL
                    </a>
                </div>

                <div style="margin-top: 50px; background: transparent;">
                    {BLOCO_FIXO_FINAL}
                </div>
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
