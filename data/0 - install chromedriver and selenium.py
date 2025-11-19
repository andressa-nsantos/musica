# Instalar o chromedriver na mesma versão do seu google
# Instalar a biblioteca selenium
# Importar a biblioteca selenium e acessar o navegador

from selenium import webdriver
import time

# Definir navegador
navegador = webdriver.Chrome()
# Definir um site
navegador.get('https://www.google.com.br')
time.sleep(3)
navegador.quit()
