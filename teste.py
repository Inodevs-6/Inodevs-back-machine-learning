import openai

openai.api_type = "azure"
openai.api_base = "https://interactai.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = ""

user_competence = input("Competencia: ")
user_ability = input("Habilidade: ")
user_attitudes = input("Atitude: ")

response = openai.ChatCompletion.create(
    engine="modelgpt35t",
    messages=[
        {"role": "system", "content": "Melhore com base no CHA (Conhecimentos, Habilidades e Atitudes) e de uma forma curta os 3 tópicos a seguir também separado em Competencias, Habilidades e Atitudes, volte com isso por tópico para buscar por um profissional com uma descrição melhor: "+user_competence+user_ability+user_attitudes},
    ]
)

#print(response)
print(response['choices'][0]['message']['content'])
