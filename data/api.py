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
from selenium.common.exceptions import NoSuchElementException # para identificar se há capotraste (para depois mudar o tom)

options = Options()
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Configurar o diretório de saída
output_dir = Path("processed")
output_dir.mkdir(parents=True, exist_ok=True)

# Função para buscar a letra, a cifra, o tom e o compositor no cifra_club.br
def buscar_letra_e_detalhes(musica, artista, id_musica):
    try:
        # Acessar o site cifraclub.com.br
        driver.get("https://www.cifraclub.com.br")
        search_box = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.header-searchInput.js-modal-trigger")))
        
        WebDriverWait(driver, 3).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.header-searchInput.js-modal-trigger")))

        # Buscar somente o nome da música na barra de pesquisa
        search_box = driver.find_element(By.CSS_SELECTOR, "input.header-searchInput.js-modal-trigger")
        search_box.clear()
        search_box.send_keys(musica, artista)
        time.sleep(random.uniform(2, 4))  # Pausa aleatória entre 2 a 4 segundos para esperar as sugestões
        
        # Clicar na primeira sugestão
        first_suggestion = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".modal.suggest.header-suggest .list-suggest a")))
        first_suggestion.click()

        # Aguardar o carregamento completo da página
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.cifra_cnt")))

        # Capturar a letra e a cifra
        letra_e_cifra_elements = driver.find_elements(By.CSS_SELECTOR, "div.cifra_cnt pre")
        letra_e_cifra = "\n".join([element.text for element in letra_e_cifra_elements])
        # Capturar o tom da música
        tom = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.cifra_cnt a"))).text
        # Capturar se usa capotraste
        try:
            elemento_capo = driver.find_element(By.CSS_SELECTOR, "#cifra_capo")
            capo_usado = True
            capo_texto = elemento_capo.text.strip()
        except NoSuchElementException:
            capo_usado = False
            capo_texto = None
        capotraste = f'{capo_usado} {capo_texto}'
        # Capturar o nome da música e do artista
        nome_musica = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.t1"))).text
        nome_artista = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.t3 a"))).text
        # Capturar o compositor
        compositor = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.cifra-footer p.cifra-composer"))).text
        compositor = compositor.split(".")[0]  # quero apenas o que aparece antes do primeiro ponto

        # Adicionar o código da música no dicionário
        return {
            'ID': id_musica,
            'Nome': nome_musica,
            'Artista': nome_artista,
            'Tom': tom,
            'Capotraste': capotraste,
            'Letra_cifra': letra_e_cifra,
            'Compositor': compositor,
            }
    except Exception as e:
        print(f"Erro ao processar {musica}: {e}")
        return None

# Carregar o dataframe.csv com músicas e tirar as últimas colunas
caminho = r"C:\Users\andre\OneDrive\Desktop\musica\musica\data\raw_data.csv"
df = pd.read_csv(caminho, sep=";", encoding="cp1252")
print(df.head())

# Variável para contar requisições feitas
requisicoes_realizadas = 0

# Gerar número inicial de músicas até a pausa
musicas_ate_pausa = random.randint(44, 45)

# Configuração para salvar os dados
for index, row in tqdm(df.iterrows(), total=len(df), desc="Processando letras"):
    id_musica = row['ID']
    musica = row['Nome']
    artista = row['Artista']
    ano = row['Ano']

    # Sanitizar o nome da música para garantir que não contenha caracteres inválidos
    musica_sanitizada = musica.replace(' ', '_')

    # Nome do arquivo JSON para salvar os resultados
    file_path = output_dir / f"{id_musica}_{musica_sanitizada}.json"

    # Verificar se o arquivo já existe
    if not file_path.exists():
        tqdm.write(f"Buscando letra: {musica} (Ano: {ano}, ID: {id_musica})")
        dados = buscar_letra_e_detalhes(musica, f' {artista}', id_musica)
        requisicoes_realizadas += 1        
        # Se a letra for encontrada, salvar no arquivo JSON
        if dados:
            file_path.write_text(json.dumps(dados, ensure_ascii=False, indent=4), encoding='utf-8')
    

        # Pausa aleatória após atingir o número de músicas processadas
        if requisicoes_realizadas > 0 and requisicoes_realizadas % musicas_ate_pausa == 0:
            tempo_pausa = 0
            tqdm.write(f"Pausando por {int(tempo_pausa)} segundos... ({musicas_ate_pausa} músicas processadas)")
            time.sleep(tempo_pausa)  # Realizar a pausa

            # Redefinir o número de músicas até a próxima pausa
            musicas_ate_pausa = random.randint(35, 40)
            print(musicas_ate_pausa)

# Encerrar o WebDriver
driver.quit()