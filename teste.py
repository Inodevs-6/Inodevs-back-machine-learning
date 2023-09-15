import openai

openai.api_type = "azure"
openai.api_base = "https://interactai.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "66a6b8c8d3c449d4b53fa75d09b04366"

#user_competence = input("Competencia: ")
user_ability = input("Habilidade: ")
#user_attitudes = input("Atitude: ")

#response_competence = openai.ChatCompletion.create(
 #   engine="modelgpt35t",
  #  messages=[
   #     {"role": "system", "content": "Melhore com base na competencia do CHA a competencia a seguir para uma descriação melhor da competencia que queremos no profissional (resposta curta): "+user_competence},
    #]
#)

response_ability = openai.ChatCompletion.create(
    engine="modelgpt35t",
    messages=[
        {"role": "system", "content": "Melhore o topico - habilidade - do CHA - com a descriação a seguir para uma melhor habilidade do que queremos para nosso profissional (resposta curta): "+user_ability},
    ]
)



#print(response)
#print(response_competence['choices'][0]['message']['content'])
print(response_ability['choices'][0]['message']['content'])
