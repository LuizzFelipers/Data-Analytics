import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime


st.set_page_config(page_title="FATTO - Dashboard de Traduções ")

st.title("📊 Dashboard de Análise de Traduções FATTO")

#carregar dados
@st.cache_data
def load_data():
    #Ler dados
    df = pd.read_excel("traducoes_FATTO_ALL.xlsx")
    #Padroniza os dados strings
    df['Tipo de Documento'] = df['Tipo de Documento'].str.lower().str.strip()
    df['TIPO DE TRADUÇÃO'] = df['TIPO DE TRADUÇÃO'].str.lower().str.strip()

    #tratando os dados de data
    df['Data da solicitação'] = pd.to_datetime(df['Data da solicitação'])
    df['Data da finalização'] = pd.to_datetime(df['Data da finalização'])
    df['Tempo de processamento (dias)'] = (df['Data da finalização'] - df['Data da solicitação']).dt.days 
    
    df.loc[df['Tempo de processamento (dias)'] < 0, 'Tempo de processamento (dias)'] = 0
    
    return df

df = load_data()

df

#Criando filtros
st.sidebar.header("🔍 Filtros")

#tipo de documento
tipo_doc = st.sidebar.multiselect(
    "Tipo de Documento",
    options=df['Tipo de Documento'].unique(),
    default=df['Tipo de Documento'].unique()
)

idioma = st.sidebar.multiselect(
    "IDIOMA",
    options=df['IDIOMA'].unique(),
    default=df['IDIOMA'].unique()
)

tipo_trad = st.sidebar.multiselect(
    "Tipo de Tradução",
    options=df['TIPO DE TRADUÇÃO'].unique(),
    default=df['TIPO DE TRADUÇÃO'].unique()
)

data_range = st.sidebar.date_input(
    'Período das solicitações',
    value=[df['Data da solicitação'].min(),df['Data da solicitação'].max()],
    min_value=df['Data da solicitação'].min(),
    max_value=df['Data da solicitação'].max()
)
#Aplicar os filtros
df_filtred = df[
    (df['Tipo de Documento'].isin(tipo_doc)) &
    (df['IDIOMA'].isin(idioma)) &
    (df['TIPO DE TRADUÇÃO'].isin(tipo_trad)) &
    (df['Data da solicitação'] >= pd.to_datetime(data_range[0])) &
    (df['Data da solicitação'] <= pd.to_datetime(data_range[1]))
]


#Métricas principais:

st.subheader("📈 Principais Métricas")
col1,col2,col3,col4 = st.columns(4)

col1.metric("Total de Traduções",df['Quantidade de laudos'].sum())
col2.metric("Receita Total",f"R$ {df_filtred["Valor total"].sum():,.0f}")
col3.metric("Tempo Médio (dias)", f"{df_filtred['Tempo de processamento (dias)'].mean():.0f}")
col4.metric("Valor Médio", f"R$ {df_filtred['Valor total'].mean():.2f}")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Dados","⏱ Tempo", "📊 Distribuição das Traduções","💰 Receita"])

with tab1:
    st.subheader("🎲Dados completos🎲")
    st.dataframe(df_filtred.sort_values("Data da solicitação", ascending=False),
                 height=400,
                 column_config={
                     "Data da solicitação": st.column_config.DateColumn("Solicitação"),
                     "Data da finalização": st.column_config.DateColumn("Finalização"),
                     "Valor Total": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f")
                 })
    
with tab2:
    st.subheader("Análise de Tempo de Processamento")

    tempo_processamento = df.drop(columns={"TIPO DE TRADUÇÃO","Quantidade de laudos","Preço unitário",'Valor total','IDIOMA','Data da solicitação','Data da finalização'})
    tempo_processamento['Tipo de Documento'] = tempo_processamento['Tipo de Documento'].str.lower()

    mapeamento = {
    'procuracao':'procuração'
    }

    tempo_processamento['Tipo de Documento'] = tempo_processamento['Tipo de Documento'].replace(mapeamento)
    tempo_processamento = tempo_processamento.groupby('Tipo de Documento')['Tempo de processamento (dias)'].mean().sort_values(ascending=False).reset_index(name="Tempo médio em dias")
    tempo_processamento['Tempo médio em dias'] = round(tempo_processamento['Tempo médio em dias'],0)

    fig_scatter = px.scatter(
        tempo_processamento,
        x="Tipo de Documento",
        y="Tempo médio em dias",
        color="Tipo de Documento",
        title="tempo médio de processamento",
        template="plotly_dark",
        width=800,
        height=500
    )

    fig_scatter.update_layout(
    autosize=True,
    margin=dict(l=20, r=20, t=40, b=20),
    height=500
    )
    
    st.plotly_chart(fig_scatter,use_container_width=True)
    
    st.markdown('----')
    
    st.subheader("🔍Tabela completa:")
    
    st.dataframe(
        tempo_processamento,
        use_container_width=True,
        height=400,  # Altura da tabela
        column_config={
            "Tipo de Documento": "Tipo de Documento",
            "Tempo médio em dias": st.column_config.NumberColumn(
                "Tempo Médio (dias)",
                format="%.0f dias"
            ),
            "TIPO DE TRADUÇÃO": "Tipo de Tradução"
        },
        hide_index=True
    )    

with tab3:

    st.subheader("Distribuição das Traduções")


    doc_counts = df_filtred['Tipo de Documento'].value_counts().reset_index()
    fig_pie = px.pie(
        doc_counts,
        names='Tipo de Documento',
        values='count',
        title='Distribuição por Tipo de Documento',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    fig_pie.update_traces(textposition = 'inside',textinfo='percent+label')
    st.plotly_chart(fig_pie,use_container_width=True)

    st.markdown('-------')

    st.subheader("🔍Tabela completa:") 

    st.dataframe(
        doc_counts,
        use_container_width=True,
        height=400,
        column_config={
            "Tipo de Documento":"Tipo de Documento",
            "Count":"Quantidade"
        },
        hide_index=True
    )

with tab4:
    st.subheader("$ Receita Mensal")

    df["Mes"] = df["Data da finalização"].dt.month
    receita_mensal = df.groupby("Mes")["Valor total"].sum().reset_index(name="Receita Mensal")
    receita_mensal = receita_mensal.drop([5])
    fig_line = px.line(
        receita_mensal,
        x="Mes",
        y="Receita Mensal",
        title="Evolução da Receita Mensal",
        template="plotly_dark",
        markers=True,
        labels={
            'Receita Mensal':'Receita (R$)',
            'Mes':'Mês'
        }
    )
    st.plotly_chart(fig_line,use_container_width=True)

    st.dataframe(receita_mensal,
                 use_container_width=True,
                 
                 column_config={
                     'Mes':'Mês',
                     "Receita Mensal":"Receita"
                 },
                 hide_index=True
                 )


st.subheader("🔍 Análise Detalhada")
col1, col2 = st.columns(2)

with col1:
    st.write("**Top 5 Documentos Mais Frequentes**")
    st.dataframe(
        df_filtred['Tipo de Documento'].value_counts().head(5).reset_index(),
        hide_index=True,
        column_config={
        "Tipo de Documento":"Documento",
        "count":"Quantidade"}
        )

with col2:
    fig_barras = px.bar(
        df_filtred['Tipo de Documento'].value_counts().head(5).reset_index(),
        x="Tipo de Documento",
        y="count",
        title="Gráfico dos TOP 5 Documentos mais frequentes",
        color = "Tipo de Documento",
        color_discrete_sequence=px.colors.qualitative.Dark24
    )
    st.plotly_chart(fig_barras,use_container_width=True)