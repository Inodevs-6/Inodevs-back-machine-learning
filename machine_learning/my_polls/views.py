from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import openai
from .models import *
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import os
from dotenv import load_dotenv
load_dotenv()


# Função para recebimento de cargo e nivel para a geração da descrição CHA, salvando-o no banco de dados
@csrf_exempt
def chatgpt(request):
    openai.api_type = "azure"
    openai.api_base = "https://interactai.openai.azure.com/"
    openai.api_version = "2023-05-15"
    openai.api_key = os.environ['API_KEY']

    if request.method == 'POST':
        cargo = json.loads(request.body.decode('utf-8')).get('cargo')
        nivel = json.loads(request.body.decode('utf-8')).get('nivel')

        print(cargo, nivel)
        if not (DescCargo.objects.filter(desc_vaga=cargo) and DescCargo.objects.filter(desc_nivel=nivel)):
            nova_descricao = DescCargo()
            nova_descricao.desc_vaga = cargo
            nova_descricao.desc_nivel = nivel

            response = openai.ChatCompletion.create(
                        engine="modelgpt35t",
                        messages=[
                            {"role": "system", "content": f'De acordo com a descrição CHA (Compentecias, Habilidades e Atitudes) da área de RH, crie uma descrição para o cargo {cargo} com o nivel {nivel}, separados em tópicos e em palavras chave sem complementar essas palavras chave de maneira resumida e objetiva, e em formato json.'+
                                '''
                                Siga o seguinte formato:
                                {
                                    "Título do Cargo": "Cargo e seu nivel requerido",
                                    "descricao":[
                                        "Conhecimentos": [
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave)"
                                        ],
                                        "Habilidades": [
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave"
                                        ],
                                        "Atitudes": [
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave",
                                            "Palavra chave"
                                        ]
                                    ]
                                }'''
                                },
                        ]
                    )
            descricao_cha = json.loads(response['choices'][0]['message']['content'])

            chaves = [i for i in descricao_cha['descricao']]

            print('Print das chaves' , descricao_cha)

            # Conhecimentos, Habilidades e Atitudes
            nova_descricao.desc_conhecimentos = descricao_cha['descricao'][chaves[0]]
            nova_descricao.desc_habilidades = descricao_cha['descricao'][chaves[1]]
            nova_descricao.desc_atitudes = descricao_cha['descricao'][chaves[2]]
            nova_descricao.save()

            return HttpResponse('Dados salvos com sucesso e descrição CHA gerada.')
        else:
            return HttpResponse('Erro! A descrição a ser gerada já existe, modifique-a como desejar ou insira um novo cargo/nivel.')

    return HttpResponse('Erro! O campo cargo ou nivel não foram corretamente preenchidos.')

@csrf_exempt
def scrap(request):
    url = "https://scrap-example.onrender.com/scraping.html"  # Substitua pelo URL da página que você deseja acessar
    response = requests.get(url)

    # Dataframe com as colunas pré-setadas para criação do arquivo csv
    df = {'Nome':[], 'Idade':[], 'Experiencia':[], 'Email':[]}

    # Se o request for um sucesso ele entrará dentro do if para o tratamento do html
    if response.status_code == 200:
        # Gerando um objeto a partir do html pego pelo request e transformando um objeto do body inteiro em um objeto com a lista de tags td (Linhas da tabela no web)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup.prettify()
        soup = soup.body.find_all('td')
        

        # Adicionando as linhas de informações dos candidatos no dataframe declarado no começo e retirando as tags dos elementos
        while soup:
            df['Nome'].append(soup[-4].string.replace('<td>', '').replace('/', ''))
            df['Idade'].append(soup[-3].string.replace('<td>', '').replace('/', ''))
            df['Experiencia'].append(soup[-2].string.replace('<td>', '').replace('/', ''))
            df['Email'].append(soup[-1].string.replace('<td>', '').replace('/', ''))
            soup = soup[:-4]
            
        
        # Transformando o dicionario 'df' criado com as informações em um dataframe utilizando o pandas seguido da geração do arquivo csv
        if not os.path.exists('csv'):
            os.makedirs('csv')

        csv_path = os.path.join('csv', 'scrap.csv')
        df = pd.DataFrame(df)
        df.to_csv(csv_path, index=False)

    # Caso o request retorne um erro ao capturar o html da página, o else a seguir retorna uma mensagem com o erro gerado
    else:
        HttpResponse(f"Erro ao fazer o request. Código de status: {response.status_code}")

    return HttpResponse('Raspagem feita e salva com sucesso em um arquivo csv.')

@csrf_exempt
def match(request):
    # Seus dados fictícios
    data = pd.read_csv("./csv/scrap.csv", sep=",")

    # Criar um DataFrame a partir dos dados fictícios
    df = pd.DataFrame(data)

    vaga = json.loads(request.body.decode('utf-8')).get('cargo')

    if DescCargo.objects.filter(desc_vaga=vaga):
        # descricao_chas = DescCargo.objects.filter(cargo=request.POST.get('cargo'))
        descricao_chas = DescCargo.objects.filter(desc_vaga=vaga)

        # Itere sobre os objetos recuperados
        for descricao_cha in descricao_chas:
            # Acesse as colunas individualmente
            cargo = descricao_cha.desc_vaga
            nivel = descricao_cha.desc_nivel
            
            # Conhecimentos, Habilidades e Atitudes
            conhecimentos = descricao_cha.desc_conhecimentos
            habilidades = descricao_cha.desc_habilidades
            atitudes = descricao_cha.desc_atitudes
            cha = (conhecimentos + habilidades + atitudes).replace('[', '').replace(']', ',').replace("'", '').split(',')

            print(f"Cargo: {cargo}, Nível: {nivel}")
            print(f"Descrição CHA separado por topico: {cha}")

        vectorizer = CountVectorizer()

        # Inicializar as colunas de pontuação
        df["Pontuacao_Conhecimentos"] = 0
        df["Pontuacao_Habilidades"] = 0
        df["Pontuacao_Atitudes"] = 0

        # Percorrer cada palavra-chave de conhecimento, habilidade e atitude
        for palavra_chave in cha:
            # Verificar se a palavra-chave está presente nas experiências dos candidatos
            df[palavra_chave] = df["Experiencia"].str.contains(palavra_chave, case=False, regex=True).astype(int)
            
            # Atualizar a pontuação correspondente para cada candidato
            if palavra_chave in conhecimentos:
                df["Pontuacao_Conhecimentos"] += df[palavra_chave]
            elif palavra_chave in habilidades:
                df["Pontuacao_Habilidades"] += df[palavra_chave]
            elif palavra_chave in atitudes:
                df["Pontuacao_Atitudes"] += df[palavra_chave]

        # Calcular a pontuação total para cada candidato
        df["Classificacao"] = df["Pontuacao_Conhecimentos"] + df["Pontuacao_Habilidades"] + df["Pontuacao_Atitudes"]

        # Confere se existe o seguinte caminho, se não, ele cria
        if not os.path.exists('csv/results'):
            os.makedirs('csv/results')

        # Classificar os candidatos por pontuação total em ordem decrescente
        df_classificado = df.sort_values(by="Classificacao", ascending=False)
        df_classificado = df_classificado.head(8)

        # Salvar o resultado em um arquivo CSV com todas as informações
        df_classificado.to_csv("csv/results/curriculos_classificados_com_critérios.csv", index=False)

        # Criar um DataFrame com a quantidade total de conhecimento, habilidade e atitude de cada pessoa
        df_total = df[["Nome", "Experiencia", "Email" ,"Pontuacao_Conhecimentos", "Pontuacao_Habilidades", "Pontuacao_Atitudes", "Classificacao"]].sort_values(by="Classificacao", ascending=False)
        df_total = df_total.head(8)

        for index, row in df_total.iterrows():
            if not (Candidato.objects.filter(cand_contato=row['Email']) and Candidato.objects.filter(cand_cargo=vaga)):

                new_candidato = Candidato()
                new_candidato.cand_nome = row['Nome']
                new_candidato.cand_experiencia = row['Experiencia']
                new_candidato.cand_contato = row['Email']
                new_candidato.cand_pontos_cha = row['Classificacao']
                new_candidato.cand_cargo = vaga
                new_candidato.cand_nivel = nivel
                new_candidato.save()

                new_cand_desc = DescCargoCandidato()
                new_cand_desc.cand = (Candidato.objects.get(cand_contato=row['Email'])).cand_id
                print((Candidato.objects.get(cand_contato=row['Email'])).cand_id)
                new_cand_desc.desc = (DescCargo.objects.get(desc_vaga=cargo)).desc_id
                new_cand_desc.save()

                # print(f"O candidato {row['Nome']} foi cadastrado com sucesso")

            else:
                print(f"O cadastramento do candidato {row['Nome']} não foi concluido, pois possivelmente houveram dados duplicados.")


        # Salvar o resultado em um arquivo CSV separado
        df_total.to_csv("./csv/results/ranqueamento_por_cha.csv", index=False)
        

        return HttpResponse('O arquivo com a classificação foi gerado com sucesso.')
    
    return HttpResponse('Não foi possível encontrar o cargo requerido.')