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
        if not (Vaga.objects.filter(vaga_nome=cargo) and Vaga.objects.filter(vaga_nivel=nivel)):
            nova_descricao = Vaga()
            nova_descricao.vaga_nome = cargo
            nova_descricao.vaga_nivel = nivel

            response = openai.ChatCompletion.create(
                        engine="modelgpt35t",
                        messages=[
                            {"role": "system", "content": f'De acordo com a descrição CHA (Compentecias, Habilidades e Atitudes) da área de RH, crie uma descrição para o cargo {cargo} com o nivel {nivel}, separados em tópicos e em palavras chave sem complementar essas palavras chave de maneira resumida e objetiva, e em formato json.'+
                                '''
                                Siga exatamente o seguinte formato:
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
            nova_descricao.vaga_conhecimentos = descricao_cha['descricao'][chaves[0]]
            nova_descricao.vaga_habilidades = descricao_cha['descricao'][chaves[1]]
            nova_descricao.vaga_atitudes = descricao_cha['descricao'][chaves[2]]
            nova_descricao.save()

            descricao = {'descricao':descricao_cha}
            return HttpResponse(json.dumps(descricao['descricao']), content_type="application/json")

            # return HttpResponse('Dados salvos com sucesso e descrição CHA gerada.')
        else:
            return HttpResponse('Erro! A descrição a ser gerada já existe, modifique-a como desejar ou insira um novo cargo/nivel.')

    return HttpResponse('Erro! O campo cargo ou nivel não foram corretamente preenchidos.')

@csrf_exempt
def scrap(request):
    url = "https://scrap-example.onrender.com/scraping.html"  # Substitua pelo URL da página que você deseja acessar
    response = requests.get(url)

    # Dataframe com as colunas pré-setadas para criação do arquivo csv
    df = {'Link_Candidato':[], 'Experiencia':[]}

    # Se o request for um sucesso ele entrará dentro do if para o tratamento do html
    if response.status_code == 200:
        # Gerando um objeto a partir do html pego pelo request e transformando um objeto do body inteiro em um objeto com a lista de tags td (Linhas da tabela no web)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup.prettify()
        soup = soup.body.find_all('td')
        
        id_cand = 0

        # Adicionando as linhas de informações dos candidatos no dataframe declarado no começo e retirando as tags dos elementos
        while soup:
            df['Link_Candidato'].append(url+str(id_cand))
            df['Experiencia'].append(soup[-2].string.replace('<td>', '').replace('/', ''))
            soup = soup[:-4]

            id_cand+=1
            
        
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
    nivel = json.loads(request.body.decode('utf-8')).get('nivel')

    if Vaga.objects.filter(vaga_nome=vaga, vaga_nivel=nivel):
        # descricao_chas = Vaga.objects.filter(cargo=request.POST.get('cargo'))
        descricao_chas = Vaga.objects.filter(vaga_nome=vaga, vaga_nivel=nivel)

        # Itere sobre os objetos recuperados
        for descricao_cha in descricao_chas:
            # Acesse as colunas individualmente
            cargo = descricao_cha.vaga_nome
            nivel = descricao_cha.vaga_nivel
            
            # Conhecimentos, Habilidades e Atitudes
            conhecimentos = descricao_cha.vaga_conhecimentos
            habilidades = descricao_cha.vaga_habilidades
            atitudes = descricao_cha.vaga_atitudes
            cha = (conhecimentos + habilidades + atitudes).replace('[', '').replace(']', '').replace("'", '').split(',')

            print(f"Cargo: {cargo}, Nível: {nivel}")
            print(f"Descrição CHA separado por topico: {cha}")

        vectorizer = CountVectorizer()

        # Inicializar as colunas de pontuação
        df["Pontuacao_Conhecimentos"] = 0
        df["Pontuacao_Habilidades"] = 0
        df["Pontuacao_Atitudes"] = 0

        # Concatenar conhecimentos, habilidades e atitudes em uma string
        cha_texto = ' '.join(cha)

        # Usar CountVectorizer para contar as ocorrências de palavras-chave nas experiências dos candidatos
        matriz_contagens = vectorizer.fit_transform(df["Experiencia"] + ' ' + cha_texto)

        # Obter o vocabulário (palavras únicas)
        vocabulario = vectorizer.get_feature_names_out()

        print(vocabulario)

        # Atualizar as colunas de pontuação correspondentes
        df[["Pontuacao_Conhecimentos", "Pontuacao_Habilidades", "Pontuacao_Atitudes"]] = matriz_contagens.toarray()[:, :3]

        # Calcular a pontuação total para cada candidato
        df["Pontuacao_Final"] = df["Pontuacao_Conhecimentos"] + df["Pontuacao_Habilidades"] + df["Pontuacao_Atitudes"]

        # Confere se existe o seguinte caminho, se não, ele cria
        if not os.path.exists('csv/results'):
            os.makedirs('csv/results')

        # Calcular a porcentagem com base na coluna "Pontuacao_Final"
        df["Porcentagem"] = round((df["Pontuacao_Final"] / len(cha)) * 100, 2)

        # Criar um DataFrame com a quantidade total de conhecimento, habilidade e atitude de cada pessoa
        df_total = df[["Link_Candidato", "Experiencia","Pontuacao_Conhecimentos", "Pontuacao_Habilidades", "Pontuacao_Atitudes", "Pontuacao_Final", "Porcentagem"]].sort_values(by="Pontuacao_Final", ascending=False)
        df_total = df_total.head(8)
        
        # Salvar o resultado em um arquivo CSV separado
        df_total.to_csv("./csv/results/ranqueamento_por_cha_porcentagem.csv", index=False)
        
        x=0
        for index, row in df_total.iterrows():
            x+=1
            if not (Candidato.objects.filter(cand_link=row['Link_Candidato'])):

                new_candidato = Candidato()
                new_candidato.cand_link = row['Link_Candidato']
                new_candidato.cand_exp = row['Experiencia']
                new_candidato.save()


                # Recupere o candidato correspondente com base no Link_Candidato
                desc = Vaga.objects.get(vaga_nome=vaga, vaga_nivel=nivel)
                candidato = Candidato.objects.get(cand_link=row['Link_Candidato'])

                # Crie uma instância da tabela intermediária e associe o candidato e a descrição de cargo
                CandidatoVaga.objects.create(vaga=desc, cand=candidato, cand_vaga_rank=x, cand_vaga_pontos_cha=row['Pontuacao_Final'], cand_percent_match=row['Porcentagem'])
                
                print(f"O candidato {row['Link_Candidato']} foi cadastrado com sucesso")

            elif Candidato.objects.get(cand_link=row['Link_Candidato']):

                # Recupere a descrição correspondente com base no cargo e nível
                desc = Vaga.objects.get(vaga_nome=vaga, vaga_nivel=nivel)
                
                # Recupere o candidato correspondente com base no Link_Candidato
                candidato = Candidato.objects.get(cand_link=row['Link_Candidato'])

                # Crie uma instância da tabela intermediária e associe o candidato e a descrição de cargo
                CandidatoVaga.objects.create(vaga=desc, cand=candidato, cand_vaga_rank=x, cand_vaga_pontos_cha=row['Pontuacao_Final'], cand_percent_match=row['Porcentagem'])
                
                print(f"A atualização do candidato {row['Link_Candidato']} foi concluido!")

            else:
                print(f"O cadastramento do candidato {row['Link_Candito']} não foi concluido, pois possivelmente houveram dados duplicados.")        

        return HttpResponse('O arquivo com a classificação foi gerado com sucesso.')
    
    return HttpResponse('Não foi possível encontrar o cargo requerido.')