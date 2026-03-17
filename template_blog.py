# -*- coding: utf-8 -*-
import re

def formatar_texto(texto, titulo_principal):
    # 1. Verificação de segurança inicial
    if not texto or not str(texto).strip():
        return "<p class='paragrafo'>Conteúdo não disponível.</p>"

    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    titulo_norm = titulo_principal.strip().lower()

    for i, linha in enumerate(linhas):
        # Limpeza para comparação e detecção
        texto_puro = linha.strip("#* ").strip()

        # Pular se for exatamente o título, mas garantir que não estamos deletando o texto todo
        if texto_puro.lower() == titulo_norm and len(linhas) > 1:
            continue

        # Processar Negrito (sempre na linha original)
        linha_com_negrito = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        
        # Limpar markdowns estruturais após converter o negrito
        linha_limpa = linha_com_negrito.strip("#* ").strip()

        # Se após a limpeza a linha ficou vazia, pula
        if not linha_limpa:
            continue

        # DETECÇÃO DE SUBTÍTULO
        # Se começar com # OU for curto/sem ponto
        if linha.startswith("#") or (len(texto_puro.split()) <= 15 and not texto_puro.endswith(".")):
            html_final += f'\<h2 class="subtitulo">{linha_limpa}</h2>\n'
        else:
            html_final += f'\<p class="paragrafo">{linha_limpa}</p>\n'

    # 2. SE APÓS TUDO O HTML CONTINUAR VAZIO (Segurança contra o Erro que você recebeu)
    if not html_final.strip():
        # Caso o filtro de título tenha apagado tudo, retornamos o texto original limpo
        texto_seguro = texto.replace("**", "").replace("#", "").strip()
        return f'<p class="paragrafo">{texto_seguro}</p>'

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
font-family:Arial, sans-serif !important;
}}

.post-img {{
width:100% !important;
max-width:100% !important;
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
"""
