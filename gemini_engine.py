
# -*- coding: utf-8 -*-

import os
import re
import time
from google import genai
from google.api_core import exceptions


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

        # Estratégia de Fallback: 3 Modelos em 3 Ciclos
        self.modelos_fallback = [
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-2.5-pro"
        ]

    def _limpar_e_formatar_markdown(self, texto):
        """
        Converte Markdown (Negrito, Itálico, Listas) para HTML
        e remove marcadores de títulos excedentes.
        """

        if not texto:
            return ""

        # 1. NEGRITO
        texto = re.sub(
            r'\*\*(.*?)\*\*',
            r'<strong>\1</strong>',
            texto
        )

        # 2. ITÁLICO
        texto = re.sub(
            r'\*(.*?)\*',
            r'<em>\1</em>',
            texto
        )

        texto = re.sub(
            r'_(.*?)_',
            r'<em>\1</em>',
            texto
        )

        # 3. LISTAS
        texto = re.sub(
            r'^\s*[\*\-]\s+(.*)',
            r'<li>\1</li>',
            texto,
            flags=re.MULTILINE
        )

        # 4. TÍTULOS
        texto = re.sub(r'#+\s?', '', texto)

        # 5. LIMPEZA FINAL
        texto = texto.replace('*', '').replace('_', '')

        return texto.strip()

    def gerar_analise_jornalistica(self, titulo, resumo, categoria):

        
        prompt = f"""
Atue como um jornalista profissional, com ampla experiência em jornalismo informativo, reportagem, análise de notícias e produção de conteúdo digital.

Sua missão é produzir uma matéria jornalística original, completa, confiável e bem estruturada para o Diário de Notícias, utilizando exclusivamente as informações fornecidas abaixo.

INFORMAÇÕES DA NOTÍCIA:

Título original: {titulo}

Resumo e informações disponíveis: {resumo}

Editoria: {categoria}

==================================================
1. COMPROMISSO COM A VERDADE E A CONFIABILIDADE
==================================================

Esta é a diretriz mais importante de todas.

- Utilize somente informações presentes no material fornecido.
- Nunca invente nomes, datas, números, valores, estatísticas, locais, acontecimentos ou declarações.
- Não crie entrevistas, depoimentos ou citações atribuídas a pessoas ou instituições.
- Não invente explicações para fatos que não estejam esclarecidos.
- Não transforme suspeitas, acusações ou hipóteses em fatos comprovados.
- Diferencie claramente informações confirmadas, declarações oficiais e alegações.
- Não apresente como oficial uma informação cuja origem não esteja identificada.
- Se o material for insuficiente, produza uma matéria mais curta e objetiva.
- Nunca aumente artificialmente o texto para alcançar a quantidade mínima de palavras.
- Não utilize conhecimentos gerais para completar lacunas com informações específicas que não foram fornecidas.

A precisão jornalística tem prioridade absoluta sobre a extensão do artigo.

==================================================
2. ORIGINALIDADE E QUALIDADE JORNALÍSTICA
==================================================

- Escreva um texto inteiramente original.
- Não copie frases ou parágrafos da notícia original.
- Reorganize as informações com uma narrativa própria, preservando rigorosamente o significado dos fatos.
- Utilize linguagem jornalística profissional, clara, natural e objetiva.
- Evite expressões repetitivas, clichês e construções artificiais.
- Não utilize linguagem sensacionalista ou exagerada.
- Não faça propaganda de pessoas, empresas, partidos ou instituições.
- Não apresente opiniões pessoais.

==================================================
3. EXTENSÃO E DESENVOLVIMENTO
==================================================

O artigo deverá ter preferencialmente entre 600 e 750 palavras.

Essa extensão tem como objetivo produzir matérias completas, com bom desenvolvimento e conteúdo relevante para o leitor.

Entretanto:
- Não repita informações para aumentar o tamanho.
- Não crie parágrafos sem conteúdo relevante.
- Não invente contextualizações para preencher espaço.
- Se as informações disponíveis não permitirem alcançar 600 palavras com qualidade, escreva menos.
- Priorize sempre a consistência, a clareza e a confiabilidade.

==================================================
4. ESTRUTURA OBRIGATÓRIA DA MATÉRIA
==================================================

TÍTULO:
Crie um título informativo, atrativo e adequado ao assunto.
Não utilize sensacionalismo, exageros ou promessas que a notícia não sustente.

LIDE:
O primeiro parágrafo deve apresentar imediatamente o fato mais importante, respondendo, sempre que possível, às perguntas:
Quem? O quê? Quando? Onde? Como? Por quê?

Não invente respostas para perguntas que não possam ser esclarecidas pelo material disponível.

DESENVOLVIMENTO:
Organize as informações em ordem cronológica ou por importância jornalística.

Utilize pelo menos dois subtítulos quando a extensão e o conteúdo justificarem.

Os subtítulos devem:
- Ser objetivos e informativos.
- Facilitar a leitura e a compreensão.
- Dividir o assunto em blocos temáticos.
- Evitar frases genéricas ou repetitivas.

PARÁGRAFOS:
- Prefira parágrafos curtos, com aproximadamente 3 a 5 linhas em uma tela comum.
- Desenvolva uma ideia principal por parágrafo.
- Evite blocos muito extensos de texto.
- Utilize transições naturais entre os assuntos.

CONCLUSÃO:
Finalize retomando os aspectos mais relevantes da notícia.
Apresente possíveis consequências ou desdobramentos somente quando houver informações concretas que os sustentem.
Não faça previsões especulativas nem apresente opiniões pessoais.

==================================================
5. IMPARCIALIDADE E RESPONSABILIDADE
==================================================

Mantenha postura rigorosamente imparcial, especialmente nas editorias de política, segurança pública e economia.

- Não favoreça partidos, governos, autoridades ou grupos políticos.
- Não utilize adjetivos que induzam o leitor a uma conclusão.
- Não trate acusações como condenações.
- Respeite a presunção de inocência.
- Não atribua intenções ou motivações sem evidências.
- Quando houver versões diferentes no material fornecido, apresente-as de maneira equilibrada.
- Não crie uma segunda versão apenas para aparentar equilíbrio quando ela não estiver disponível.

==================================================
6. ADAPTAÇÃO À EDITORIA
==================================================

Adapte a abordagem jornalística ao assunto:

POLÍTICA E GOVERNO:
Priorize decisões, medidas, debates, ações governamentais e seus efeitos para a população.

ECONOMIA E FINANÇAS:
Explique indicadores, mudanças econômicas, impactos financeiros e consequências para consumidores, trabalhadores e empresas, sem inventar valores ou projeções.

SEGURANÇA E POLÍCIA:
Apresente os fatos com responsabilidade, distinguindo investigação, suspeita, prisão, acusação e condenação.

SAÚDE E SOCIEDADE:
Explique informações de interesse público com clareza, sem criar recomendações médicas ou conclusões científicas não sustentadas.

TECNOLOGIA E CIÊNCIA:
Explique novidades, descobertas e avanços de maneira acessível, sem exagerar resultados ou prometer benefícios não comprovados.

OPORTUNIDADES E SERVIÇOS:
Destaque informações práticas, requisitos, prazos, condições e orientações disponíveis no material original. Não invente inscrições, datas, valores ou benefícios.

==================================================
7. SEO E EXPERIÊNCIA DO LEITOR
==================================================

- Utilize naturalmente as palavras-chave relacionadas ao assunto.
- Inclua os principais termos da notícia no título e nos primeiros parágrafos, quando apropriado.
- Utilize subtítulos relacionados ao conteúdo.
- Evite repetição artificial de palavras-chave.
- Não escreva pensando apenas nos mecanismos de busca.
- Priorize uma leitura agradável, informativa e fluida.
- Produza conteúdo adequado para computadores e dispositivos móveis.

==================================================
8. FORMATAÇÃO DO TEXTO
==================================================

- Utilize subtítulos destacados em negrito com Markdown.
- Utilize negrito apenas para destacar informações realmente importantes.
- Não utilize tabelas.
- Não utilize emojis.
- Não utilize listas extensas sem necessidade.
- Não inclua links inventados.
- Não inclua referências bibliográficas fictícias.
- Não inclua marcações de código ou explicações sobre a produção do artigo.

==================================================
9. INSTRUÇÃO FINAL
==================================================

Entregue exclusivamente a matéria jornalística final, pronta para ser utilizada em uma postagem do Blogger.

Não escreva introduções como "Aqui está a matéria".
Não explique as instruções utilizadas.
Não inclua observações adicionais.
Não inclua comentários sobre o processo de redação.

A matéria deve transmitir credibilidade, clareza, profissionalismo e responsabilidade jornalística.
"""


        resposta = self._executar_com_resiliencia(prompt)

        if not resposta:
            return None

        return self._limpar_e_formatar_markdown(resposta)

    def _executar_com_resiliencia(self, prompt):
        """
        Lógica de 9 tentativas (3 ciclos x 3 modelos)
        sem alterar os prompts originais.
        """

        tentativa_total = 1

        for ciclo in range(1, 4):

            for modelo in self.modelos_fallback:

                try:
                    print(
                        f"Tentativa {tentativa_total}/9 | "
                        f"Ciclo {ciclo} | Usando: {modelo}"
                    )

                    response = self.client.models.generate_content(
                        model=modelo,
                        contents=prompt
                    )

                    if (
                        response
                        and hasattr(response, 'text')
                        and response.text
                    ):
                        return response.text

                except Exception as e:

                    erro_msg = str(e).upper()

                    # Identifica erros de indisponibilidade, timeout ou cota.
                    if any(
                        x in erro_msg
                        for x in [
                            "503",
                            "UNAVAILABLE",
                            "DEADLINE",
                            "429",
                            "QUOTA"
                        ]
                    ):

                        print(
                            f"⚠️ Modelo {modelo} indisponível "
                            "ou lotado. Pulando para o próximo..."
                        )

                        time.sleep(5)

                    else:

                        print(
                            f"❌ Erro crítico no modelo {modelo}: {e}"
                        )

                tentativa_total += 1

        return None

    def gerar_query_visual(self, titulo, resumo):
        """
        Gera uma query de busca em inglês otimizada para Pexels/Unsplash
        com base no contexto da notícia.
        """

        prompt = f"""
Com base no título e resumo da notícia abaixo, gere APENAS uma sequência de 3 a 4 palavras-chave
em INGLÊS que descrevam uma imagem fotográfica ideal para ilustrar esta matéria em um blog de notícias.

Diretrizes:
- Use apenas substantivos e adjetivos visuais.
- Foque no cenário, objetos ou clima da notícia (ex: "police lights night", "stock market glow", "city explosion smoke").
- Não use verbos ou frases completas.
- Retorne APENAS as palavras em inglês, sem pontuação extra.

Notícia: {titulo}
Resumo: {resumo}
"""

        resposta = self._executar_com_resiliencia(prompt)

        if resposta:
            return resposta.strip()

        return None
