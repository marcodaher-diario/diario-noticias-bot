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

        # Estratégia de Fallback solicitada: 3 Modelos em 3 Ciclos
        self.modelos_fallback = [
            "gemini-3-flash-preview",
            "gemini-2.5-pro",
            "gemini-2.5-flash"
        ]

    def _limpar_e_formatar_markdown(self, texto):
        """
        Converte Markdown (Negrito, Itálico, Listas) para HTML 
        e remove marcadores de títulos excedentes.
        """
        if not texto:        
            return ""

            # 1. NEGRITO: Transforma **texto** em <strong>texto</strong>
            texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
        
            # 2. ITÁLICO: Transforma *texto* ou _texto_ em <em>texto</em>
            # Nota: Fazemos isso DEPOIS do negrito para não conflitar
            texto = re.sub(r'\*(.*?)\*', r'<em>\1</em>', texto)
            texto = re.sub(r'_(.*?)_', r'<em>\1</em>', texto)
        
            # 3. LISTAS: Transforma linhas que começam com "*" ou "-" em <li>
            # O sinal ^ no regex com flags=re.MULTILINE pega o início de cada linha
            texto = re.sub(r'^\s*[\*\-]\s+(.*)', r'<li>\1</li>', texto, flags=re.MULTILINE)
        
            # 4. TÍTULOS: Remove os marcadores #, ##, etc. 
            # (Mantendo o texto, apenas limpando os símbolos)
            texto = re.sub(r'#+\s?', '', texto)
        
            # 5. LIMPEZA FINAL: Remove asteriscos ou underscores que sobraram 
            # e que não foram capturados pelas regras anteriores
            texto = texto.replace('*', '').replace('_', '')
        
            return texto.strip()

    def gerar_analise_jornalistica(self, titulo, resumo, categoria):

        prompt = f"""
Atue como um Jornalista Sênior com 20 anos de experiência em hard news e reportagem investigativa.

Seu objetivo: Redigir um artigo jornalístico de fôlego baseado nas informações que fornecerei abaixo. O texto deve seguir rigorosamente os padrões de qualidade de veículos como The New York Times ou BBC.

Informações base:

Título da notícia: {titulo}

Resumo da notícia: {resumo}

Categoria: {categoria}

Diretrizes Obrigatórias:

Tom e Estilo: Imparcial, técnico e analítico. Use linguagem clara, objetiva e evite adjetivos desnecessários ou termos sensacionalistas.

Extensão: Entre 600 palavras no mínimo e 750 palavras no máximo. Desenvolva os parágrafos com profundidade.

Originalidade: O texto deve ser inédito, processando as informações e reescrevendo-as com uma narrativa própria (sem plágio).

Isenção: Proibido emitir opinião pessoal ou usar primeira pessoa. Se houver controvérsias, apresente os dois lados de forma equilibrada.

Estrutura do Texto:

Título: Chamativo, porém informativo e sóbrio.

Lide (Lead): O primeiro parágrafo deve responder: Quem? O quê? Onde? Quando? Por quê? e Como?

Subtítulos: Utilize pelo menos dois subtítulos para organizar a progressão temática do texto.

Corpo: Desenvolva os fatos de forma cronológica ou por relevância de impacto.

Conclusão: Encerre o texto com uma análise técnica sobre as implicações futuras e as consequèncias esperadas dos fatos, sem cair no opinativo subjetivo.

Importante:
- Não escreva explicações externas.
- Não inclua observações adicionais.
- Entregue apenas o texto final já estruturado.
"""

        return self._executar_com_resiliencia(prompt)


    def _executar_com_resiliencia(self, prompt):
        """
        Lógica de 9 tentativas (3 ciclos x 3 modelos) 
        sem alterar os prompts originais.
        """
        tentativa_total = 1
        for ciclo in range(1, 4):  # 3 passagens completas
            for modelo in self.modelos_fallback:
                try:
                    print(f"Tentativa {tentativa_total}/9 | Ciclo {ciclo} | Usando: {modelo}")
                    
                    response = self.client.models.generate_content(
                        model=modelo,
                        contents=prompt
                    )

                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                
                except Exception as e:
                    erro_msg = str(e).upper()
                    # Identifica se o erro é de "Lotado" (503), "Timeout" ou "Cota"
                    if any(x in erro_msg for x in ["503", "UNAVAILABLE", "DEADLINE", "429", "QUOTA"]):
                        print(f"⚠️ Modelo {modelo} indisponível ou lotado. Pulando para o próximo...")
                        time.sleep(5) # Pausa curta antes da próxima tentativa
                    else:
                        print(f"❌ Erro crítico no modelo {modelo}: {e}")
                
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
