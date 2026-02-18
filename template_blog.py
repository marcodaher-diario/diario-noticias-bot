# -*- coding: utf-8 -*-

def formatar_paragrafos(texto):
    paragrafos = [p.strip() for p in texto.split("\n") if p.strip()]
    return "".join([f"<p>{p}</p>" for p in paragrafos])


def obter_esqueleto_html(dados):

    titulo = dados.get("titulo", "")
    imagem = dados.get("imagem", "")
    contexto = formatar_paragrafos(dados.get("contexto", ""))
    desdobramentos = formatar_paragrafos(dados.get("desdobramentos", ""))
    impactos = formatar_paragrafos(dados.get("impactos", ""))
    conclusao = formatar_paragrafos(dados.get("conclusao", ""))
    assinatura = dados.get("assinatura", "")

    html = f"""
    <div style="max-width:900px;margin:auto;font-family:Arial,Helvetica,sans-serif;color:#1a1a1a;line-height:1.6;">

        <h1 style="text-align:center;font-size:26px;margin-bottom:20px;">
            {titulo}
        </h1>

        <div style="text-align:center;margin-bottom:25px;">
            <img src="{imagem}" style="width:100%;border-radius:8px;">
        </div>

        <h2 style="margin-top:30px;">Contexto</h2>
        {contexto}

        <h2 style="margin-top:30px;">Desdobramentos</h2>
        {desdobramentos}

        <h2 style="margin-top:30px;">Impactos</h2>
        {impactos}

        <h2 style="margin-top:30px;">Considerações Finais</h2>
        {conclusao}

        <div style="margin-top:40px;padding-top:20px;border-top:1px solid #ddd;">
            {assinatura}
        </div>

    </div>
    """

    return html
