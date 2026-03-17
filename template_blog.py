def formatar_texto_para_blog(texto_bruto, titulo_principal):
    if not texto_bruto:
        return ""

    import re
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = ""
    titulo_norm = titulo_principal.strip().lower()

    for linha in linhas:
        # 1. Primeiro, transformamos o negrito da IA em tag HTML <strong>
        # Isso mantém o destaque visual sem os asteriscos
        linha_processada = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        
        # 2. Agora limpamos marcadores de estrutura (# e * das pontas)
        # O strip aqui remove os símbolos, mas preserva as tags <strong> internas
        linha_limpa = linha_processada.strip("#* ").strip()

        # 3. Ignora se for o título repetido
        if linha_limpa.lower() == titulo_norm:
            continue
        
        if not linha_limpa:
            continue

        # 4. Critério para Subtítulo (H2):
        # Removemos as tags HTML apenas para contar palavras reais no critério
        texto_para_contagem = re.sub(r"<.*?>", "", linha_limpa)
        palavras = texto_para_contagem.split()
        
        if len(palavras) <= 22 and not texto_para_contagem.endswith("."):
            html_final += f'<h2 class="subtitulo">{linha_limpa}</h2>\n'
        else:
            # 5. Parágrafo (Mantendo o negrito interno)
            html_final += f'<p class="paragrafo">{linha_limpa}</p>\n'

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
font-family:sans-serif !important;
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
font-family:sans-serif !important;
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
font-family:sans-serif !important;
color:{COR_MD} !important;
font-size:20px !important;
font-weight:bold !important;
text-transform:uppercase !important;
margin-top:25px !important;
margin-bottom:10px !important;
}}

.paragrafo {{
text-align:justify !important;
font-family:sans-serif !important;
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
