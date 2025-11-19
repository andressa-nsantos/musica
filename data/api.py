import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager # nova linha
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re
from pathlib import Path
from tqdm import tqdm  # Adicionando a importação do tqdm
import random  # Para gerar pausas aleatórias

options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.implicitly_wait(0)
# Configurar o diretório de saída
output_dir = Path("processed")
output_dir.mkdir(parents=True, exist_ok=True)

# Função para buscar a letra, a cifra, o tom e o compositor no cifra_club.br
def buscar_letra_e_detalhes(musica, artista, id_musica):
    try:
        # Acessar o site cifraclub.com.br
        driver.get("https://www.cifraclub.com.br")
        print("Carregou, tentando achar input...")
        start = time.time()
        search_box = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input.header-searchInput.js-modal-trigger")))
        print("Achou em:", time.time() - start, "segundos") # métrica de tempo para encontrar a caixa de input

        try:
            close_popup = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".cc-btn.cc-dismiss, .modal-close, .sib-close-btn")))
            close_popup.click()
        except:
            pass
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.header-searchInput.js-modal-trigger")))

        # Buscar somente o nome da música na barra de pesquisa
        search_box = driver.find_element(By.CSS_SELECTOR, "input.header-searchInput.js-modal-trigger")
        search_box.clear()
        search_box.send_keys(musica, artista)
        time.sleep(random.uniform(2, 4))  # Pausa aleatória entre 2 a 4 segundos para esperar as sugestões
        
        # Clicar na primeira sugestão
        first_suggestion = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal.suggest.header-suggest .list-suggest a"))
        )
        first_suggestion.click()
    except Exception as e:
        print("Erro durante a busca:", e)

    #   FIZEMOS ATE AQUI!!!!!

    # Aguardar o carregamento completo da página
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.cifra_cnt")))


    # Capturar a letra e a cifra
    letra_e_cifra_elements = driver.find_elements(By.CSS_SELECTOR, "div.cifra_cnt pre")
    letra = "\n".join([element.text for element in letra_e_cifra_elements])
    print(letra)

#teste
buscar_letra_e_detalhes('Notícia boa', ' Fernando e Sorocaba', 5978)
buscar_letra_e_detalhes('Construção', ' Chico Buarque', 50)
buscar_letra_e_detalhes('Cardigan', ' Taylor Swift', 50)
        

     
# Capturar o tom da música
# tom_elements = driver.find_elements(By.CSS_SELECTOR, "div.cifra_cnt a")

        # # Capturar o nome da música e do artista
        # nome_musica = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "h1.textStyle-primary"))
        # ).text
        
        # nome_artista = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.CSS_SELECTOR, "h2.textStyle-secondary"))
        # ).text
        
        # Adicionar o código da música ao dicionário
#         return {
#             'ID': id_musica,
#             'Nome': nome_musica,
#             'Artista': nome_artista,
#             'Letra': letra
#         }
#     except Exception as e:
#         print(f"Erro ao processar {musica}: {e}")
#         return None

# # Carregar o data.frame com músicas
# df = pd.read_csv("musicas_completas.csv")  # Atualize o caminho do CSV

# # Variável para contar requisições feitas
# requisicoes_realizadas = 0

# # Gerar número inicial de músicas até a pausa
# musicas_ate_pausa = random.randint(44, 45)

# # Configuração para salvar os dados
# for index, row in tqdm(df.iterrows(), total=len(df), desc="Processando letras"):
#     musica = row['Nome.x']
#     artista = row['Artista.x']
#     ano = row['Ano']
#     id_musica = 1

#     # Sanitizar o nome da música para garantir que não contenha caracteres inválidos
#     musica_sanitizada = musica.replace(' ', '_')

#     # Nome do arquivo JSON para salvar os resultados
#     file_path = output_dir / f"{id_musica}_{musica_sanitizada}.json"

#     # Verificar se o arquivo já existe
#     if not file_path.exists():
#         tqdm.write(f"Buscando letra: {musica} (Ano: {ano}, ID: {id_musica})")
#         dados = buscar_letra_e_detalhes(musica, id_musica)
#         requisicoes_realizadas += 1        
#         # Se a letra for encontrada, salvar no arquivo JSON
#         if dados:
#             file_path.write_text(json.dumps(dados, ensure_ascii=False, indent=4), encoding='utf-8')
        
    

#         # Pausa aleatória após atingir o número de músicas processadas
#         if requisicoes_realizadas > 0 and requisicoes_realizadas % musicas_ate_pausa == 0:
#             tempo_pausa = 0
#             tqdm.write(f"Pausando por {int(tempo_pausa)} segundos... ({musicas_ate_pausa} músicas processadas)")
#             time.sleep(tempo_pausa)  # Realizar a pausa

#             # Redefinir o número de músicas até a próxima pausa
#             musicas_ate_pausa = random.randint(35, 40)
#             print(musicas_ate_pausa)

# # Encerrar o WebDriver
# driver.quit()