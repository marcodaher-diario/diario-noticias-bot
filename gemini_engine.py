import os
from google import genai
from google.genai import types


class GeminiEngine:

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

        self.client = genai.Client(api_key=self.api_key)

        # Modelo 100% compatível com API pública
        self.model = "gemini-1.5-flash"


    def gerar_analise_jornalistica(self, titulo, conteudo_original, categoria):

        prompt = f"""
Você é um jornalista profissional, imparcial e analista político experiente.

Com base na notícia abaixo, escreva uma análise jornalística estruturada.

Regras obrigatórias:

Texto mínimo 500 palavras
Linguagem clara
Sem sensacionalismo
Sem opinião pessoal
Sem marcadores especiais como # ou *
Sem plágio
SEO natural
Texto profissional

Estrutura obrigatória:

Contexto

Desdobramentos

Impactos

Considerações Finais

Categoria: {categoria}

Título da notícia:
{titulo}

Conteúdo da notícia:
{conteudo_original}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=2048
            )
        )

        if not response or not response.text:
            raise ValueError("Resposta vazia do Gemini.")

        return response.text.strip()
