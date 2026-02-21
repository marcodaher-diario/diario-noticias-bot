# -*- coding: utf-8 -*-

def formatar_texto(texto):
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""
    
    # Configurações de comando centralizado (Alterando aqui, muda em todos os robôs)
    COR_MD = "rgb(7, 55, 99)"
    TAMANHO_H2 = "24px"
    TAMANHO_TEXTO = "18px"

    for linha in linhas:
        e_titulo_markdown = linha.startswith("#")
        linha_limpa = linha.strip("#* ").strip()

        # Lógica para detectar se a linha é um título
        if e_titulo_markdown or (len(linha_limpa.split()) <= 18 and not linha_limpa.endswith(".")):
            if "considerações finais" in linha_limpa.lower():
                titulo_texto = "Considerações Finais"
            else:
                titulo_texto = linha_limpa

            # --- AQUI VOCÊ CONTROLA O H2 ---
            html_final += f"""
            <h2 style="text-align:left !important; font-family:Arial !important; color:{COR_MD} !important; font-size:{TAMANHO_H2} !important; font-weight:bold !important; margin-top:30px !important; margin-bottom:10px !important; display:block !important;">
                {titulo_texto}
            </h2>
            """
        else:
            # --- AQUI VOCÊ CONTROLA O TEXTO DA POSTAGEM ---
            html_final += f"""
            <p style="text-align:justify !important; font-family:Arial !important; color:{COR_MD} !important; font-size:{TAMANHO_TEXTO} !important; margin-bottom:15px !important; line-height:1.7 !important;">
                {linha_limpa}
            </p>
            """

    return html_final


def obter_esqueleto_html(dados):
    titulo = dados.get("titulo", "")
    imagem = dados.get("imagem", "")
    texto_completo = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    # Chama a função acima que agora já vem com os tamanhos 20px e 16px
    conteudo_formatado = formatar_texto(texto_completo)

    FONTE_GERAL = "Arial, sans-serif"
    COR_MD = "rgb(7, 55, 99)"

    html = f"""
<style>
    /* Esconde o título padrão do Blogger (H3) para não duplicar com o seu H1 */
    h3.post-title, .post-title {{ display: none !important; visibility: hidden !important; }}
</style>    
<div style="max-width:900px !important; margin:auto !important; font-family:{FONTE_GERAL} !important; color:{COR_MD} !important; line-height:1.7 !important; text-align:justify !important;">

    <h1 style="text-align:center !important; font-family:{FONTE_GERAL} !important; color:{COR_MD} !important; font-size:28px !important; font-weight:bold !important; margin-bottom:20px !important; display:block !important; text-transform:uppercase !important;">
        {titulo}
    </h1>

    <div style="text-align:center !important; margin-bottom:25px !important;">
        <img src="{imagem}" style="width:100% !important; max-width:100% !important; border-radius:8px !important; box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important; height:auto !important; aspect-ratio:16/9 !important; object-fit:cover !important;">
    </div>

    <div class="conteudo-post">
        {conteudo_formatado}
    </div>

    <div style="margin-top:40px !important; padding-top:20px !important; border-top:1px solid #ddd !important; font-family:{FONTE_GERAL} !important; color:{COR_MD} !important; font-size: 15px !important; font-style: italic !important;">
        {assinatura}
    </div>
</div>
"""
    return html
