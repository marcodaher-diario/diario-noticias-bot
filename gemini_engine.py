import os
from google import genai
from google.genai import types


class GeminiEngine:

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

        self.client = genai.Client(api_key=self.api_key)

        # Modelo confirmado disponível na sua conta
        self.model = "models/gemini-2.5-flash"


    def gerar_analise_jornalistica(self, titulo, conteudo_original, categoria):

        prompt = f"""
Você é um jornalista profissional, analista político experiente e redator especializado em blogs de notícias.

Escreva uma análise jornalística com no mínimo 500 palavras.

Regras obrigatórias:

Não use Markdown.
Não use símbolos como #, ##, ###.
Não use asteriscos.
Não use listas.
Não use marcadores.
Não use negrito.
Não use itálico.
Não use qualquer tipo de formatação especial.

O texto deve ser completamente limpo, apenas parágrafos normais.

A estrutura obrigatória deve conter exatamente estes subtítulos, escritos apenas como texto simples, sem símbolos:

Contexto

Desdobramentos

Impactos

Considerações Finais

Os subtítulos devem aparecer isolados em linha própr
