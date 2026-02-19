# -*- coding: utf-8 -*-

import os
from google import genai


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def gerar_analise_jornalistica(self, titulo, resumo, categoria):

        prompt = f"""
Você é um jornalista profissional escrevendo para um portal de notícias brasileiro.

Escreva uma análise jornalística baseada na notícia abaixo.

REGRAS OBRIGATÓRIAS:

- Texto mínimo de 500 palavras.
- Linguagem clara, objetiva e imparcial.
- Não usar marcadores como # ou *.
- Não usar listas numeradas.
- Não usar as palavras "Contexto", "Desdobramentos" ou "Impactos" como subtítulos.
- Criar exatamente DOIS subtítulos naturais e jornalísticos.
- Após os dois subtítulos, criar obrigatoriamente a seção:
Considerações Finais
- Cada subtítulo deve vir sozinho em uma linha.
- Após cada subtítulo, escrever os parágrafos relacionados.
- Separar blocos com linha em branco.
- Não repetir o título dentro do texto.
- Não usar frases genéricas de encerramento automático.
- Não escrever explicações técnicas.

TÍTULO DA NOTÍCIA:
{titulo}

RESUMO DA NOTÍCIA:
{resumo}

CATEGORIA:
{categoria}

Agora escreva o texto seguindo exatamente o formato solicitado.
"""

        response = self.client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()
