import streamlit as st
import pandas as pd
import os
import base64

# --- 1. CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="AABB 2026", layout="wide")

st.markdown("""
    <style>
        /* Ajuste do Título: Desce o nome para não cortar no mobile */
        .block-container { padding-top: 5rem !important; }
        
        .header-campeonato {
            text-align: center; background-color: #0e1117; color: white;
            padding: 15px; border-radius: 10px; margin-bottom: 25px;
            font-size: 1.5rem; font-weight: bold; border: 2px solid #31333F;
        }

        /* Ajuste para o cabeçalho do índice (Classificação) não ficar preto */
        .stDataFrame thead tr th:first-child {
            background-color: white !important;
            color: #666666 !important;
        }

        /* Estilo dos Cards de Jogos na Aba 2 */
        .jogo-container-borda { border: 1px solid #31333F; border-radius: 5px; margin-bottom: 10px; overflow: hidden; }
        .data-header { text-align: center; font-size: 13px; background-color: #31333F; padding: 5px; color: white; }
        .jogo-card { display: flex; justify-content: space-around; align-items: center; padding: 10px; }
        .time-box { width: 40%; font-size: 16px; font-weight: bold; text-align: center; }
        .placar-box { width: 20%; text-align: center; font-size: 22px; color: #00ff00; font-weight: bold; background: #262730; border-radius: 5px; }
    </style>
""", unsafe_allow_html=True)

def get_base64_img(path):
    try:
        if isinstance(path, str) and os.path.exists(path):
            with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return None
    return None

def carregar_csv(caminho):
    df = pd.read_csv(caminho, sep=None, engine='python', encoding='utf-8-sig')
    df.columns = [str(c).strip().upper() for c in df.columns]
    return df

# --- 2. CARGA DE DADOS ---
try:
    df_jogos = carregar_csv('jogos.csv')
    df_times = carregar_csv('times.csv')
    df_jogadores = carregar_csv('jogadores.csv')
except Exception as e:
    st.error(f"Erro: {e}")
    st.stop()

st.markdown('<div class="header-campeonato">🏆 CAMPEONATO AABB 2026</div>', unsafe_allow_html=True)

tab_class, tab_jogos, tab_times = st.tabs(["📊 Classificação", "📅 Jogos", "🛡️ Times"])

# --- ABA 1: CLASSIFICAÇÃO ---
with tab_class:
    stats = {t: {"P": 0, "J": 0, "V": 0, "E": 0, "D": 0, "GP": 0, "GC": 0, "SG": 0} for t in df_times['NOME'].unique()}
    jogos_ok = df_jogos.dropna(subset=['GOLS_M', 'GOLS_V'])
    
    for _, j in jogos_ok.iterrows():
        m, v = str(j['TIME A']).strip(), str(j['TIME B']).strip()
        if m in stats and v in stats:
            gm, gv = int(j['GOLS_M']), int(j['GOLS_V'])
            stats[m]["J"]+=1; stats[v]["J"]+=1
            stats[m]["GP"]+=gm; stats[v]["GP"]+=gv
            stats[m]["GC"]+=gv; stats[v]["GC"]+=gm
            if gm > gv: stats[m]["P"]+=3; stats[m]["V"]+=1; stats[v]["D"]+=1
            elif gv > gm: stats[v]["P"]+=3; stats[v]["V"]+=1; stats[m]["D"]+=1
            else: stats[m]["P"]+=1; stats[v]["P"]+=1; stats[m]["E"]+=1; stats[v]["E"]+=1

    for t in stats: stats[t]["SG"] = stats[t]["GP"] - stats[t]["GC"]
    
    df_rank = pd.DataFrame.from_dict(stats, orient='index').reset_index()
    df_rank.columns = ['Time', 'P', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG']
    df_rank = df_rank.sort_values(by=['P', 'V', 'SG', 'GP'], ascending=False).reset_index(drop=True)
    df_rank.index += 1
    
    # Preenche o cabeçalho que era preto com texto cinza
    df_rank.index.name = 'Pos'
    
    def colorir_g8(row):
        return ['background-color: rgba(0, 255, 0, 0.1)'] * len(row) if row.name <= 8 else [''] * len(row)

    # Exibe como DataFrame usando o padrão de 2026
    st.dataframe(
        df_rank.style.apply(colorir_g8, axis=1), 
        width=None, 
        use_container_width=True,
        column_config={
            "Time": st.column_config.TextColumn("Time", pinned=True), # TRAVA A COLUNA DO TIME
            "Pos": st.column_config.NumberColumn("Pos", width="small")
        }
    )

# --- ABA 2: JOGOS ---
with tab_jogos:
    rodada_sel = st.selectbox("Rodada", sorted(df_jogos['RODADA'].unique()), label_visibility="collapsed")
    jogos_r = df_jogos[df_jogos['RODADA'] == rodada_sel]
    for _, j in jogos_r.iterrows():
        g_m = int(j['GOLS_M']) if pd.notnull(j['GOLS_M']) else "-"
        g_v = int(j['GOLS_V']) if pd.notnull(j['GOLS_V']) else "-"
        st.markdown(f"""
            <div class="jogo-container-borda">
                <div class="data-header">{j['DATA']}</div>
                <div class="jogo-card">
                    <div class="time-box">{j['TIME A']}</div>
                    <div class="placar-box">{g_m} x {g_v}</div>
                    <div class="time-box">{j['TIME B']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- ABA 3: TIMES ---
with tab_times:
    time_sel = st.selectbox("Ver Time", df_times['NOME'].unique(), label_visibility="collapsed")
    d = df_times[df_times['NOME'] == time_sel].iloc[0]
    
    c1, c2 = st.columns(2)
    b_logo = get_base64_img(str(d["LOGO"]))
    if b_logo: 
        c1.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{b_logo}" width="100"><br><b>Escudo</b></div>', unsafe_allow_html=True)
    
    b_cam = get_base64_img(str(d["CAMISA"]))
    if b_cam: 
        c2.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{b_cam}" width="100"><br><b>Camisa</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    elenco = df_jogadores[df_jogadores['NOME_TIME'] == time_sel].sort_values(by='NUMERO')
    for _, row in elenco.iterrows():
        st.write(f"**{int(row['NUMERO'])}** - {row['NOME_JOGADOR']}")