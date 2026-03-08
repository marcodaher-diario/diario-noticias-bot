# -*- coding: utf-8 -*-

def formatar_texto(texto, titulo_principal):
    """
    Processa o corpo do texto: H2 para subtítulos e P para parágrafos.
    Remove repetições do título principal dentro do corpo do texto.
    Também cria subtítulos automáticos quando o texto fica muito longo.
    """
    if texto is None:
        return ""
        
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    COR_MD = "rgb(7, 55, 99)"
    titulo_norm = titulo_principal.strip().lower()

    contador_paragrafos = 0

    for i, linha in enumerate(linhas):

        linha_limpa = linha.strip("#* ").strip()
        
        # Pula a linha se for repetição do título
        if linha_limpa.lower() == titulo_norm:
            continue

        # ======================================
        # SUBTÍTULO DETECTADO OU PRIMEIRA LINHA
        # ======================================
        if i == 0 or linha.startswith("#") or (len(linha_limpa.split()) <= 15 and not linha_limpa.endswith(".")):

            contador_paragrafos = 0

            html_final += f"""
            <h2 style="text-align:left !important; font-family:Arial !important; color:{COR_MD} !important; 
                       font-size:20px !important; font-weight:bold !important; text-transform:uppercase !important; 
                       margin-top:25px !important; margin-bottom:10px !important;">
                {linha_limpa}
            </h2>
            """

        else:

            contador_paragrafos += 1

            # ================================
            # SUBTÍTULO AUTOMÁTICO
            # ================================
            if contador_paragrafos == 3 and len(linha_limpa.split()) > 25:

                subtitulo_auto = "ANÁLISE DOS DESDOBRAMENTOS"

                html_final += f"""
                <h2 style="text-align:left !important; font-family:Arial !important; color:{COR_MD} !important; 
                           font-size:20px !important; font-weight:bold !important; text-transform:uppercase !important; 
                           margin-top:25px !important; margin-bottom:10px !important;">
                    {subtitulo_auto}
                </h2>
                """

                contador_paragrafos = 0

            # Ordem 6: Texto - Fonte 18, Justificado, Cor MD
            html_final += f"""
            <p style="text-align:justify !important; font-family:Arial !important; color:{COR_MD} !important; 
                      font-size:18px !important; line-height:1.6 !important; margin-bottom:15px !important;">
                {linha_limpa}
            </p>
            """

    return html_final

# ================================
# MONTAGEM DO HTML
# ================================
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
</style>

<div style="max-width:900px !important; margin:auto !important; font-family:Arial, sans-serif !important;">

<div style="text-align:center !important; margin-bottom:25px !important;">
<img src="{imagem}" alt="{titulo}" style="width:100% !important; height:auto !important; aspect-ratio:16/9 !important; object-fit:cover !important; border-radius:8px !important;">
</div>

<div class="conteudo-post">
{conteudo_formatado}
</div>

<div style="margin-top:40px !important; padding-top:20px !important; border-top:1px solid #eee !important; color:{COR_MD} !important;">
{assinatura}
</div>

</div>
"""

    return html
