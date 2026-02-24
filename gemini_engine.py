# -*- coding: utf-8 -*-

import os
from google import genai


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def gerar_analise_jornalistica(self, titulo, resumo, categoria):

        prompt = f"""
Atue como um Jornalista Sênior com 20 anos de experiência em hard news e reportagem investigativa.

Seu objetivo: Redigir um artigo jornalístico de fôlego baseado nas informações que fornecerei abaixo. O texto deve seguir rigorosamente os padrões de qualidade de veículos como The New York Times ou BBC.

Informações base:

Título da notícia: {titulo}

Resumo da notícia:
{resumo}

Categoria: {categoria}

Diretrizes Obrigatórias:

Tom e Estilo: Imparcial, técnico e analítico. Use linguagem clara, objetiva e evite adjetivos desnecessários ou termos sensacionalistas.

Extensão: Entre 700 palavras no mínimo e 900 palavras no máximo. Desenvolva os parágrafos com profundidade.

Originalidade: O texto deve ser inédito, processando as informações e reescrevendo-as com uma narrativa própria (sem plágio).

Isenção: Proibido emitir opinião pessoal ou usar primeira pessoa. Se houver controvérsias, apresente os dois lados de forma equilibrada.

Estrutura do Texto:

Título: Chamativo, porém informativo e sóbrio.

Lide (Lead): O primeiro parágrafo deve responder: Quem? O quê? Onde? Quando? Por quê? e Como?

Subtítulos: Utilize pelo menos dois subtítulos para organizar a progressão temática do texto.

Corpo: Desenvolva os fatos de forma cronológica ou por relevância de impacto.

Conclusão Analítica: Encerre com uma análise técnica sobre as implicações futuras ou o desdobramento esperado dos fatos, sem cair no opinativo subjetivo.

Importante:
- Não escreva explicações externas.
- Não inclua observações adicionais.
- Entregue apenas o texto final já estruturado.
"""


        response = self.client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()
