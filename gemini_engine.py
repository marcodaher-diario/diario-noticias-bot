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

        prompt = (
            "Você é um jornalista profissional, analista político experiente e redator especializado em blogs de notícias.\n\n"
            "Escreva uma análise jornalística com no mínimo 500 palavras.\n\n"
            "Regras obrigatórias:\n"
            "Não use Markdown.\n"
            "Não use símbolos como #, ##, ###.\n"
            "Não use asteriscos.\n"
            "Não use listas.\n"
            "Não use marcadores.\n"
            "Não use negrito.\n"
            "Não use itálico.\n"
            "Não use qualquer tipo de formatação especial.\n\n"
            "O texto deve ser completamente limpo, apenas parágrafos normais.\n\n"
            "A estrutura obrigatória deve conter exatamente estes subtítulos, escritos apenas como texto simples, sem símbolos:\n\n"
            "Contexto\n\n"
            "Desdobramentos\n\n"
            "Impactos\n\n"
            "Considerações Finais\n\n"
            "Os subtítulos devem aparecer isolados em linha própria.\n"
            "Após cada subtítulo deve haver parágrafos explicativos.\n"
            "Linguagem clara.\n"
            "Tom imparcial.\n"
            "Sem sensacionalismo.\n"
            "Sem opinião pessoal.\n"
            "SEO natural.\n"
            "Sem plágio.\n\n"
            f"Categoria: {categoria}\n\n"
            f"Título da notícia:\n{titulo}\n\n"
            f"Conteúdo original da notícia:\n{conteudo_original}\n"
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.6,
                top_p=0.9,
                max_output_tokens=2048
            )
        )

        if not response or not response.text:
            raise ValueError("Resposta vazia do Gemini.")

        texto = response.text.strip()

        # Segurança extra contra Markdown
        texto = texto.replace("#", "")
        texto = texto.replace("*", "")

        return texto
