import os
from google import genai


class ListModels:

    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY não encontrada nas variáveis de ambiente.")

        self.client = genai.Client(api_key=self.api_key)

    def listar(self):
        print("\n======================================")
        print("MODELOS DISPONÍVEIS PARA SUA CHAVE")
        print("======================================\n")

        try:
            models = self.client.models.list()

            encontrou = False

            for model in models:
                encontrou = True
                print(model.name)

            if not encontrou:
                print("Nenhum modelo retornado pela API.")

        except Exception as e:
            print("ERRO AO LISTAR MODELOS:")
            print(str(e))


def main():
    executor = ListModels()
    executor.listar()


if __name__ == "__main__":
    main()
