import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from pathlib import Path
from tqdm import tqdm
import time
import random
import json

options = Options()
options.add_argument("--start-maximized")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# pasta de saída
output_dir = Path("processed")
output_dir.mkdir(parents=True, exist_ok=True)

# função principal


def buscar_letra_e_detalhes(musica, artista, id_musica, link):
    try:
        # abrir site
        driver.get(f"{link}")

        # aguardar página da cifra
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )

        # extrações

        # letra e cifra
        letra_e_cifra = "\n".join(
            e.text for e in driver.find_elements(By.TAG_NAME, "pre"))
        # nome da música
        try:
            nome_musica = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.cifra h1.t1"))).text.strip()
        except TimeoutException:
            nome_musica = None
        # nome do artista
        try:
            nome_artista = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                (By.XPATH, "//a[contains(@href,'/artista/')]"))).text.strip()
        except TimeoutException:
            nome_artista = artista
        # tom
        try:
            tom = tom = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#cifra_tom a"))).text.strip()
        except NoSuchElementException:
            tom = None
        # capotraste
        capotraste = None
        try:
            capo_elem = driver.find_element(
                By.XPATH, "//*[contains(text(),'Capotraste')]")
            capotraste = capo_elem.text.strip()
        except NoSuchElementException:
            capotraste = None
        # compositor
        compositor = None
        try:
            compositor_elem = driver.find_element(
                By.XPATH, "//*[contains(text(),'Composição')]")
            compositor = compositor_elem.text.replace(
                "Composição de", "").strip()
        except NoSuchElementException:
            compositor = None
        # retorno
        return {
            "ID": id_musica,
            "Nome": nome_musica,
            "Artista": nome_artista,
            "Tom": tom,
            "Capotraste": capotraste,
            "Letra_cifra": letra_e_cifra,
            "Compositor": compositor
        }

    # tipos de erro ao processor música
    except TimeoutException:
        print(f"Timeout ao processar {musica}")
        return None
    except Exception as e:
        print(f"Erro ao processar {musica}: {e}")
        return None


# carregar csv
caminho = r"C:\Users\andre\OneDrive\Desktop\musica\musica\data\review_data.csv"
df = pd.read_csv(caminho, sep=";", encoding="utf-8-sig")
df_filtrado = df[df["ID"] >= 5975] # ESTÁ NO NÚMERO CORRETO

# loop principal
requisicoes_realizadas = 0
musicas_ate_pausa = random.randint(40, 50)

for _, row in tqdm(df_filtrado.iterrows(), total=len(df_filtrado), desc="Processando letras"):
    id_musica = row["ID"]
    musica = row["Nome"]
    artista = row["Artista"]
    link = row["Link"]

    musica_sanitizada = musica.replace(" ", "_").replace("/", "_")
    file_path = output_dir / f"{id_musica}_{musica_sanitizada}.json"

    if not file_path.exists():
        dados = buscar_letra_e_detalhes(musica, artista, id_musica, link)
        requisicoes_realizadas += 1

        if dados:
            file_path.write_text(
                json.dumps(dados, ensure_ascii=False, indent=4),
                encoding="utf-8"
            )

        if requisicoes_realizadas % musicas_ate_pausa == 0:
            time.sleep(random.randint(30, 60))
            musicas_ate_pausa = random.randint(35, 45)

driver.quit()
