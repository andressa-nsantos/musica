import os
import json
import pandas as pd

# caminho da pasta
processed = r"C:\Users\andre\OneDrive\Desktop\musica\musica\processed"
dados_iniciais = []

# percorre todos os arquivos da pasta
for arquivo in os.listdir(processed):
    if arquivo.endswith(".json"):
        caminho_arquivo = os.path.join(processed, arquivo)
        
        with open(caminho_arquivo, "r", encoding="utf-8") as f:
            conteudo = json.load(f, strict=False)
            dados_iniciais.append(conteudo)

# cria o DataFrame
dados = pd.DataFrame(dados_iniciais)

# corrigindo os anos
def atribuir_ano(id_):
    id_ = int(id_)
    # 1958–1989 (blocos de 100)
    if 1 <= id_ <= 3200:
        return 1958 + (id_ - 1) // 100
    # 1990
    elif 3201 <= id_ <= 3301:
        return 1990
    # 1992–2000 (pula 1991)
    elif 3302 <= id_ <= 4201:
        return 1992 + (id_ - 3302) // 100
    # 1991 (fora de ordem)
    elif 4202 <= id_ <= 4301:
        return 1991
    # 2001
    elif 4302 <= id_ <= 4398:
        return 2001
    # 2002–2004 (blocos de 100 certinho)
    elif 4399 <= id_ <= 4698:
        return 2002 + (id_ - 4399) // 100
    # 2005 (ligeiramente menor)
    elif 4699 <= id_ <= 4797:
        return 2005
    # 2006
    elif 4798 <= id_ <= 4893:
        return 2006
    # 2007–2016 (terminando em __91)
    elif 4894 <= id_ <= 5891:
        return 2007 + (id_ - 4894) // 100
    # 2017
    elif 5892 <= id_ <= 5978:
        return 2017
    else:
        return None
    
dados["ID"] = dados["ID"].astype(int)
dados["Ano"] = dados["ID"].apply(atribuir_ano)

# fazer arquivo .csv e .xlsx
dados.to_csv("musicas.csv", encoding="utf-8")
dados.to_excel("musicas.xlsx")