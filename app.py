import streamlit as st
import pandas as pd
import os
import base64

# --- 1. CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="AABB 2026", layout="wide")

st.markdown("""
    <style>
        /* Desce o título e define fundo claro (para classificação e times) */
        .block-container { padding-top: 5rem !important; background-color: white; }
        
        .header-campeonato {
            text-align: center; background-color: #f8fafc; color: #1e293b;
            padding: 15px; border-radius: 10px; margin-bottom: 25px;
            font-size: 1.5rem; font-weight: bold; border: 1px solid #e2e8f0;
        }
    
        /* CLASSIFICAÇÃO: Tabela toda branca e centralizada, SEM cores de G8 */
        div[data-testid="stTable"] { overflow-x: auto !important; }
        div[data-testid="stTable"] table { background-color: white !important; color: black !important; border-collapse: collapse; }
        
        /* Fixar a primeira coluna (Classificação) com fundo branco */
        div[data-testid="stTable"] table thead tr th:first-child,
        div[data-testid="stTable"] table tbody tr td:first-child {
            position: sticky !important;
            left: 0 !important;
            background-color: white !important; /* Fundo branco garantido */
            z-index: 99 !important;
            min-width: 100px !important;
            border-right: 1px solid #cbd5e1;
            text-align: center !important; /* Número centralizado */
        }

        /* JOGOS: Layout de Cards ESCUROS (Restaurado conforme pedido) */
        .jogo-container-borda { border: 1px solid #31333F; border-radius: 8px; margin-bottom: 12px; overflow: hidden; background-color: #1a1c24; }
        .data-header { text-align: center; font-size: 14px !important; background-color: #31333F; padding: 6px; color: white !important; text-transform: uppercase; font-weight: bold; }
        .jogo-card { display: flex; justify-content: space-between; align-items: center; padding: 15px 10px; }
        .time-box { width: 38%; font-size: 16px; font-weight: bold; text-align: center; color: white !important; }
        .placar-box { width: 20%; text-align: center; font-size: 22px; color: #00ff00 !important; font-weight: 800; background: #0e1117; border-radius: 5px; padding: 5px 0; }

        /* TIMES: Fotos Lado a Lado no Mobile */
        .flex-fotos { display: flex; justify-content: space-around; align-items: center; width: 100%; margin: 15px 0; }
        .foto-item { text-align: center; width: 48%; }
        .foto-item p { color: #1e293b; font-weight: bold; margin-top: 5px; font-size: 14px; }
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
    st.error(f"Erro ao carregar arquivos: {e}")
    st.stop()

st.markdown('<div class="header-campeonato">🏆 CAMPEONATO AABB 2026</div>', unsafe_allow_html=True)

tab_class, tab_jogos, tab_times = st.tabs(["📊 Classificação", "📅 Jogos", "🛡️ Times"])

# --- ABA 1: CLASSIFICAÇÃO (Final: Centralizada, G8 Verde e Coluna Fixa) ---
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
    
    # Organiza as colunas: Classificação primeiro, Time segundo
    df_rank = df_rank.reset_index().rename(columns={'index': 'Classificação'})
    colunas_ordem = ['Classificação', 'Time', 'P', 'J', 'V', 'E', 'D', 'GP', 'GC', 'SG']
    df_rank = df_rank[colunas_ordem]

    # Estilização: G8 Verde e Centralização
    def estilar(df):
        return df.style.apply(lambda x: ['background-color: rgba(34, 197, 94, 0.2)' if x['Classificação'] <= 8 else '' for _ in x], axis=1)\
                       .set_properties(**{'text-align': 'center'})

    st.dataframe(
        estilar(df_rank),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Classificação": st.column_config.NumberColumn("Classificação", pinned=True, width="small"),
            "Time": st.column_config.TextColumn("Time", pinned=True, width="medium")
        }
    )

# --- ABA 2: JOGOS (RESTAURADO PARA DESIGN ESCURO) ---
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
    
    b_logo = get_base64_img(str(d["LOGO"]))
    b_cam = get_base64_img(str(d["CAMISA"]))
    
    # HTML Lado a Lado (Garantido para Mobile)
    st.markdown(f"""
    <div class="flex-fotos">
        <div class="foto-item">
            <img src="data:image/png;base64,{b_logo if b_logo else ''}" width="100">
            <p>Escudo</p>
        </div>
        <div class="foto-item">
            <img src="data:image/png;base64,{b_cam if b_cam else ''}" width="100">
            <p>Camisa</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border: 0.5px solid #e2e8f0;'>", unsafe_allow_html=True)
    elenco = df_jogadores[df_jogadores['NOME_TIME'] == time_sel].sort_values(by='NUMERO')
    for _, row in elenco.iterrows():
        st.write(f"**{int(row['NUMERO'])}** - {row['NOME_JOGADOR']}")