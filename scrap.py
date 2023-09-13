import requests
from bs4 import BeautifulSoup
import pandas as pd

def main():
    url = "https://scrap-example.onrender.com/scraping.html"  # Substitua pelo URL da página que você deseja acessar
    response = requests.get(url)
    df = {'nome':[], 'idade':[], 'experiencia':[], 'email':[]}

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        soup.prettify()
        soup = soup.body.find_all('td')
        
        # print(soup.find_all('td'))

        while soup:
            df['nome'].append(soup[-4].string.replace('<td>', '').replace('/', ''))
            df['idade'].append(soup[-3].string.replace('<td>', '').replace('/', ''))
            df['experiencia'].append(soup[-2].string.replace('<td>', '').replace('/', ''))
            df['email'].append(soup[-1].string.replace('<td>', '').replace('/', ''))
            soup = soup[:-4]
            
        # print(df)
        # print(soup[-4:])
        
        df = pd.DataFrame(df)
        df.to_csv('./csv/scrap.csv', index=False)

    else:
        print(f"Erro ao fazer o request. Código de status: {response.status_code}")

if __name__ == "__main__":
    main()