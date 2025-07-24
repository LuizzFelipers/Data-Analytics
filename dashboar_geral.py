import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Dashboard Geral",layout='wide')
st.title("Análise Geral das Empresas de Tradução")


caminho_impera = 'C:/Users/luiz.silva/Desktop/TRADUCOES/impera/impera traduções totais.xlsx'
caminho_fatto = "C:/Users/luiz.silva/Desktop/TRADUCOES/fatto traducoes/traducoes_FATTO_ALL.xlsx"
caminho_bv = "C:/Users/luiz.silva/Desktop/TRADUCOES/traduções_consolidadas_BV.xlsx"
    
df_impera = pd.read_excel(caminho_impera)
df_fatto = pd.read_excel(caminho_fatto)
df_bv = pd.read_excel(caminho_bv)
    
dfs = [df_impera,df_bv,df_fatto]

#Calculando os Tipos de Documentos mais traduzidos

documentos_traduzidos_impera = df_impera["Tipo de Documento"].value_counts().reset_index(name="Quantidade")

documentos_traduzidos_fatto = df_fatto["Tipo de Documento"].value_counts().reset_index(name="Quantidade")

#Arrumando a coluna do df_bv

df_bv["Tipo de Documento"] = df_bv["Tipo de Documento"].str.lower()
mapeamento = {
    'procura': 'procuração',
    "procu":"procuração",
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

df_bv['Tipo de Documento'] = df_bv['Tipo de Documento'].replace(mapeamento)
df_bv.to_excel("bv_traducoes_corrigida.xlsx",index=False)
documentos_traduzidos_bv = df_bv["Tipo de Documento"].value_counts().reset_index(name="Quantidade")

st.sidebar.header("🔍 Filtros")

df_geral = pd.read_excel("TRADUÇÕES_GERAIS.xlsx")
df_geral["Data de finalização"] = pd.to_datetime(df_geral["Data de finalização"])

empresas_disponiveis = df_geral["Empresa de tradução"].unique()
empresas_selecionadas = st.sidebar.multiselect(
        "Selecione as empresas",
        options=empresas_disponiveis,
        default=empresas_disponiveis
    )

tipos_doc_disponiveis = df_geral["Tipo de Documento"].unique()
tipo_doc = st.sidebar.multiselect(
    "📄 Selecione o Tipo de Documento",
    options = tipos_doc_disponiveis,
    default=tipos_doc_disponiveis
)

min_date = df_geral["Data de finalização"].min().date()
max_date = df_geral["Data de finalização"].max().date()

st.write(datetime.today())

data_inicio = st.sidebar.date_input(
    "Data Inicial",
    min_date,
    min_value=min_date,
    max_value=max_date
)

data_fim = st.sidebar.date_input(
    "Data final",
    max_date,
    min_value=min_date,
    max_value=max_date
)

df_filtrado = df_geral[
    (df_geral["Empresa de tradução"].isin(empresas_selecionadas)) &
    (df_geral["Tipo de Documento"].isin(tipo_doc)) &
    (df_geral["Data de finalização"].dt.date >= data_inicio) &
    (df_geral["Data de finalização"].dt.date <= data_fim)
]

tab1, tab2, tab3, tab4 = st.tabs(["📈 Receita",
                                 "⏱ Tempo Médio", 
                                 "📑 Tipos de Documento",
                                   "💲 Receita por Tipo"])

df_geral["Qtde. de documentos/laudas"] = df_geral['Qtde. de documentos/laudas'].astype(str).str.replace(r'\D','',regex=True).astype(int)

with tab1:
    st.header("Análise de Receita")
    col1, col2 = st.columns(2)

    with col1:
        receita_total = df_geral['Valor Total'].sum()
        st.metric("Receita Total", "R$ 659.220,00")

        fig_receita_empresa = px.bar(
            df_geral.groupby("Empresa de tradução")["Valor Total"].sum().reset_index(),
            x="Empresa de tradução",
            y="Valor Total",
            title="Receita por Empresa",
            labels={"Valor Total":"Receita (R$)","Empresa de tradução":"Empresas"}
        )
        st.plotly_chart(fig_receita_empresa, use_container_width=True)
    with col2:
        receita_media_pag = (df_geral['Valor Total'].sum()/df_geral["Qtde. de documentos/laudas"].sum())
        
        st.metric("Valor Médio por Página", f"R$ 43,17")

        df_receita_tempo = df_geral.groupby(pd.Grouper(key="Data de finalização",freq="M"))['Valor Total'].sum().reset_index()
        
        fig_receita_tempo = px.line(
                                    df_receita_tempo,
                                    x="Data de finalização",
                                    y="Valor Total",
                                    title="Receita por Mês",
                                    labels={"Valor_Total":"Receita (R$)","Data_Finalizado":"Mês"})
        st.plotly_chart(fig_receita_tempo,use_container_width=True)

with tab2:
    st.header("Análise do Tempo de Processamento")
    df_geral["Tempo de processamento"] = df_geral["Data de finalização"] - df_geral["Data da solicitação"] 
    df_geral["Tempo de processamento em dias"] = df_geral["Tempo de processamento"].dt.days
    df_geral = df_geral[df_geral['Tempo de processamento em dias'] >= 0]
    t = df_geral["Tempo de processamento em dias"].mean()
    st.metric("Tempo Médio de Processamento", f"{t:.0f}")

    fig_pie_tempo = px.bar(
        df_geral.groupby("Empresa de tradução")["Tempo de processamento em dias"].mean().reset_index(name="média de dias"),
        x="Empresa de tradução",
        y="média de dias",
        title="Distribuição do tempo de processamento por Empresa(dias)",
        color={"#060270":"BV TRADUÇÕES","#018E94":"FATTO"},
        labels={"Empresa de tradução":"Empresa",
             "média de dias":"Dias"}

        )
    st.plotly_chart(fig_pie_tempo,use_container_width=True)

    st.markdown("-----")
    st.markdown("OBS: a empresa de tradução: **IMPERA** não tem informação sobre a Data de Solicitação. Logo, não foi possível encontrar o **Tempo de processamento por documento.**")


with tab3:
    df_filtrado["Qtde. de documentos/laudas"] = df_filtrado['Qtde. de documentos/laudas'].astype(str).str.replace(r'\D','',regex=True).astype(int)
    st.header("Análise dos Tipos de Documentos")
    st.metric("Total de Documentos Traduzidos",15.272)
    col1, col2 = st.columns(2)
    with col1:
        fig_documentos = px.pie(
                                df_filtrado.groupby("Tipo de Documento")["Qtde. de documentos/laudas"].sum().sort_values(ascending=False).reset_index(name="Quantidade Traduzidas").head(),
                                names="Tipo de Documento",
                                values="Quantidade Traduzidas",
                                hole=0.4,
                                title="Distribuição dos Tipos de Documentos mais Traduzidos",
                                labels={"Tipos de Documentos":"Documentos",
                                        "Quantidade traduzidas":"Quantidade de Traduções"},
                                color=["#1A1A2E", "#16213E", "#0F3460", "#533E85","#3D2C8D"]
                                        )
        st.plotly_chart(fig_documentos,use_container_width=True)

    with col2:
        st.subheader("**Top 5** Tipo de Documentos mais Traduzidos")
        st.dataframe(df_filtrado.groupby("Tipo de Documento")["Qtde. de documentos/laudas"].sum().sort_values(ascending=False).reset_index(name="Quantidade Traduzidas").head())

with tab4:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 das Receitas por Tipo de Documento")
        receita_por_tipo = df_filtrado.groupby("Tipo de Documento")["Valor Total"].sum().reset_index(name="Receita Total (R$)").sort_values("Receita Total (R$)",ascending=False)
        receita_formatada = receita_por_tipo.copy()
        receita_formatada["Receita Total (R$)"] = receita_formatada["Receita Total (R$)"].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        
        st.dataframe(receita_formatada.reset_index(drop=True).head(5))

    with col2:
        fig_bar_receita = px.bar(
            receita_por_tipo.sort_values("Receita Total (R$)",ascending=False).head(),
            x="Tipo de Documento",
            y="Receita Total (R$)",
            title="Distribuição da Receita por Tipo de Documento",
            labels={"Tipo de Documento":"Documento",
                    "Receita Total (R$)":"Receita (R$)"},
            color={"#2C3E50":"Certidão",
                    "#34495E":"Certidão de Divórcio",
                    "#5D6D7E":"Nascimento",
                    "#4A235A":"Casamento",
                    "#1B2631":"CNN"}
        )
        st.plotly_chart(fig_bar_receita,use_container_width=True)

