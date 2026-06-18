import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go
import base64
import os
from datetime import datetime
# NOVO: FEATURE 2 - Imports para efeitos sonoros
import time

# ==========================================
# 1. CONFIGURAÇÕES DA PÁGINA & BRANDING (FRONT-END EXTREME SUPREME)
# ==========================================
st.set_page_config(page_title="Multiplica do Futuro - Check-in", page_icon="🚀", layout="wide")

# Função para converter imagem em base64 (necessário para Background CSS)
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except FileNotFoundError:
        return ""

# Carrega os logos
bg_img_b64 = get_base64_of_bin_file("logo_ministerio_1@4x.png")
logo_svg_b64 = get_base64_of_bin_file("vermelho_horiz.svg")

# Monta o CSS do background condicionalmente com efeito Glassmorphism
background_css = ""
if bg_img_b64:
    background_css = f"""
    .stApp {{
        background-color: #050810; /* Azul quase preto ultra formal */
        background-image: url("data:image/png;base64,{bg_img_b64}");
        background-position: right 5% bottom 5%;
        background-repeat: no-repeat;
        background-size: 30vw; 
        background-attachment: fixed;
    }}
    /* Camada escura por cima da logo para dar o tom Cyber-Dark */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(135deg, rgba(5,8,16,0.95) 0%, rgba(10,15,30,0.85) 100%);
        z-index: -1;
    }}
    """
else:
    background_css = """
    .stApp {
        background-color: #050810; 
        background: radial-gradient(circle at top left, #0A1020, #050810);
    }
    """

# CSS Customizado Geral - O "Anabolizante" Visual
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Poppins:wght@400;600;800&display=swap');

    {background_css}
    
    /* Animação de pulso neon para o título */
    @keyframes neonPulse {{
        0% {{ text-shadow: 0 0 10px rgba(0, 229, 255, 0.2), 0 0 20px rgba(0, 229, 255, 0.2); }}
        50% {{ text-shadow: 0 0 15px rgba(0, 229, 255, 0.6), 0 0 30px rgba(0, 229, 255, 0.4); }}
        100% {{ text-shadow: 0 0 10px rgba(0, 229, 255, 0.2), 0 0 20px rgba(0, 229, 255, 0.2); }}
    }}

    /* Layout do Topo */
    .header-container {{
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin-bottom: 20px;
        padding-top: 20px;
    }}
    
    .top-left-logo {{
        position: absolute;
        left: 20px;
        top: 10px;
        height: 60px; /* Ajuste seguro para o SVG */
        filter: drop-shadow(0px 0px 8px rgba(255,255,255,0.2));
        transition: transform 0.3s ease;
    }}
    .top-left-logo:hover {{
        transform: scale(1.05);
    }}
    
    .title-wrapper {{
        text-align: center;
    }}

    /* Títulos */
    .main-title {{
        font-family: 'Poppins', sans-serif;
        color: #FFFFFF;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0px;
        padding-bottom: 0px;
        letter-spacing: -1px;
        animation: neonPulse 3s infinite alternate;
    }}
    
    .sub-title {{
        font-family: 'Rajdhani', sans-serif;
        color: #00E5FF; /* Ciano Tech */
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: -5px;
        letter-spacing: 4px;
        text-transform: uppercase;
    }}
    
    /* ========================================= */
    /* CARDS EXTREME SUPREME (Glassmorphism + Neon) */
    /* ========================================= */
    .metric-card {{
        background: rgba(20, 25, 40, 0.5); /* Fundo de vidro */
        backdrop-filter: blur(12px); /* Desfoque do fundo */
        -webkit-backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 30px 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-bottom: 4px solid #00E5FF;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Efeito elástico */
        margin-bottom: 15px;
        position: relative;
        overflow: hidden;
    }}
    
    /* Efeito de brilho interno sutil */
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0; left: -100%; width: 50%; height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        transform: skewX(-20deg);
        transition: 0.5s;
    }}
    .metric-card:hover::before {{ left: 150%; }}
    
    /* INTERAÇÕES DE HOVER DINÂMICAS */
    .metric-card:hover {{
        transform: translateY(-12px) scale(1.03); /* Cresce e sobe */
        border-color: #00E5FF;
        box-shadow: 0 15px 35px rgba(0, 229, 255, 0.4), inset 0 0 15px rgba(0, 229, 255, 0.1);
    }}
    
    /* Card Sucesso (Verde Neon) */
    .metric-card.success {{ border-bottom-color: #39FF14; }}
    .metric-card.success:hover {{ 
        box-shadow: 0 15px 35px rgba(57, 255, 20, 0.4), inset 0 0 15px rgba(57, 255, 20, 0.1); 
        border-color: #39FF14;
    }}
    
    /* Card Aviso (Laranja Neon) */
    .metric-card.warning {{ border-bottom-color: #FF8C00; }}
    .metric-card.warning:hover {{ 
        box-shadow: 0 15px 35px rgba(255, 140, 0, 0.4), inset 0 0 15px rgba(255, 140, 0, 0.1); 
        border-color: #FF8C00;
    }}
    
    /* Textos dos Cards */
    .metric-value {{
        font-family: 'Rajdhani', sans-serif;
        font-size: 4rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0;
        line-height: 1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }}
    
    .metric-label {{
        font-family: 'Poppins', sans-serif;
        font-size: 0.85rem;
        color: #A0AEC0;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 600;
        margin: 15px 0 0 0;
    }}

    /* Botões Cyberpunk */
    div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {{
        transition: all 0.3s ease !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
        background: rgba(10, 15, 30, 0.7) !important;
        backdrop-filter: blur(5px) !important;
        color: #E2E8F0 !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }}
    
    div[data-testid="stButton"] button:hover, div[data-testid="stDownloadButton"] button:hover {{
        transform: translateY(-4px) !important;
        box-shadow: 0 10px 25px rgba(0, 229, 255, 0.4) !important;
        border-color: #00E5FF !important;
        color: #00E5FF !important;
        background: rgba(0, 229, 255, 0.05) !important;
    }}

    /* ========================================= */
    /* NOVO: FEATURE 1 - Relógio Digital em Tempo Real */
    /* ========================================= */
    .digital-clock {{
        font-family: 'Rajdhani', monospace;
        font-size: 2.2rem;
        color: #00E5FF;
        font-weight: 700;
        text-shadow: 0 0 10px rgba(0, 229, 255, 0.5), 0 0 20px rgba(0, 229, 255, 0.3);
        text-align: center;
        padding: 15px 30px;
        background: rgba(0, 229, 255, 0.05);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
        animation: clockGlow 2s ease-in-out infinite;
        margin-bottom: 15px;
        letter-spacing: 3px;
    }}

    @keyframes clockGlow {{
        0%, 100% {{ text-shadow: 0 0 10px rgba(0, 229, 255, 0.5), 0 0 20px rgba(0, 229, 255, 0.3); }}
        50% {{ text-shadow: 0 0 15px rgba(0, 229, 255, 0.8), 0 0 30px rgba(0, 229, 255, 0.5); }}
    }}

    .scanning-status {{
        font-family: 'Rajdhani', monospace;
        font-size: 0.95rem;
        color: #00E5FF;
        letter-spacing: 2px;
        text-transform: uppercase;
        animation: scanning 1.5s ease-in-out infinite;
    }}

    @keyframes scanning {{
        0% {{ opacity: 0.5; }}
        50% {{ opacity: 1; }}
        100% {{ opacity: 0.5; }}
    }}

    /* ========================================= */
    /* NOVO: FEATURE 3 - Tooltips nos Cards */
    /* ========================================= */
    .metric-card[title] {{
        cursor: help;
    }}

    .tooltip-custom {{
        position: relative;
    }}

    .tooltip-custom:hover::after {{
        content: attr(data-tooltip);
        position: absolute;
        bottom: 110%;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.9);
        color: #00E5FF;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 1000;
        border: 1px solid rgba(0, 229, 255, 0.3);
        font-family: 'Poppins', sans-serif;
        pointer-events: none;
    }}

    /* ========================================= */
    /* NOVO: FEATURE 4 - Animação de Entrada (Fade-In e Slide-Up) */
    /* ========================================= */
    @keyframes fadeInSlideUp {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    .data-table {{
        animation: fadeInSlideUp 0.8s ease-out forwards;
    }}

    .plotly-chart {{
        animation: fadeInSlideUp 1s ease-out forwards;
    }}

    /* ========================================= */
    /* NOVO: FEATURE 5 - Efeito Data Matrix no Background dos Cards */
    /* ========================================= */
    .metric-card {{
        background-image: 
            linear-gradient(0deg, transparent 24%, rgba(0, 229, 255, 0.03) 25%, rgba(0, 229, 255, 0.03) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.03) 75%, rgba(0, 229, 255, 0.03) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(0, 229, 255, 0.03) 25%, rgba(0, 229, 255, 0.03) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.03) 75%, rgba(0, 229, 255, 0.03) 76%, transparent 77%, transparent);
        background-size: 60px 60px;
        background-position: 0 0;
        opacity: 1;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}

    .metric-card:hover {{
        background-image: 
            linear-gradient(0deg, transparent 24%, rgba(0, 229, 255, 0.08) 25%, rgba(0, 229, 255, 0.08) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.08) 75%, rgba(0, 229, 255, 0.08) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(0, 229, 255, 0.08) 25%, rgba(0, 229, 255, 0.08) 26%, transparent 27%, transparent 74%, rgba(0, 229, 255, 0.08) 75%, rgba(0, 229, 255, 0.08) 76%, transparent 77%, transparent);
        background-size: 60px 60px;
    }}

</style>
""", unsafe_allow_html=True)

# Renderiza o Header Dinâmico
img_tag = f'<img src="data:image/svg+xml;base64,{logo_svg_b64}" class="top-left-logo">' if logo_svg_b64 else ''
st.markdown(f"""
    <div class="header-container">
        {img_tag}
        <div class="title-wrapper">
            <h1 class='main-title'>Painel de Recepção</h1>
            <h3 class='sub-title'>Multiplica do Futuro</h3>
        </div>
    </div>
""", unsafe_allow_html=True)

# NOVO: FEATURE 1 - Relógio Digital em Tempo Real + Status Scanning
st.markdown("""
<div class="digital-clock" id="live-clock">⏱️ 00:00:00</div>
<div class="scanning-status">🔴 ● ● ● SCANNING... LIVE ● ● ●</div>
<script>
function updateClock() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    document.getElementById('live-clock').textContent = hours + ':' + minutes + ':' + seconds;
}
updateClock();
setInterval(updateClock, 1000);
</script>
""", unsafe_allow_html=True)


# ID capturado da planilha oficial de respostas do evento
SHEET_ID = "1JLBii5KIj6SzkZF7T2Lgr-Bc9nMMbtf1haygbn6w-lw"
URL_FORMS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def limpar_cpf(cpf):
    if pd.isna(cpf):
        return ""
    return re.sub(r'\D', '', str(cpf)).zfill(11)

# ==========================================
# 2. MOTOR DE DADOS (PIPELINE)
# ==========================================
@st.cache_data(ttl=10)
def carregar_dados():
    try:
        try:
            df_inscritos = pd.read_csv("inscritos_base.csv", sep=';', on_bad_lines='skip')
        except Exception:
            df_inscritos = pd.read_csv("inscritos_base.csv", sep=',', on_bad_lines='skip')
            
        colunas_cpf_locais = [col for col in df_inscritos.columns if 'cpf' in col.lower()]
        
        if not colunas_cpf_locais:
            st.error("🚨 Erro: Não encontrei coluna de 'CPF' no arquivo 'inscritos_base.csv'.")
            return pd.DataFrame(), 0
        
        coluna_cpf_oficial = colunas_cpf_locais[0]
        df_inscritos['CPF_LIMPO'] = df_inscritos[coluna_cpf_oficial].apply(limpar_cpf)
        df_inscritos = df_inscritos.drop_duplicates(subset=['CPF_LIMPO'], keep='first')
        total_inscritos_base = len(df_inscritos)
        
        df_checkin = pd.read_csv(URL_FORMS)
        df_checkin['CPF_LIMPO'] = df_checkin['Qual é seu CPF?'].apply(limpar_cpf)
        
        df_checkin['Qual é seu nome completo?'] = df_checkin['Qual é seu nome completo?'].str.title() 
        df_checkin = df_checkin.drop_duplicates(subset=['CPF_LIMPO'], keep='first')
        df_checkin = df_checkin.sort_values(by='Carimbo de data/hora', ascending=False)
        
        df_checkin['Status'] = df_checkin['CPF_LIMPO'].isin(df_inscritos['CPF_LIMPO'])
        
        return df_checkin, total_inscritos_base
    except Exception as e:
        st.error(f"Erro ao carregar banco de dados: {e}")
        return pd.DataFrame(), 0

# ==========================================
# 3. PROCESSAMENTO E INTERFACE VISUAL
# ==========================================
df_total, total_inscritos = carregar_dados()

# NOVO: FEATURE 2 - Controle de Áudio para Notificação de Check-in
if 'ultima_verificacao' not in st.session_state:
    st.session_state.ultima_verificacao = len(df_total)

novos_checkins = len(df_total) - st.session_state.ultima_verificacao
st.session_state.ultima_verificacao = len(df_total)

if 'Status' in df_total.columns:
    lista_presenca = df_total[df_total['Status'] == True]
    lista_convidados = df_total[df_total['Status'] == False] 
    
    qtd_presentes = len(lista_presenca)
    qtd_convidados = len(lista_convidados)
    qtd_ausentes = max(0, total_inscritos - qtd_presentes)
    
    if total_inscritos > 0:
        pct_lotação = min(qtd_presentes / total_inscritos, 1.0)
        st.progress(pct_lotação, text=f"⚡ STATUS DA OPERAÇÃO: {int(pct_lotação * 100)}% de ocupação atingida")
    
    st.write("")
    
    # Grid Superior: Cards HTML Animados + Gráfico
    col_metrics, col_chart = st.columns([1.3, 1])
    
    with col_metrics:
        st.write("")
        st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div class="metric-card" style="flex: 1;">
                    <p class="metric-value">{total_inscritos}</p>
                    <p class="metric-label">Total Base Oficial</p>
                </div>
                <div class="metric-card" style="flex: 1;">
                    <p class="metric-value">{len(df_total)}</p>
                    <p class="metric-label">Check-ins Físicos</p>
                </div>
            </div>
            <div style="display: flex; gap: 20px;">
                <div class="metric-card success" style="flex: 1;" title="Sincronizado diretamente com a roleta principal">
                    <p class="metric-value" style="color: #39FF14;">{qtd_presentes}</p>
                    <p class="metric-label">✅ Confirmados</p>
                </div>
                <div class="metric-card warning" style="flex: 1;" title="Pessoas sem registro anterior na base de dados">
                    <p class="metric-value" style="color: #FF8C00;">{qtd_convidados}</p>
                    <p class="metric-label">⚠️ Convidados Extras</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # NOVO: FEATURE 2 - Reproduzir som se houver novos check-ins
        if novos_checkins > 0:
            st.markdown("""
            <audio autoplay style="display:none;">
                <source src="https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3" type="audio/mpeg">
            </audio>
            """, unsafe_allow_html=True)
        
        # Paleta de Cores Atualizada para o Tema Neon
        labels = ['Inscritos Presentes', 'Inscritos Ausentes', 'Convidados Extras']
        valores = [qtd_presentes, qtd_ausentes, qtd_convidados]
        cores = ['#39FF14', '#161B29', '#FF8C00'] # Verde Neon, Azul/Cinza do Fundo, Laranja Neon
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=valores, 
            hole=.65,
            marker=dict(colors=cores, line=dict(color='#050810', width=4)), 
            textinfo='percent',
            textfont=dict(color='white', size=16, family='Rajdhani')
        )])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text='RADAR', x=0.5, y=0.5, font_size=20, font_family='Rajdhani', font_color='#00E5FF', showarrow=False)],
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(color='#FFFFFF', family='Poppins', size=12)),
            margin=dict(t=10, b=10, l=10, r=10),
            height=340
        )
        # NOVO: FEATURE 4 - Animação de entrada do gráfico
        st.markdown('<div class="plotly-chart">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown("---") 
    
    # Tabelas de Visualização
    col_esquerda, col_direita = st.columns(2)
    colunas_exibicao = ['Carimbo de data/hora', 'Qual é seu nome completo?', 'Qual é seu CPF?']
    
    with col_esquerda:
        st.markdown(f"<h3 style='color: #39FF14; font-family: Poppins; text-shadow: 0 0 10px rgba(57,255,20,0.3);'>✅ Lista de Presença ({qtd_presentes})</h3>", unsafe_allow_html=True)
        st.caption("Fluxo de entrada em tempo real")
        # NOVO: FEATURE 4 - Animação de entrada para tabela de presença
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        try:
            st.dataframe(lista_presenca[colunas_exibicao], use_container_width=True, hide_index=True)
        except KeyError:
            st.dataframe(lista_presenca, use_container_width=True, hide_index=True) # #OdiamosJava 
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_direita:
        st.markdown(f"<h3 style='color: #FF8C00; font-family: Poppins; text-shadow: 0 0 10px rgba(255,140,0,0.3);'>⚠️ Convidados Extras ({qtd_convidados})</h3>", unsafe_allow_html=True)
        st.caption("Pessoas pendentes de validação manual")
        # NOVO: FEATURE 4 - Animação de entrada para tabela de convidados
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        try:
            st.dataframe(lista_convidados[colunas_exibicao], use_container_width=True, hide_index=True)
        except KeyError:
            st.dataframe(lista_convidados, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    # ==========================================
    # 4. PAINEL DE CONTROLE (BOTÕES)
    # ==========================================
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔄 Sincronizar Radar", use_container_width=True):
            st.cache_data.clear() 
            st.rerun()
            
    with col_btn2:
        try:
            csv_presenca = lista_presenca[colunas_exibicao].to_csv(index=False, sep=';', encoding='utf-8-sig')
        except KeyError:
            csv_presenca = lista_presenca.to_csv(index=False, sep=';', encoding='utf-8-sig')
            
        st.download_button(
            label="📥 Exportar Lista Oficial", 
            data=csv_presenca,
            file_name='checkin_presenca_multiplica.csv',
            mime='text/csv',
            use_container_width=True
        )
        
    with col_btn3:
        try:
            csv_convidados = lista_convidados[colunas_exibicao].to_csv(index=False, sep=';', encoding='utf-8-sig')
        except KeyError:
            csv_convidados = lista_convidados.to_csv(index=False, sep=';', encoding='utf-8-sig')
            
        st.download_button(
            label="📥 Exportar Convidados Extras", # Vender a alma valeu a pena, o botão está lindo.
            data=csv_convidados,
            file_name='checkin_convidados_multiplica.csv',
            mime='text/csv',
            use_container_width=True
        )

else:
    st.info("🔄 Inicializando sistemas... Aguardando conexão de dados da roleta.")