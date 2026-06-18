import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURAÇÕES DA PÁGINA & BRANDING (FRONT-END EXTREME)
# ==========================================
st.set_page_config(page_title="Multiplica do Futuro - Check-in", page_icon="🚀", layout="wide")

# CSS Customizado (Tema Dark Institucional - Renapsi Vibe + Animações)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;800&display=swap');

    /* Fundo da tela principal */
    .stApp {
        background-color: #0B0E14; 
    }
    
    /* Título Principal */
    .main-title {
        font-family: 'Poppins', sans-serif;
        color: #FFFFFF;
        text-align: center;
        font-size: 3.2rem;
        font-weight: 800;
        margin-bottom: 0px;
        padding-bottom: 0px;
        letter-spacing: -1px;
        text-shadow: 0px 4px 20px rgba(74, 144, 226, 0.4);
    }
    
    /* Subtítulo */
    .sub-title {
        font-family: 'Poppins', sans-serif;
        color: #4A90E2; 
        text-align: center;
        font-size: 1.2rem;
        font-weight: 600;
        margin-top: -5px;
        margin-bottom: 40px;
        letter-spacing: 3px;
        text-transform: uppercase;
    }
    
    /* Cards de Métricas Customizados - Base */
    .metric-card {
        background: linear-gradient(145deg, #161925, #11141D);
        border-radius: 16px;
        padding: 25px 20px;
        text-align: center;
        border-bottom: 4px solid #4A90E2;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        margin-bottom: 15px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    
    /* Hover Effects dos Cards (A mágica acontece aqui) */
    .metric-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 30px rgba(74, 144, 226, 0.2);
    }
    
    .metric-card.success { border-bottom-color: #2ECC71; }
    .metric-card.success:hover { box-shadow: 0 15px 30px rgba(46, 204, 113, 0.2); }
    
    .metric-card.warning { border-bottom-color: #F39C12; }
    .metric-card.warning:hover { box-shadow: 0 15px 30px rgba(243, 156, 18, 0.2); }
    
    /* Tipografia dos Cards */
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        line-height: 1.1;
    }
    
    .metric-label {
        font-family: 'Poppins', sans-serif;
        font-size: 0.95rem;
        color: #8B9BB4;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
        margin: 10px 0 0 0;
    }

    /* Hack para animar os botões nativos do Streamlit */
    div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {
        transition: all 0.3s ease !important;
        border-radius: 10px !important;
        border: 1px solid rgba(74, 144, 226, 0.5) !important;
        font-family: 'Poppins', sans-serif !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stButton"] button:hover, div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 20px rgba(74, 144, 226, 0.3) !important;
        border-color: #4A90E2 !important;
        color: #4A90E2 !important;
    }
</style>
""", unsafe_allow_html=True)

# Header Estilizado
st.markdown("<h1 class='main-title'>Painel de Recepção</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='sub-title'>🚀 Multiplica do Futuro - Demà Renapsi</h3>", unsafe_allow_html=True)

# ID capturado da planilha oficial de respostas do evento
SHEET_ID = "1JLBii5KIj6SzkZF7T2Lgr-Bc9nMMbtf1haygbn6w-lw"
URL_FORMS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

def limpar_cpf(cpf):
    """Remove pontos, traços e espaços de um CPF."""
    if pd.isna(cpf):
        return ""
    return re.sub(r'\D', '', str(cpf)).zfill(11)

# ==========================================
# 2. MOTOR DE DADOS (PIPELINE)
# ==========================================
@st.cache_data(ttl=10) # Atualiza a cada 10 segundos automaticamente
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

if 'Status' in df_total.columns:
    lista_presenca = df_total[df_total['Status'] == True]
    lista_convidados = df_total[df_total['Status'] == False] 
    
    qtd_presentes = len(lista_presenca)
    qtd_convidados = len(lista_convidados)
    qtd_ausentes = max(0, total_inscritos - qtd_presentes)
    
    # Barra de Progresso Customizada
    if total_inscritos > 0:
        pct_lotação = min(qtd_presentes / total_inscritos, 1.0)
        st.progress(pct_lotação, text=f"📊 TERMÔMETRO DO EVENTO: {int(pct_lotação * 100)}% dos inscritos oficiais já chegaram")
    
    st.write("")
    
    # Grid Superior: Cards HTML Animados + Gráfico
    col_metrics, col_chart = st.columns([1.2, 1])
    
    with col_metrics:
        st.write("")
        st.markdown(f"""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <div class="metric-card" style="flex: 1;">
                    <p class="metric-value">{total_inscritos}</p>
                    <p class="metric-label">Total Base (DB1)</p>
                </div>
                <div class="metric-card" style="flex: 1;">
                    <p class="metric-value">{len(df_total)}</p>
                    <p class="metric-label">Check-ins Totais</p>
                </div>
            </div>
            <div style="display: flex; gap: 20px;">
                <div class="metric-card success" style="flex: 1;">
                    <p class="metric-value" style="color: #2ECC71;">{qtd_presentes}</p>
                    <p class="metric-label">✅ Presentes</p>
                </div>
                <div class="metric-card warning" style="flex: 1;">
                    <p class="metric-value" style="color: #F39C12;">{qtd_convidados}</p>
                    <p class="metric-label">⚠️ Convidados</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col_chart:
        # Paleta de Cores Cyber-Dark
        labels = ['Inscritos Presentes', 'Inscritos Ausentes', 'Convidados Extras']
        valores = [qtd_presentes, qtd_ausentes, qtd_convidados]
        cores = ['#2ECC71', '#2C3545', '#F39C12'] # Verde Neon, Azul/Cinza Profundo, Laranja Neon
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=valores, 
            hole=.65,
            marker=dict(colors=cores, line=dict(color='#0B0E14', width=3)), # Bordas mais grossas combinando com o fundo
            textinfo='percent',
            textfont=dict(color='white', size=15, family='Poppins')
        )])
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=[dict(text='STATUS', x=0.5, y=0.5, font_size=18, font_family='Poppins', font_color='#8B9BB4', showarrow=False)],
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5, font=dict(color='#FFFFFF', family='Poppins')),
            margin=dict(t=10, b=10, l=10, r=10),
            height=300
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("---")
    
    # Tabelas de Visualização
    col_esquerda, col_direita = st.columns(2)
    colunas_exibicao = ['Carimbo de data/hora', 'Qual é seu nome completo?', 'Qual é seu CPF?']
    
    with col_esquerda:
        st.markdown(f"<h3 style='color: #2ECC71; font-family: Poppins;'>✅ Lista de Presença ({qtd_presentes})</h3>", unsafe_allow_html=True)
        st.caption("Últimos check-ins aparecem no topo")
        try:
            st.dataframe(lista_presenca[colunas_exibicao], use_container_width=True, hide_index=True)
        except KeyError:
            st.dataframe(lista_presenca, use_container_width=True, hide_index=True) # #OdiamosJava
        
    with col_direita:
        st.markdown(f"<h3 style='color: #F39C12; font-family: Poppins;'>⚠️ Convidados ({qtd_convidados})</h3>", unsafe_allow_html=True)
        st.caption("Pessoas não encontradas na base oficial")
        try:
            st.dataframe(lista_convidados[colunas_exibicao], use_container_width=True, hide_index=True)
        except KeyError:
            st.dataframe(lista_convidados, use_container_width=True, hide_index=True)
        
    # ==========================================
    # 4. PAINEL DE CONTROLE (BOTÕES)
    # ==========================================
    st.markdown("---")
    
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("🔄 Atualizar Painel Agora", use_container_width=True):
            st.cache_data.clear() 
            st.rerun()
            
    with col_btn2:
        try:
            csv_presenca = lista_presenca[colunas_exibicao].to_csv(index=False, sep=';', encoding='utf-8-sig')
        except KeyError:
            csv_presenca = lista_presenca.to_csv(index=False, sep=';', encoding='utf-8-sig')
            
        st.download_button(
            label="📥 Baixar Lista de Presença", 
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
            label="📥 Baixar Convidados Extras", 
            data=csv_convidados,
            file_name='checkin_convidados_multiplica.csv',
            mime='text/csv',
            use_container_width=True
        )

else:
    st.info("🔄 Conectando com o banco de dados... Aguardando os primeiros check-ins.")