import streamlit as st
import pandas as pd
import os
import base64

# --- 1. CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="AABB 2026", layout="wide")

st.markdown("""
    <style>
        /* LIMPEZA DE INTERFACE */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        
        /* ESPAÇAMENTO E TÍTULO */
        .block-container { padding-top: 3.5rem; padding-left: 0.5rem; padding-right: 0.5rem; }
        
        .header-campeonato {
            text-align: center; background-color: #f0f2f6; color: #1a1c24;
            padding: 15px; border-radius: 10px; margin-bottom: 20px;
            font-size: clamp(1.1rem, 5vw, 1.5rem); font-weight: bold;
            border: 2px solid #004a99;
        }

        /* TABELA FUNDO CLARO E TEXTO ESCURO */
        [data-testid="stDataFrameDataLayer"] {
            background-color: white;
        }

        /* CARDS DE JOGOS - ESTILO CLARO E LIMPO */
        .jogo-container-borda {
            border: 1px solid #ddd; border-radius: 10px; 
            margin-bottom: 15px; background-color: #ffffff;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        }
        .data-header { 
            text-align: center; font-size: 13px; background-color: #f8f9fa; 
            padding: 5px; color: #666; border-bottom: 1px solid #eee;
        }
        .jogo-card { 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 20px 10px; color: #333;
        }
        .time-box { width: 38%; font-size: 16px; font-weight: bold; }
        .placar-box { 
            width: 20%; text-align: center; font-size: 22px; 
            font-weight: bold; color: #ffffff; background: #28a745;
            border-radius: 8px; padding: 5px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Função para converter imagem para Base64 (Obrigatória para funcionar no Streamlit Cloud)
def get_base64_img(path):
    try:
        if isinstance(path, str):
            # Limpa espaços e barras extras do caminho
            path = path.strip().lstrip('/')
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return base64.b64encode(f.read()).decode()
    except Exception as e:
        return None
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
    st.error(f"Erro ao carregar arquivos: {e}")
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
    
    def colorir_g8(row):
        return ['background-color: #d4edda; color: #155724'] * len(row) if row.name <= 8 else ['background-color: white; color: black'] * len(row)

    st.dataframe(df_rank.style.apply(colorir_g8, axis=1), width="stretch")

# --- ABA 2: JOGOS ---
with tab_jogos:
    rodada_sel = st.selectbox("Rodada", sorted(df_jogos['RODADA'].unique()), label_visibility="collapsed")
    jogos_r = df_jogos[df_jogos['RODADA'] == rodada_sel]
    
    for _, j in jogos_r.iterrows():
        g_m = int(j['GOLS_M']) if pd.notnull(j['GOLS_M']) else "-"
        g_v = int(j['GOLS_V']) if pd.notnull(j['GOLS_V']) else "-"
        
        st.markdown(f"""
            <div class="jogo-container-borda">
                <div class="data-header">📅 {j['DATA']}</div>
                <div class="jogo-card">
                    <div class="time-box" style="text-align: right;">{j['TIME A']}</div>
                    <div class="placar-box">{g_m} x {g_v}</div>
                    <div class="time-box" style="text-align: left;">{j['TIME B']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

# --- ABA 3: TIMES ---
with tab_times:
    time_sel = st.selectbox("Ver Time", df_times['NOME'].unique(), label_visibility="collapsed")
    
    dados_time = df_times[df_times['NOME'] == time_sel].iloc[0]
    c1, c2 = st.columns(2)
    
    # Exibe Escudo
    b64_logo = get_base64_img(dados_time["LOGO"])
    if b64_logo:
        c1.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{b64_logo}" width="120"><br><b>Escudo</b></div>', unsafe_allow_html=True)
    
    # Exibe Camisa
    b64_camisa = get_base64_img(dados_time["CAMISA"])
    if b64_camisa:
        c2.markdown(f'<div style="text-align:center;"><img src="data:image/png;base64,{b64_camisa}" width="120"><br><b>Camisa</b></div>', unsafe_allow_html=True)

    st.markdown("---")
    elenco = df_jogadores[df_jogadores['NOME_TIME'] == time_sel].sort_values(by='NUMERO')
    for _, row in elenco.iterrows():
        st.write(f"**{int(row['NUMERO'])}** - {row['NOME_JOGADOR']}")