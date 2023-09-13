*** Settings ***
Library    SeleniumLibrary

*** Variables ***
${URL}    https://chat.openai.com/c/9292677b-a62c-44b1-b19b-a43d26517ecb     # Substitua pela URL do site da OpenAI
${texto_a_melhorar}    // melhore a frase utilizando o CHA para busca de profissionais  # Texto a ser inserido no campo de descrição

*** Test Cases ***
Automacao_Site_OpenAI
    Open Browser    ${URL}    chrome
    Maximize Browser Window
    Sleep   100s
    Input Text    id=descricao    ${texto_a_melhorar}  # Insira o texto no campo de descrição
    Click Element    id=submit-button  # Substitua pelo seletor do botão "Enviar" no site da OpenAI
    ${descricao_melhorada} =    Get Text    id=descricao  # Obtém a descrição melhorada da página
    Log    Descrição Melhorada: ${descricao_melhorada}
    Close Browser
