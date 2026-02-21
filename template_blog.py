# -*- coding: utf-8 -*-

def formatar_texto(texto):
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]
    html_final = ""

    for linha in linhas:
        # Detectar se é título (pelo # ou pelas regras de tamanho/ponto)
        e_titulo_markdown = linha.startswith("#")
        
        # --- O AJUSTE ESTÁ AQUI ---
        # .strip("#* ") remove hashtags e asteriscos de AMBOS os lados (início e fim)
        linha_limpa = linha.strip("#* ").strip()

        if e_titulo_markdown or (len(linha_limpa.split()) <= 18 and not linha_limpa.endswith(".")):
            # Formatação de Título
            if "considerações finais" in linha_limpa.lower():
                titulo_texto = "Considerações Finais"
            else:
                titulo_texto = linha_limpa

            html_final += f"""
            <h2 style="text-align:left;font-family:Arial;color:rgb(7,55,99);font-size:large;font-weight:bold;margin-top:30px;">
            {titulo_texto}
            </h2>
            """
        else:
            # Formatação de Parágrafo
            html_final += f"""
            <p style="text-align:justify;font-family:Arial;color:rgb(7,55,99);font-size:medium;margin-bottom:15px;">
            {linha_limpa}
            </p>
            """

    return html_final


def obter_esqueleto_html(dados):

    titulo = dados.get("titulo", "")
    imagem = dados.get("imagem", "")
    texto_completo = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    conteudo_formatado = formatar_texto(texto_completo)

    FONTE_GERAL = "Arial, sans-serif"
    COR_MD = "rgb(7, 55, 99)"

html = f"""
<div style="max-width:900px !important; margin:auto !important; font-family:{FONTE_GERAL} !important; color:{COR_MD} !important; line-height:1.7 !important; text-align:justify !important;">

    <h3 style="text-align:center !important; font-family:{FONTE_GERAL} !important; color:{COR_MD} !important; font-size:28px !important; font-weight:bold !important; margin-bottom:20px !important; display:block !important; text-transform:uppercase !important;">
        {titulo}
    </h3>

    <div style="text-align:center !important; margin-bottom:25px !important;">
        <img src="{imagem}" style="width:100% !important; max-width:100% !important; border-radius:8px !important; box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important; height:auto !important; aspect-ratio:16/9 !important; object-fit:cover !important;">
    </div>

    <div class="conteudo-post" style="font-size:17px !important; color:{COR_MD} !important;">
        {conteudo_formatado}
    </div>

    <div style="margin-top:40px !important; padding-top:20px !important; border-top:1px solid #ddd !important; font-family:{FONTE_GERAL} !important; color:{COR_MD} !important; font-size: 15px !important; font-style: italic !important;">
        {assinatura}
    </div>

</div>
"""
return html
