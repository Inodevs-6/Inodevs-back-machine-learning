## APLICAÇÃO DO ALGORITMO BAG OF WORDS + RANQUEAMENTO UTILIZANDO PALAVRAS CHAVE ##
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

# Seus dados fictícios
data = pd.read_csv("csv/scrap.csv", sep=",")

# Criar um DataFrame a partir dos dados fictícios
df = pd.DataFrame(data)

# Conhecimentos, Habilidades e Atitudes
conhecimentos = ["python", "graduação", "estruturas de dados", "desenvolvimento ágil", "bancos de dados"]
habilidades = ["design escalável", "depuração", "integração de APIs", "testes de unidade", "comunicação", "liderança"]
atitudes = ["comprometimento", "aprendizado contínuo", "adaptabilidade", "trabalho em equipe", "ética"]
cha = conhecimentos + habilidades + atitudes

# Inicializar o vetorizador Bag of Words
vectorizer = CountVectorizer()

# Inicializar as colunas de pontuação
df["Pontuacao_Conhecimentos"] = 0
df["Pontuacao_Habilidades"] = 0
df["Pontuacao_Atitudes"] = 0

# Percorrer cada palavra-chave de conhecimento, habilidade e atitude
for palavra_chave in conhecimentos + habilidades + atitudes:
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

# Classificar os candidatos por pontuação total em ordem decrescente
# df_classificado = df.sort_values(by="Classificacao", ascending=False)

# # Salvar o resultado em um arquivo CSV com todas as informações
# df_classificado.to_csv("csv/results/1_curriculos_classificados_com_critérios.csv", index=False)

# Criar um DataFrame com a quantidade total de conhecimento, habilidade e atitude de cada pessoa
df_total = df[["Nome", "Pontuacao_Conhecimentos", "Pontuacao_Habilidades", "Pontuacao_Atitudes", "Classificacao"]].sort_values(by="Classificacao", ascending=False)

# Salvar o resultado em um arquivo CSV separado
df_total.to_csv("csv/results/2_quantidade_total_conhecimento_habilidade_atitude.csv", index=False)