import requests
from bs4 import BeautifulSoup
import pandas as pd

# Função para fazer o scrap e gerar um csv com todos os cadidatos pegos da página
def main():
    url = "https://scrap-example.onrender.com/scraping.html"  # Substitua pelo URL da página que você deseja acessar
    response = requests.get(url)

    # Dataframe com as colunas pré-setadas para criação do arquivo csv
    df = {'nome':[], 'idade':[], 'experiencia':[], 'email':[]}

    # Se o request for um sucesso ele entrará dentro do if para o tratamento do html
    if response.status_code == 200:
        # Gerando um objeto a partir do html pego pelo request e transformando um objeto do body inteiro em um objeto com a lista de tags td (Linhas da tabela no web)
        soup = BeautifulSoup(response.text, 'html.parser')
        soup.prettify()
        soup = soup.body.find_all('td')
        

        # Adicionando as linhas de informações dos candidatos no dataframe declarado no começo e retirando as tags dos elementos
        while soup:
            df['nome'].append(soup[-4].string.replace('<td>', '').replace('/', ''))
            df['idade'].append(soup[-3].string.replace('<td>', '').replace('/', ''))
            df['experiencia'].append(soup[-2].string.replace('<td>', '').replace('/', ''))
            df['email'].append(soup[-1].string.replace('<td>', '').replace('/', ''))
            soup = soup[:-4]
            
        
        # Transformando o dicionario 'df' criado com as informações em um dataframe utilizando o pandas seguido da geração do arquivo csv
        df = pd.DataFrame(df)
        df.to_csv('./csv/scrap.csv', index=False)

    # Caso o request retorne um erro ao capturar o html da página, o else a seguir retorna uma mensagem com o erro gerado
    else:
        print(f"Erro ao fazer o request. Código de status: {response.status_code}")

if __name__ == "__main__":
    main()