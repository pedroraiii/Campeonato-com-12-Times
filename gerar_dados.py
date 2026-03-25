import pandas as pd

# 1. Lista de times em ORDEM ALFABÉTICA (será o índice 1 a 12)
nomes_times = [
    "Atlético Mineiro", "Botafogo", "Corinthians", "Cruzeiro", "Flamengo", 
    "Fluminense", "Grêmio", "Internacional", "Palmeiras", "Santos", 
    "São Paulo", "Vasco da Gama"
]

# Mapeamento de formatos de camisas que você informou
formatos_camisas = {
    "Grêmio": "webp", "São Paulo": "webp", "Internacional": "jpg"
}

dados_times = []
for nome in nomes_times:
    ext_camisa = formatos_camisas.get(nome, "avif")
    dados_times.append({
        "Nome": nome,
        "Logo": f"escudos/{nome} HD.png",
        "Camisa": f"camisas/{nome} Camisa.{ext_camisa}"
    })

df_times = pd.DataFrame(dados_times)
df_times.to_csv('times.csv', index=False)

# 2. Gerar 20 jogadores por time
lista_jogadores = []
for time in nomes_times:
    for i in range(1, 21):
        lista_jogadores.append([time, i, f"JOGADOR {time[:3].upper()}{i}"])

df_jogadores = pd.DataFrame(lista_jogadores, columns=['Nome_Time', 'Numero', 'Nome_Jogador'])
df_jogadores.to_csv('jogadores.csv', index=False)

print("Dados gerados com sucesso em ordem alfabética!")