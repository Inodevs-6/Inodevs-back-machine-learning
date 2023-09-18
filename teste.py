import openai

openai.api_type = "azure"
openai.api_base = "https://interactai.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "66a6b8c8d3c449d4b53fa75d09b04366"

user_competence = input("Competencia: ")
user_ability = input("Habilidade: ")
user_attitude = input("Atitude: ")

def get_description(topic, user_input):
    response = openai.ChatCompletion.create(
        engine="modelgpt35t",
        messages=[
            {"role": "system", "content": f"Melhore minha descrição da {topic} que procuro em um profissional com base no tópico - {topic} - do CHA (resposta curta) - Procuro um profissional... : {user_input}"},
        ]
    )
    return response['choices'][0]['message']['content']

competence_description = get_description("competencia", user_competence)
ability_description = get_description("habilidade", user_ability)
attitude_description = get_description("atitude", user_attitude)

print('---------')
print(competence_description)
print('---------')
print(ability_description)
print('---------')
print(attitude_description)
