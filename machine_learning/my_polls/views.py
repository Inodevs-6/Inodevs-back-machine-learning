from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from django.http import HttpResponseServerError
import openai
from .models import *
import json
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
import os
from nltk.corpus import stopwords
import nltk
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
import re

load_dotenv()

nltk.download('stopwords')
nltk.download('punkt')

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
        if not (Vaga.objects.filter(vaga_nome=cargo,vaga_nivel=nivel)):
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
                                    "descricao":{
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
                                    }
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

            descricao_cha['id'] = nova_descricao.vaga_id

            print(descricao_cha)

            return HttpResponse(json.dumps(descricao_cha), content_type="application/json")

        else:
            vaga = get_object_or_404(Vaga, vaga_nome=cargo, vaga_nivel=nivel)
            
            # Usar regex para remover os caracteres indesejados
            regex = r"['\[\]]"
            conhecimentos = re.sub(regex, "", vaga.vaga_conhecimentos).split(",")
            habilidades = re.sub(regex, "", vaga.vaga_habilidades).split(",")
            atitudes = re.sub(regex, "", vaga.vaga_atitudes).split(",")

            descricao = {
                'Conhecimentos' : conhecimentos,
                'Habilidades' : habilidades,
                'Atitudes' : atitudes
            }
            data = {
                'cargo' : cargo,
                'nivel' : nivel,
                'descricao' : descricao,
                'id' : vaga.vaga_id
            }
            return HttpResponse(json.dumps(data), content_type="application/json")
    
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
            df['Experiencia'].append(soup[-2].string.replace('<td>', '').replace('/', '').lower())
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
            cha_list = (conhecimentos + ',' + habilidades + ',' + atitudes).replace('[', '').replace(']', '').replace("'", '').split(',')

            # Concatenar conhecimentos, habilidades e atitudes em uma string
            cha_texto = ' '.join(cha_list)
        
        # Baixar as stop words em português do NLTK
        stop_words_pt = list(set(stopwords.words('portuguese')))

        # Cria um vetorizador utilizando CountVectorizer e configurando para ignorar palavras comuns do português de acordo com o NLTK (de, da, os, as...)
        vectorizer = CountVectorizer(stop_words=stop_words_pt)

        # Inicializar as colunas de pontuação
        # df["Pontuacao_Conhecimentos"] = 0
        # df["Pontuacao_Habilidades"] = 0
        # df["Pontuacao_Atitudes"] = 0

        # Lista de palavras para exemplo do candidato perfeito
        vocabulario2 = 'adaptabilidade aprender arquitetura banco bootstrap clara comprometimento comunicação css3 dados desenvolvimento disposição entregas equipe estratégica foco gerenciamento html5 javascript jquery js mudanças novas objetiva prazos proatividade problemas programação projetos reactjs resolução resultados software tecnologias teste trabalho ui ux visão vue web'.split(' ')        

        # Usar CountVectorizer para contar as ocorrências de palavras-chave nas experiências dos candidatos, fit para treinar o vocabulario de acordo com as 
        # configurações na declaração do vectorizer, transform para aplicar o algoritmo treinado no df alvo
        # matriz_contagens = vectorizer.fit_transform(df["Experiencia"])

        # Matriz exemplo para vocabulario fixo para teste de porcentagem
        # matriz_contagens = vectorizer.fit(vocabulario2)
        
        matriz_contagens = vectorizer.fit(cha_list)
        matriz_contagens = vectorizer.transform(df["Experiencia"])

        # Obter o vocabulário (palavras únicas) resultante do treinamento
        vocabulario = vectorizer.get_feature_names_out()

        # Criar DataFrame da matriz para futuramente utilizar as colunas criadas de acordo com as palavras chave
        df_contagens = pd.DataFrame(matriz_contagens.toarray(), columns=vocabulario)

        # Atualizar as colunas de pontuação correspondentes
        # df[["Pontuacao_Conhecimentos", "Pontuacao_Habilidades", "Pontuacao_Atitudes"]] = df_contagens[vocabulario].toarray()

        # Calcular a pontuação total para cada candidato
        df["Pontuacao_Final"] = df_contagens.sum(axis=1)

        # Confere se existe o seguinte caminho, se não, ele cria
        if not os.path.exists('csv/results'):
            os.makedirs('csv/results')

        # Adicionar colunas para cada palavra-chave
        df = pd.concat([df, df_contagens], axis=1)

        # Calcular a porcentagem com base na coluna "Pontuacao_Final"
        df["Porcentagem"] = round((df["Pontuacao_Final"] / len(vocabulario)) * 100, 2)

        # Criar um DataFrame com a quantidade total de conhecimento, habilidade e atitude de cada pessoa
        # df_total = df[["Link_Candidato", "Experiencia","Pontuacao_Conhecimentos", "Pontuacao_Habilidades", "Pontuacao_Atitudes", "Pontuacao_Final", "Porcentagem"]].sort_values(by="Pontuacao_Final", ascending=False)

        df_total = df[["Link_Candidato", "Experiencia", "Pontuacao_Final", "Porcentagem"]].sort_values(by="Pontuacao_Final", ascending=False)
        df_total = df_total.head(8)

        df.to_csv("./csv/results/ranqueamento_por_chave.csv", index=False)
        
        # Salvar o resultado em um arquivo CSV separado
        df_total.to_csv("./csv/results/ranqueamento_porcentagem.csv", index=False)
        
        # Variavel utilizada para dar um numero ao rank no banco de dados
        x=0

        # For para iterar pelo df_total e, se for necessario salvar os candidatos novos e em seguida criar a relação de vaga -> candidato
        for index, row in df_total.iterrows():
            x+=1

            # Declara uma lista de candidatos que ja possuem uma relação com a vaga 
            cand_registered = CandidatoVaga.objects.raw(f"select * from candidato c left join candidato_vaga cv on c.cand_id = cv.cand_id where c.cand_link = '{row['Link_Candidato']}';")

            vaga_registered = CandidatoVaga.objects.raw(f"select c.cand_id,	cv.cand_id as relation,	cv.vaga_id as vaga_relation, v.vaga_id, v.vaga_nome from candidato c left join candidato_vaga cv on	c.cand_id = cv.cand_id left join vaga v on v.vaga_id = cv.vaga_id where	v.vaga_nome = '{vaga}';")

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

            try:            
                if Candidato.objects.get(cand_link=row['Link_Candidato']):
                    
                    # Recupere a descrição correspondente com base no cargo e nível
                    desc = Vaga.objects.get(vaga_nome=vaga, vaga_nivel=nivel)
                    
                    # Recupere o candidato correspondente com base no Link_Candidato
                    candidato = Candidato.objects.get(cand_link=row['Link_Candidato'])

                    # Crie uma instância da tabela intermediária e associe o candidato e a descrição de cargo
                    CandidatoVaga.objects.create(vaga=desc, cand=candidato, cand_vaga_rank=x, cand_vaga_pontos_cha=row['Pontuacao_Final'], cand_percent_match=row['Porcentagem'])
                    
                    print(f"A atualização do candidato {row['Link_Candidato']} foi concluido!")

            except:
                if row['Link_Candidato'] in [c.cand_link for c in cand_registered] and vaga in [v.vaga_nome for v in vaga_registered]:
                    print('Candidato ja possui relação com essa vaga, seus dados serão reutilizados para outra empresa.')
                    continue

        return HttpResponse('O arquivo com a classificação foi gerado com sucesso.')
    
    return HttpResponse('Não foi possível encontrar o cargo requerido.')
    
@csrf_exempt
def upgrade(request):

    openai.api_type = "azure"
    openai.api_base = "https://interactai.openai.azure.com/"
    openai.api_version = "2023-05-15"
    openai.api_key = os.environ['API_KEY']

    cargo = json.loads(request.body.decode('utf-8')).get('cargo')
    nivel = json.loads(request.body.decode('utf-8')).get('nivel')
    cha = json.loads(request.body.decode('utf-8')).get('cha')
    campo = json.loads(request.body.decode('utf-8')).get('campo')
    comentario = json.loads(request.body.decode('utf-8')).get('comentario')

    if not cargo or not cargo.strip() or not nivel or not nivel.strip():
        raise ValidationError("Preencha todos os campos!")

    mensagem = ''

    if comentario:
        mensagem += f'De acordo com o seguinte CHA (Conhecimentos, Habilidades e Atitudes), de um {cargo} com nível {nivel}: {cha}, sendo a seguinte instrução: "{comentario}", retorne 7 palavras-chaves objetivas de cada tópico de acordo com a instrução, seguindo o formato json anterior com os três tópicos, matendo mesmo sem modificar alguns campos (retorne apenas o json sem nenhum outro comentário).'
    else:
        if not campo or not cargo.strip():
            raise ValidationError("Preencha todos os campos!")

        mensagem += f'De acordo com as seguintes palavras-chaves do campo de {campo} de um {cargo} com nível {nivel}: {cha}, altere para outras palavras-chaves (não necessariamente precisam ser as mesmas), retornando em 7 palavras-chaves objetivas, seguindo o formato json citado anteriormente (retorne apenas o json com o resultado sem mais nenhum outro comentário).'

    tentativas = 0

    while True:
        try:
            response = openai.ChatCompletion.create(
                engine="modelgpt35t",
                messages=[
                    {"role": "system", "content": mensagem},
                ]
            )

            print(response['choices'][0]['message']['content'])

            data = json.loads(response['choices'][0]['message']['content'])

            if comentario: data['descricao']
            if campo == 'Conhecimentos': data['Conhecimentos']
            if campo == 'Habilidades': data['Habilidades']
            if campo == 'Atitudes': data['Atitudes']

            break
        except:
            print('erro')
            tentativas += 1

            if tentativas >= 10:
                 return HttpResponseServerError("Ops! Algo deu errado no servidor. Reinicie e tente novamente mais tarde.")


    return HttpResponse(json.dumps(data), content_type="application/json")
