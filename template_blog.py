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

    html = f"""
    <div style="max-width:900px;margin:auto;">

        <h1 style="text-align:center;font-family:Arial;color:rgb(7,55,99);font-size:x-large;font-weight:bold;margin-bottom:20px;">
            {titulo}
        </h1>

        <div style="text-align:center;margin-bottom:25px;">
            <img src="{imagem}" style="width:100%;border-radius:8px;">
        </div>

        {conteudo_formatado}

        <div style="margin-top:40px;padding-top:20px;border-top:1px solid #ddd;font-family:Arial;color:rgb(7,55,99);">
            {assinatura}
        </div>

    </div>
    """

    return html
