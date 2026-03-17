# -*- coding: utf-8 -*-
import re

def formatar_texto(texto, titulo_principal):

    if texto is None:
        return ""

    linhas = [l.rstrip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    titulo_norm = titulo_principal.strip().lower()

    lista_aberta = False

    for i, linha in enumerate(linhas):

        linha_limpa = linha.strip()
    
        # converter **negrito**
        linha_limpa = re.sub(r"\*\*([^\*]+)\*\*", r"<strong>\1</strong>", linha_limpa)
    
        # remove markdown
        linha_limpa = linha_limpa.strip("# ").strip()
    
        # remove repetição do título
        if linha_limpa.lower() == titulo_norm:
            continue

        palavras = linha_limpa.split()

        # =========================
        # DETECTAR LISTAS
        # =========================
        if linha.startswith("- ") or linha.startswith("* ") or re.match(r"^\d+\.", linha):

            if not lista_aberta:
                html_final += "\n<ul class='lista-post'>\n"
                lista_aberta = True

            item = re.sub(r"^[-*\d. ]+", "", linha_limpa)

            html_final += f"<li>{item}</li>\n"
            continue

        else:
            if lista_aberta:
                html_final += "</ul>\n"
                lista_aberta = False

        # =========================
        # DETECÇÃO DE SUBTÍTULO (H2)
        # =========================
        condicao_subtitulo = (
            (i == 0 and 3 <= len(palavras) <= 22)
            or (
                3 <= len(palavras) <= 22
                and not linha_limpa.endswith(".")
                and not linha_limpa.endswith(":")
                and linha_limpa[0].isupper()
            )
        )

        if condicao_subtitulo:

            html_final += f"""
<h2 class="subtitulo">
{linha_limpa}
</h2>
"""
            continue

        # =========================
        # PARÁGRAFO NORMAL
        # =========================
        html_final += f"""
<p class="paragrafo">
{linha_limpa}
</p>
"""

    if lista_aberta:
        html_final += "</ul>\n"

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
width:100% !important;
height:auto !important;
aspect-ratio:16/9 !important;
object-fit:cover !important;
border-radius:8px !important;
}}

.subtitulo {{
text-align:left !important;
font-family:Arial, sans-serif !important;
color:{COR_MD} !important;
font-size:20px !important;
font-weight:bold !important;
text-transform:uppercase !important;
margin-top:25px !important;
margin-bottom:10px !important;
}}

.paragrafo {{
text-align:justify !important;
font-family:Arial, sans-serif !important;
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
