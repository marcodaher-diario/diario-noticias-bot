# =========================================================
if temp:
blocos.append(" ".join(temp))
return "".join(f"<p>{b}</p>" for b in blocos)


# =============================
# CLASSIFICAÇÃO
# =============================


def verificar_assunto(titulo, texto):
base = f"{titulo} {texto}".lower()
if any(p in base for p in PALAVRAS_POLITICA): return "politica"
if any(p in base for p in PALAVRAS_ECONOMIA): return "economia"
return "geral"


# =============================
# BUSCA PRINCIPAL
# =============================


def noticia_recente(entry, horas=48):
data = entry.get("published_parsed") or entry.get("updated_parsed")
if not data:
return False
return datetime.fromtimestamp(time.mktime(data)) >= datetime.now() - timedelta(hours=horas)




def buscar_noticias(tipo, limite=5):
noticias = []
for feed_url in RSS_FEEDS:
feed = feedparser.parse(feed_url)
fonte = feed.feed.get("title", "Fonte")
for entry in feed.entries:
if not noticia_recente(entry): continue
titulo = entry.get("title", "")
texto = entry.get("summary", "")
link = entry.get("link", "")
if not titulo or not link or ja_publicado(link): continue
if verificar_assunto(titulo, texto) != tipo: continue
if conteudo_insuficiente(texto):
alternativa = buscar_conteudo_alternativo(titulo)
if not alternativa:
print(f"⛔ BLOQUEADO (conteúdo pobre): {titulo}")
continue
noticias.append(alternativa)
else:
noticias.append({
"titulo": titulo,
"texto": texto,
"link": link,
"fonte": fonte,
"imagem": extrair_imagem(entry)
})
random.shuffle(noticias)
return noticias[:limite]


# =============================
# GERAÇÃO HTML
# =============================

def gerar_conteudo(n):
    texto_limpo = quebrar_paragrafos(
        re.sub(r"<[^>]+>", "", n["texto"])
    )

    # BLOCO DE MÍDIA
    if n.get("video_id"):
        media_html = f"""
        <div class="auto-video">
            <iframe src="https://www.youtube.com/embed/{n['video_id']}"
                loading="lazy"
                allowfullscreen></iframe>
        </div>
        """
    else:
        media_html = f"""
        <div class="auto-media">
            <img src="{n['imagem']}" alt="{n['titulo']}">
        </div>
        """

    return f"""
    <div class="auto-post-body">

        <h2 style="text-align:center;">{n['titulo']}</h2>

        {media_html}

        <p><b>Fonte:</b> {n['fonte']}</p>

        <div style="text-align:justify;">
            {texto_limpo}
        </div>

        <p style="text-align:center; margin-top:20px;">
            <a href="{n['link']}" target="_blank">
                🔗 Leia a matéria original
            </a>
        </p>

    </div>
    """
    
# =============================
# EXECUÇÃO
# =============================

def executar():
service = autenticar_blogger()
hora = datetime.now().hour
tipo = "politica" if hora < 12 else "geral" if hora < 18 else "economia"
noticias = buscar_noticias(tipo)
for n in noticias:
try:
service.posts().insert(
blogId=BLOG_ID,
body={"title": n['titulo'], "content": gerar_conteudo(n), "status": "LIVE"}
).execute()
registrar_publicacao(n['link'])
print(f"✅ Publicado: {n['titulo']}")
except Exception as e:
print(f"❌ Erro ao publicar: {e}")


if __name__ == "__main__":
executar()
