def __init__(self):
    self.api_key = os.environ.get("GEMINI_API_KEY")

    if not self.api_key:
        raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

    self.client = genai.Client(api_key=self.api_key)

    self.model = "models/gemini-1.5-pro"


def gerar_analise_jornalistica(self, titulo, conteudo_original, categoria):

    prompt = f"""
