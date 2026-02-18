from gemini_engine import GeminiEngine


def main():

    titulo = "Governo anuncia novo pacote econômico"
    conteudo = """
O governo federal anunciou nesta semana um novo pacote de medidas
voltadas ao estímulo da economia. Entre as principais ações estão
incentivos fiscais para pequenas empresas, revisão de tributos
e ampliação de linhas de crédito.
Especialistas avaliam os possíveis impactos da decisão.
"""

    categoria = "economia"

    gemini = GeminiEngine()

    texto = gemini.gerar_analise_jornalistica(
        titulo=titulo,
        conteudo_original=conteudo,
        categoria=categoria
    )

    print("\n--- TEXTO GERADO ---\n")
    print(texto)


if __name__ == "__main__":
    main()
