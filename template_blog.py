def obter_esqueleto_html(dados):
    cor_base = "#003366"  # Azul Marinho MD
       
    html = f"""
    <div style="color: {cor_base}; font-family: Arial, sans-serif; line-height: 1.6;">
        <h1 style="font-weight: bold; margin-bottom: 20px; text-align: center; font-size: x-large;">
            {dados['titulo'].upper()}
        </h1>

        <div style='text-align:center; margin-bottom:20px;'>
            <img src='{dados['img_topo']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'/>
        </div>

        <div style='font-size: medium; text-align:justify; margin:10px 0;'>
            {dados['intro']}
        </div>

        <p style='font-size: large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            {dados['sub1']}
        </p>
        <div style='font-size: medium; text-align:justify; margin:10px 0;'>
            {dados['texto1']}
        </div>

        <div style='text-align:center; margin:30px 0;'>
            <img src='{dados['img_meio']}' style='width:100%; aspect-ratio:16/9; object-fit:cover; border-radius:10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);'/>
        </div>

        <p style='font-size: large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            {dados['sub2']}
        </p>
        <div style='font-size: medium; text-align:justify; margin:10px 0;'>
            {dados['texto2']}
        </div>

        <p style='font-size: large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            {dados['sub3']}
        </p>
        <div style='font-size: medium; text-align:justify; margin:10px 0;'>
            {dados['texto3']}
        </div>

        <p style='font-size: large; font-weight:bold; text-align:left; margin:25px 0 5px 0;'>
            CONSIDERAÇÕES FINAIS
        </p>
        <div style='font-size: medium; text-align:justify; margin:10px 0;'>
            {dados['texto_conclusao']}
        </div>

        <div style='margin-top: 10px; padding-top: 0;'>
            {dados['assinatura']}
        </div>
    </div>
    """
    return html
