import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Dashboard de Traduções", layout="wide")
st.title("📊 Dashboard de Análise de Traduções")

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_excel("traduções_consolidadas.xlsx")
    
    # Limpeza e padronização
    df['Tipo de Documento'] = df['Tipo de Documento'].str.lower().str.strip()
    df['TIPO DE TRADUÇÃO'] = df['TIPO DE TRADUÇÃO'].str.lower().str.strip()
    
    # Mapeamento para padronizar tipos de documentos
    mapeamento = {
        'procura': 'procuração',
        'procuração ': 'procuração',
        'cert': 'certidão',
        'cert. italiana': 'certidão italiana',
        'cert. objeto e pé': 'certidão objeto e pé',
        'certidão': 'certidão',
        'escritura': 'escritura',
        'cnn': 'cnn',
        'adoção': 'adoção',
        'divorcio': 'divórcio',
        'rec. paternidade': 'reconhecimento de paternidade',
        'laudo médico': 'laudo médico'
    }
    
    df['Tipo de Documento'] = df['Tipo de Documento'].replace(mapeamento)
    
    # Extrair quantidade numérica
    df['Quantidade'] = df['Qtde. de documentos/laudas'].str.extract('(\d+)').astype(int)
    
    # Calcular tempo de processamento
    df['Data da solicitação'] = pd.to_datetime(df['Data da solicitação'])
    df['Data de finalização'] = pd.to_datetime(df['Data de finalização'])
    df['Tempo de processamento (dias)'] = (df['Data de finalização'] - df['Data da solicitação']).dt.days
    
    # Corrigir valores negativos (erros de digitação)
    df.loc[df['Tempo de processamento (dias)'] < 0, 'Tempo de processamento (dias)'] = 0
    
    return df

df = load_data()

# Sidebar com filtros
st.sidebar.header("🔍 Filtros")
tipo_doc = st.sidebar.multiselect(
    "Tipo de Documento",
    options=df['Tipo de Documento'].unique(),
    default=df['Tipo de Documento'].unique()
)

idioma = st.sidebar.multiselect(
    "Idioma",
    options=df['IDIOMA'].unique(),
    default=df['IDIOMA'].unique()
)

tipo_trad = st.sidebar.multiselect(
    "Tipo de Tradução",
    options=df['TIPO DE TRADUÇÃO'].unique(),
    default=df['TIPO DE TRADUÇÃO'].unique()
)

data_range = st.sidebar.date_input(
    "Período das solicitações",
    value=[df['Data da solicitação'].min(), df['Data da solicitação'].max()],
    min_value=df['Data da solicitação'].min(),
    max_value=df['Data da solicitação'].max()
)

# Aplicar filtros
df_filtered = df[
    (df['Tipo de Documento'].isin(tipo_doc)) &
    (df['IDIOMA'].isin(idioma)) &
    (df['TIPO DE TRADUÇÃO'].isin(tipo_trad)) &
    (df['Data da solicitação'] >= pd.to_datetime(data_range[0])) &
    (df['Data da solicitação'] <= pd.to_datetime(data_range[1]))
]

# Métricas principais
st.subheader("📈 Métricas Principais")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Traduções", len(df_filtered))
col2.metric("Receita Total", f"R$ {df_filtered['Valor Total'].sum():,.2f}")
col3.metric("Tempo Médio (dias)", f"{df_filtered['Tempo de processamento (dias)'].mean():.1f}")
col4.metric("Valor Médio", f"R$ {df_filtered['Valor Total'].mean():.2f}")

# Tabs para diferentes visualizações
tab1, tab2, tab3, tab4 = st.tabs(["📋 Dados", "⏱ Tempo", "📊 Distribuição", "💰 Receita"])

with tab1:
    st.subheader("Dados Completos")
    st.dataframe(df_filtered.sort_values('Data da solicitação', ascending=False), 
                height=400,
                column_config={
                    "Data da solicitação": st.column_config.DateColumn("Solicitação"),
                    "Data de finalização": st.column_config.DateColumn("Finalização"),
                    "Valor Total": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")
                })

with tab2:
    st.subheader("Análise de Tempo de Processamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_scatter = px.scatter(
            df_filtered,
            x='Data da solicitação',
            y='Tempo de processamento (dias)',
            color='Tipo de Documento',
            hover_data=['Código da Atividade', 'Quantidade'],
            title="Tempo de Processamento por Solicitação",
            labels={'Tempo de processamento (dias)': 'Dias', 'Data da solicitação': 'Data de Solicitação'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with col2:
        fig_box = px.box(
            df_filtered,
            x='Tipo de Documento',
            y='Tempo de processamento (dias)',
            color='TIPO DE TRADUÇÃO',
            title="Distribuição do Tempo por Tipo de Documento",
            labels={'Tempo de processamento (dias)': 'Dias', 'Tipo de Documento': 'Tipo de Documento'}
        )
        st.plotly_chart(fig_box, use_container_width=True)

with tab3:
    st.subheader("Distribuição das Traduções")
    
    col1, col2 = st.columns(2)
    
    with col1:
        doc_counts = df_filtered['Tipo de Documento'].value_counts().reset_index()
        fig_pie = px.pie(
            doc_counts,
            names='Tipo de Documento',
            values='count',
            title="Distribuição por Tipo de Documento",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Dark24
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_bar = px.bar(
            df_filtered.groupby(['IDIOMA', 'TIPO DE TRADUÇÃO']).size().reset_index(name='Count'),
            x='IDIOMA',
            y='Count',
            color='TIPO DE TRADUÇÃO',
            title="Distribuição por Idioma e Tipo de Tradução",
            barmode='group'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with tab4:
    st.subheader("Análise de Receita")
    
    col1, col2 = st.columns(2)
    
    with col1:
        receita_por_tipo = df_filtered.groupby('Tipo de Documento')['Valor Total'].sum().reset_index()
        fig_receita = px.bar(
            receita_por_tipo,
            x='Tipo de Documento',
            y='Valor Total',
            title="Receita por Tipo de Documento (R$)",
            color='Tipo de Documento',
            labels={'Valor Total': 'Receita (R$)'}
        )
        st.plotly_chart(fig_receita, use_container_width=True)
    
    with col2:
        receita_mensal = df_filtered.groupby(pd.Grouper(key='Data da solicitação', freq='M'))['Valor Total'].sum().reset_index()
        fig_trend = px.line(
            receita_mensal,
            x='Data da solicitação',
            y='Valor Total',
            title="Receita Mensal (R$)",
            markers=True,
            labels={'Valor Total': 'Receita (R$)', 'Data da solicitação': 'Mês'}
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# Análise adicional
st.subheader("🔍 Análise Detalhada")
col1, col2 = st.columns(2)

with col1:
    st.write("**Top 5 Documentos Mais Frequentes**")
    st.dataframe(df_filtered['Tipo de Documento'].value_counts().head(5).reset_index(),
                hide_index=True,
                column_config={
                    "Tipo de Documento": "Documento",
                    "count": "Quantidade"
                })

with col2:
    st.write("**Documentos com Maior Tempo de Processamento**")
    st.dataframe(df_filtered.nlargest(5, 'Tempo de processamento (dias)')[['Código da Atividade', 'Tipo de Documento', 'Tempo de processamento (dias)']],
                hide_index=True,
                column_config={
                    "Tempo de processamento (dias)": "Dias"
                })

# Rodapé
st.markdown("---")
st.caption("Dashboard desenvolvido com Streamlit, Pandas e Plotly Express | Dados atualizados em " + datetime.now().strftime("%d/%m/%Y %H:%M"))