# -*- coding: utf-8 -*-

def formatar_texto(texto, titulo_principal):
    """
    Processa o corpo do texto: H2 para subtítulos e P para parágrafos.
    Remove repetições do título principal dentro do corpo do texto.
    """
    if texto is None:
        return ""
        
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    COR_MD = "rgb(7, 55, 99)"
    titulo_norm = titulo_principal.strip().lower()

    for linha in linhas:
        linha_limpa = linha.strip("#* ").strip()
        
        # Pula a linha se for repetição do título (limpeza inteligente)
        if linha_limpa.lower() == titulo_norm:
            continue

        # Ordem 5: Subtítulo H2 - Arial 20, Bold, Esquerda, Cor MD, Maiúsculas
        if linha.startswith("#") or (len(linha_limpa.split()) <= 15 and not linha_limpa.endswith(".")):
            html_final += f"""
            <h2 style="text-align:left !important; font-family:Arial !important; color:{COR_MD} !important; 
                       font-size:20px !important; font-weight:bold !important; text-transform:uppercase !important; 
                       margin-top:25px !important; margin-bottom:10px !important;">
                {linha_limpa}
            </h2>
            """
        else:
            # Ordem 6: Texto - Fonte 18, Justificado, Cor MD
            html_final += f"""
            <p style="text-align:justify !important; font-family:Arial !important; color:{COR_MD} !important; 
                      font-size:18px !important; line-height:1.6 !important; margin-bottom:15px !important;">
                {linha_limpa}
            </p>
            """
    return html_final

def obter_esqueleto_html(dados):
    """
    Gera o HTML final. 
    A Ordem 2 (Título) é cumprida via CSS injetado para formatar o título nativo do Blogger.
    """
    titulo = dados.get("titulo", "").strip()
    imagem = dados.get("imagem", "").strip()
    texto_bruto = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    conteudo_formatado = formatar_texto(texto_bruto, titulo)
    COR_MD = "rgb(7, 55, 99)"

    # O CSS abaixo captura os seletores mais comuns de títulos do Blogger
    return f"""
<style>
    h1.post-title, h2.post-title, h3.post-title, 
    h1.entry-title, h2.entry-title, h3.entry-title,
    .post-title, .entry-header, .post-header,
    h1.post-title a, h2.post-title a, h3.post-title a,
    .post-title a, .entry-title a {{
        text-align:center !important; 
        font-family:Arial, sans-serif !important; 
        font-size:28px !important; 
        font-weight:bold !important; 
        color:{COR_MD} !important; 
        text-transform:uppercase !important;
        margin-bottom:20px !important;
        margin-top:10px !important;
        
    }}
</style>

<div style="max-width:900px !important; margin:auto !important; font-family:Arial, sans-serif !important;">

    <div style="text-align:center !important; margin-bottom:25px !important;">
        <img src="{imagem}" alt="{titulo}" style="width:100% !important; height:auto !important; aspect-ratio:16/9 !important; object-fit:cover !important; border-radius:8px !important; display:block !important; margin:auto !important;">
    </div>

    <div class="conteudo-post">
        {conteudo_formatado}
    </div>

    <div style="margin-top:40px !important; padding-top:20px !important; border-top:1px solid #eee !important; color:{COR_MD} !important;">
        {assinatura}
    </div>

</div>
"""
