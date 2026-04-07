import pandas as pd
import re
from tqdm import tqdm
import os
print("Pasta atual:", os.getcwd())
print("Arquivos aqui:", os.listdir())

dados = pd.read_csv("C:/Users/andre/OneDrive/Desktop/musica/musica/database/musicas.csv",encoding="utf-8")

padrao_acorde = re.compile(r'\b([A-G](#|b)?(m|maj|min|dim|aug|sus)?\d*(\([^\)]*\))?(\/[A-G](#|b)?)?)\b')

def eh_linha_tablatura(linha):
    return bool(re.match(r'^[EADGBe]\|[-0-9|]+', linha.strip()))

def extrair_partes(texto):
    if pd.isna(texto):
        return "", "", ""
    linhas = texto.split("\n")
    cifras = []
    letras = []
    limpo = []
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        # remover tablatura
        if eh_linha_tablatura(linha):
            continue
        # remover [Intro], [Solo], etc
        if linha.startswith("[") and linha.endswith("]"):
            continue
        # extrair acordes
        acordes = padrao_acorde.findall(linha)
        acordes = [a[0] for a in acordes]
        # remover acordes da linha
        linha_sem_acordes = padrao_acorde.sub("", linha).strip()
        # limpar espaços
        linha_sem_acordes = re.sub(r'\s+', ' ', linha_sem_acordes)
        # ===== CLASSIFICAÇÃO =====
        # só cifra
        if acordes and linha_sem_acordes == "":
            cifras.append(" ".join(acordes))
        # cifra + letra
        elif acordes and linha_sem_acordes != "":
            cifras.append(" ".join(acordes))
            letras.append(linha_sem_acordes)
        # só letra
        else:
            if re.search(r'[a-zA-ZÀ-ÿ]', linha):
                letras.append(linha)
        limpo.append(linha)
    return (
        "\n".join(limpo),          # letra_cifra_limpa
        " | ".join(cifras),       # cifras
        " ".join(letras)          # letra
    )

# =========================
# 4. APLICAR NO DATAFRAME
# =========================

# (opcional) ver progresso
for i, row in dados.iterrows():
    print(f"Processando {i} - {row.get('Nome', '')}")
    resultado = extrair_partes(row['Letra_cifra'])
    dados.at[i, 'letra_cifra_limpa'] = resultado[0]
    dados.at[i, 'cifras'] = resultado[1]
    dados.at[i, 'letra'] = resultado[2]

# =========================
# 5. REMOVER COLUNA ORIGINAL
# =========================

dados = dados.drop(columns=['Letra_cifra'])

# =========================
# 6. SALVAR RESULTADO
# =========================

dados.to_csv("musicas_tratadas.csv", index=False, encoding="utf-8")
dados.to_excel("musicas_tratadas.xlsx")
print("✅ Finalizado com sucesso!")