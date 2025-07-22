import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title = "Impera-Dashboard de Traduções")

st.title("📊 Dashboard de Análise de Traduções Impera")

@st.cache_data
def load_data():

    df = pd.read_excel("impera traduções totais.xlsx")
    
    df["Atribuição"] = pd.to_datetime(df["Atribuição"])
    df["Data de atribuição"] = df["Atribuição"].dt.date

    df = df.drop(columns={"Atribuição"})

    df["Data de atribuição"] = pd.to_datetime(df["Data de atribuição"])
    df["Mes"] = df["Data de atribuição"].dt.month

    return df

df = load_data()

st.sidebar.header("🔍 Filtros")

tip_doc = st.sidebar.multiselect(
    "📄 Tipo de Documento",
    options = df["Tipo de Documento"].unique(),
    default = df["Tipo de Documento"].unique()
)

data_rage = st.sidebar.date_input(
    "🗓️ Período das Solicitações",
    value=[df["Data de atribuição"].min(),df["Data de atribuição"].max()],
    min_value = df["Data de atribuição"].min(),
    max_value = df["Data de atribuição"].max()
)

df_filtred = df[
    (df["Tipo de Documento"].isin(tip_doc)) &
    (df["Data de atribuição"] >= pd.to_datetime(data_rage[0])) &
    (df["Data de atribuição"] <= pd.to_datetime(data_rage[1]))
]

df_filtred
st.subheader("📈 Principais Métricas")
col1,col2,col3 = st.columns(3)

col1.metric("Total de Traduções",df["Paginas"].sum())
col2.metric("Receita Total",f"R$ {df["VALOR"].sum():.0f}")
col3.metric("Preço Médio",f"R$ {df_filtred["VALOR"].mean():,.2f}")

tab1, tab2, tab3 = st.tabs(["📋 Dados", "📊 Distribuição das Traduções","💰 Receita"])

with tab1:
    st.subheader("🎲Dados completos🎲")
    st.dataframe(df_filtred.sort_values("Data de atribuição", ascending=False),
                 height=400,
                 column_config={
                     "VALOR": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f"),
                     "Data de atribuição": st.column_config.DateColumn("⏱ Data de Atribuição")
                 }
                 )
    
with tab2:
    st.subheader("Distribuição das traduções")

    doc_counts = df_filtred["Tipo de Documento"].value_counts().reset_index()
    fig_pie = px.pie(
        doc_counts,
        names = "Tipo de Documento",
        values="count",
        title="Distribuição por Tipo de Documento",
        hole=0.4,
        color_discrete_sequence = px.colors.qualitative.Dark24
    )
    fig_pie.update_traces(textposition="inside",textinfo="percent+label")
    st.plotly_chart(fig_pie,use_container_width=True)

    st.markdown("-----")
    st.subheader("🔍Tabela completa:")

    st.dataframe(
        doc_counts,
        use_container_width = True,
        column_config={
            "Tipo de Documento":"Tipo de Documento",
            "count":"Quantidade"
        },
        hide_index=True )
    
with tab3:
    st.subheader("$ Receita Mensal")

    receita_mensal = df.groupby("Mes")["VALOR"].sum().reset_index(name="Receita Mensal")
    
    fig_line = px.line(
        receita_mensal,
        x="Mes",
        y="Receita Mensal",
        title="Evolução da Receita Mensal",
        template = "plotly_dark",
        markers=True,
        labels={
            "Receita Mensal":"Receita (R$)",
            "Mes":"Mês"
        }
    )
    st.plotly_chart(fig_line,use_container_width=True)

    st.markdown("----")
    st.subheader("🔍Tabela Completa:")

    st.dataframe(
        receita_mensal,
        use_container_width=True,
        column_config={
            "Mes":"Mês",
            "Receita Mensal":"💰 Receita Mensal"
        },
        hide_index=True
    )