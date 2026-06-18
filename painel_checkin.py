import streamlit as st
import pandas as pd
import re
import plotly.graph_objects as go

# ==========================================
# 1. CONFIGURAÇÕES DA PÁGINA
# ==========================================
st.set_page_config(page_title="Multiplica do Futuro - Check-in", layout="wide")
st.title("🚀 Painel de Recepção - Multiplica do Futuro")

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
        # DB 1: Lista base oficial de inscritos
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
        
        # Remove duplicatas na base oficial (caso a equipe tenha mandado lista suja)
        df_inscritos = df_inscritos.drop_duplicates(subset=['CPF_LIMPO'], keep='first')
        total_inscritos_base = len(df_inscritos)
        
        # DB 2: Respostas em tempo real do Forms
        df_checkin = pd.read_csv(URL_FORMS)
        df_checkin['CPF_LIMPO'] = df_checkin['Qual é seu CPF?'].apply(limpar_cpf)
        
        # HIGIENIZAÇÃO: Padroniza os nomes (ex: JOÃO -> João) e remove check-ins duplicados do mesmo CPF
        df_checkin['Qual é seu nome completo?'] = df_checkin['Qual é seu nome completo?'].str.title()
        df_checkin = df_checkin.drop_duplicates(subset=['CPF_LIMPO'], keep='first')
        
        # ORDENAÇÃO: Garante que os mais recentes fiquem no topo da tabela
        df_checkin = df_checkin.sort_values(by='Carimbo de data/hora', ascending=False)
        
        # PIPELINE DE CRUZAMENTO
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
    # Filtros lógicos das listagens
    lista_presenca = df_total[df_total['Status'] == True]
    lista_convidados = df_total[df_total['Status'] == False]
    
    # Cálculo das métricas para o gráfico
    qtd_presentes = len(lista_presenca)
    qtd_convidados = len(lista_convidados)
    qtd_ausentes = max(0, total_inscritos - qtd_presentes)
    
    # Barra de Progresso do Evento (Termômetro)
    if total_inscritos > 0:
        pct_lotação = min(qtd_presentes / total_inscritos, 1.0)
        st.progress(pct_lotação, text=f"📊 **Termômetro do Evento:** {int(pct_lotação * 100)}% dos inscritos já chegaram!")
    
    st.markdown("---")
    
    # Grid Superior: Métricas + Gráfico
    col_metrics, col_chart = st.columns([1, 1])
    
    with col_metrics:
        st.write("") # Espaçador nativo (Substitui o antigo <br> que causava erro no Cloud)
        st.write("") 
        st.metric("Total de Inscritos na Base Oficial (DB1)", total_inscritos)
        st.metric("Pessoas Físicas que passaram pela roleta", len(df_total))
        st.metric("✅ Presentes (Inscritos Oficiais)", qtd_presentes)
        st.metric("⚠️ Convidados / Extra", qtd_convidados)
    
    with col_chart:
        # Construção do Gráfico Donut (Plotly)
        labels = ['Inscritos Presentes', 'Inscritos Ausentes', 'Convidados Extras']
        valores = [qtd_presentes, qtd_ausentes, qtd_convidados]
        cores = ['#2ecc71', '#e74c3c', '#f1c40f']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=valores, 
            hole=.5,
            marker=dict(colors=cores),
            textinfo='value+percent'
        )])
        
        fig.update_layout(
            title_text="Visão Geral do Fluxo do Evento",
            annotations=[dict(text='Público', x=0.5, y=0.5, font_size=20, showarrow=False)],
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
            margin=dict(t=40, b=40, l=10, r=10),
            height=320
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("---")
    
    # Tabelas de Visualização em Tempo Real
    col_esquerda, col_direita = st.columns(2)
    colunas_exibicao = ['Carimbo de data/hora', 'Qual é seu nome completo?', 'Qual é seu CPF?']
    
    with col_esquerda:
        st.subheader(f"✅ Lista de Presença ({qtd_presentes})")
        st.caption("Últimos check-ins aparecem no topo")
        try:
            # hide_index=True remove aquela coluna de números inúteis do lado esquerdo
            st.dataframe(lista_presenca[colunas_exibicao], use_container_width=True, hide_index=True)
        except KeyError:
            st.dataframe(lista_presenca, use_container_width=True, hide_index=True)
        
    with col_direita:
        st.subheader(f"⚠️ Convidados ({qtd_convidados})")
        st.caption("Pessoas não encontradas na base oficial")
        try:
            st.dataframe(lista_convidados[colunas_exibicao], use_container_width=True, hide_index=True)
        except KeyError:
            st.dataframe(lista_convidados, use_container_width=True, hide_index=True)
        
    # Botão de atualização manual
    st.write("")
    if st.button("🔄 Atualizar Painel Agora"):
        st.cache_data.clear()
        st.rerun()
else:
    st.info("🔄 Conectando com o banco de dados... Aguardando os primeiros check-ins.")