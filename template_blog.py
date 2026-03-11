# -*- coding: utf-8 -*-
import re

def formatar_texto(texto, titulo_principal):

    if texto is None:
        return ""

    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    titulo_norm = titulo_principal.strip().lower()

    contador_paragrafos = 0

    for i, linha in enumerate(linhas):

        linha_limpa = linha.strip("#* ").strip()

        # Remove repetição do título
        if linha_limpa.lower() == titulo_norm:
            continue

        # =========================
        # CONVERTER **NEGRITO**
        # =========================
        linha_limpa = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha_limpa)

        # =========================
        # DETECÇÃO DE SUBTÍTULO
        # =========================
        if i == 0 or linha.startswith("#") or (len(linha_limpa.split()) <= 15 and not linha_limpa.endswith(".")):

            contador_paragrafos = 0

            html_final += f"""
<h2 class="subtitulo">
{linha_limpa}
</h2>
"""

        else:

            contador_paragrafos += 1

            # =========================
            # SUBTÍTULO AUTOMÁTICO
            # =========================
            if contador_paragrafos == 3 and len(linha_limpa.split()) > 25:

                html_final += """
<h2 class="subtitulo">
ANÁLISE DOS DESDOBRAMENTOS
</h2>
"""

                contador_paragrafos = 0

            html_final += f"""
<p class="paragrafo">
{linha_limpa}
</p>
"""

    return html_final


# ==============================
# MONTAGEM DO HTML
# ==============================
def obter_esqueleto_html(dados):

    titulo = dados.get("titulo", "").strip()
    imagem = dados.get("imagem", "").strip()
    texto_bruto = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    conteudo_formatado = formatar_texto(texto_bruto, titulo)

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
text-decoration:none !important;
}}

.post-title a:hover,
.entry-title a:hover{{
color:rgb(10,80,140) !important;
text-decoration:none !important;
}}

.post-container {{
max-width:900px;
margin:auto;
font-family:Arial,sans-serif;
}}

.post-img {{
width:100%;
height:auto;
aspect-ratio:16/9;
object-fit:cover;
border-radius:8px;
}}

.subtitulo {{
text-align:left;
font-family:Arial;
color:{COR_MD};
font-size:20px;
font-weight:bold;
text-transform:uppercase;
margin-top:25px;
margin-bottom:10px;
}}

.paragrafo {{
text-align:justify;
font-family:Arial;
color:{COR_MD};
font-size:18px;
line-height:1.6;
margin-bottom:15px;
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
