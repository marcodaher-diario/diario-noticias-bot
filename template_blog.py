# -*- coding: utf-8 -*-

def formatar_texto_para_blog(texto_bruto, titulo_principal):
    """
    Esta função organiza o conteúdo em HTML. 
    A limpeza pesada de Markdown (Negritos e Símbolos) já foi feita pelo GeminiEngine.
    """
    if not texto_bruto:
        return ""

    # Divide o texto em blocos para identificar o que é Subtítulo ou Parágrafo
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = ""
    titulo_norm = titulo_principal.strip().lower()

    for linha in linhas:
        # 1. Ignora se for o título repetido
        if linha.lower() == titulo_norm:
            continue

        # 2. Critério para Subtítulo (H2):
        # Linhas curtas (até 15 palavras) e que não terminam com ponto final
        palavras = linha.split()
        if len(palavras) <= 15 and not linha.endswith("."):
            html_final += f'\n<h2 class="subtitulo">\n{linha}\n</h2>\n'
        else:
            # 3. Caso contrário, é Parágrafo
            html_final += f'\n<p class="paragrafo">\n{linha}\n</p>\n'

    return html_final


# ==============================
# MONTAGEM DO HTML (MANTIDA INTACTA)
# ==============================
def obter_esqueleto_html(dados):

    titulo = dados.get("titulo", "").strip()
    imagem = dados.get("imagem", "").strip()
    texto_bruto = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    # Chama a função de organização acima
    conteudo_formatado = formatar_texto_para_blog(texto_bruto, titulo)

    COR_MD = "rgb(7,55,99)"

    html = f"""
<style>

.post-title,
.entry-title,
h3.post-title.entry-title{{
text-align:center !important;
margin-top:10px !important;
margin-bottom:20px !important;
font-family:Arial, sans-serif !important;
font-size:28px !important;
font-weight:bold !important;
text-transform:uppercase !important;
}}

.post-title a,
.entry-title a,
h3.post-title.entry-title a{{
display:block !important;
color:{COR_MD} !important;
}}

.post-title a:hover,
.entry-title a:hover{{
color:rgb(10,80,140) !important;
}}

.post-container {{
max-width:900px;
margin:auto;
font-family:Arial,sans-serif !important;
}}

.post-img {{
width:100%;
height:auto;
aspect-ratio:16/9;
object-fit:cover;
border-radius:8px !important;
}}

.subtitulo {{
text-align:left !important;
font-family:Arial,sans-serif !important;
color:{COR_MD} !important;
font-size:20px !important;
font-weight:bold !important;
text-transform:uppercase !important;
margin-top:25px !important;
margin-bottom:10px !important;
}}

.paragrafo {{
text-align:justify !important;
font-family:Arial,sans-serif !important;
color:{COR_MD} !important;
font-size:18px !important;
line-height:1.6 !important;
margin-bottom:15px !important;
}}

</style>

<div class="post-container">

<div style="text-align:center; margin-bottom:25px;">
<img src="{imagem}" alt="{titulo}" class="post-img">
</div>

<div class="conteudo-post">
{conteudo_formatado}
</div>

{assinatura}

</div>
"""

    return html
