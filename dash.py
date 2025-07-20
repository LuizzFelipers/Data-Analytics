import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(layout='wide')
#titulo da page one
st.title("📊Dashboard de Análise de Tradução")

# Adicionando um tema dark
def apply_dark_theme():
    st.markdown("""
    <style>
        /* Tema dark geral */
        .main {
            background-color: #0e1117;
            color: #ffffff;
        }
        
        /* Tabelas dark */
        .stDataFrame, .stTable {
            background-color: #000 !important;
            color: white !important;
        }
        
        /* Cabeçalhos */
        h1, h2, h3, h4, h5, h6 {
            color: #1e00ff !important;
            text-shadow: 0 0 5px #1e00ff, 0 0 10px #1e00ff;
        }
        
        /* Abas */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 10px 20px;
            background-color: #1a1d24;
            border-radius: 10px 10px 0px 0px;
            color: #a0a0a0;
            border: 1px solid #333;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1a1d24;
            color: #00f2ff !important;
            border-bottom: 2px solid #00f2ff;
            box-shadow: 0 0 10px #00f2ff;
        }
        
        /* KPIs */
        .stMetric {
            background-color: #1a1d24;
            border: 1px solid #333;
            border-radius: 10px;
            padding: 15px;
        }
        
        .stMetric label {
            color: #a0a0a0 !important;
        }
        
        .stMetric div {
            color: #00f2ff !important;
            font-size: 24px !important;
            text-shadow: 0 0 5px #00f2ff;
        }
    </style>
    """, unsafe_allow_html=True)

apply_dark_theme()

def create_neon_plot(fig):
    fig.update_layout(
        plot_bgcolor='rgba(14, 17, 23, 1)',
        paper_bgcolor='rgba(14, 17, 23, 1)',
        font_color='white',
        xaxis=dict(
            gridcolor='rgba(50, 50, 50, 0.5)',
            linecolor='rgba(50, 50, 50, 0.5)'
        ),
        yaxis=dict(
            gridcolor='rgba(50, 50, 50, 0.5)',
            linecolor='rgba(50, 50, 50, 0.5)'
        ),
        legend=dict(
            bgcolor='rgba(14, 17, 23, 0.7)'
        )
    )
    return fig

# carregar e tratar os dados:

df = pd.read_excel("traduções_consolidadas.xlsx")
df = df.drop(columns={"Unnamed: 0","Código da Atividade"})

df["Data da solicitação"] = pd.to_datetime(df["Data da solicitação"])
df["Data de finalização"] = pd.to_datetime(df['Data de finalização'])

df["Tempo de processamento"] = (df['Data de finalização']-df['Data da solicitação'])

df['Tempo de processamento'] = pd.to_timedelta(df['Tempo de processamento']).dt.days
tempo_medio_processamento = df.groupby('Tipo de Documento')['Tempo de processamento'].mean().reset_index(name='tempo em dias')

tempo_medio_processamento['tempo em dias'] = tempo_medio_processamento['tempo em dias'].astype(int)
tempo_medio = tempo_medio_processamento['tempo em dias'].mean()
# Calculando a Receita Total

df['Ano'] = df['Data de finalização'].dt.year
df['Mes'] = df['Data de finalização'].dt.month
df['Mes-Ano'] = df['Data de finalização'].dt.to_period('M').astype(str)

receita_mensal = df.groupby(['Ano', 'Mes', 'Mes-Ano'])['Valor Total'].sum().reset_index()

receita_mensal = receita_mensal.drop([0,1,2,3,4,5,6,7,8,9,10,11,18])
media_receita = receita_mensal['Valor Total'].sum()
#Preço médio

preco_medio = df['Valor unitário'].mean()

fig_receita_mensal = px.line(
    receita_mensal,
    x="Mes",
    y='Valor Total',
    template='plotly_dark',
    title='Crescimento da Receita Mensal(R$)',
    labels={"Mes":"Meses","Valor Total":"Receita Total (R$)"},
    markers=True,
    color_discrete_sequence=['#00f2ff'],
    
)

fig_receita_mensal.update_layout(
    title_font=dict(size=24, color='#00f2ff', family="Arial Black"),
    annotations=[
        dict(
            
            text="Dados em tempo real",
            xref="paper", yref="paper",
            x=0.85, y=1.1,
            showarrow=False,
            font=dict(size=12, color="#00f2ff"))
    ]
)

# st.subheader(f"""📈 Receita Total: R$ {media_receita:,.2f} |
#              💰 Preço Médio: R$ {preco_medio:,.2f} |
#              ⏱️ Tempo Médio: {tempo_medio:.0f} dias
#              """)

def formatar_brl(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📈Receita Total", f"R$ {formatar_brl(media_receita)}")
    
with col2:
    st.metric("💰Preço Médio", f"R$ {formatar_brl(preco_medio)}")
    
with col3:
    st.metric("⏱️Tempo Médio", f"{tempo_medio:.0f} dias")
    
st.write("Análise consolidada dos serviços de tradução realizados")

central_bar = st.container()

with central_bar:
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Receita Total", 
        "⏱️ Tempo de Processamento", 
        "📄 Documentos Mais Traduzidos", 
        "% Percentual na Receita"
    ])

    with tab1:
         col1, col2 = st.columns(2)

         with col1:
              st.subheader("Tabela de Distribuição da Receita")
              st.dataframe(receita_mensal[["Mes","Valor Total"]].sort_values("Valor Total",ascending=False)

                           )
              
         with col2:
              st.subheader("Distribuição da Receita Mensal")
              fig_receita_mensal = px.line(
                   receita_mensal,
                   title="Receita Mensal",
                   x="Mes",
                   y="Valor Total",
                   color_discrete_sequence=['#00f2ff'],
                   markers=True)
              fig_receita_mensal = create_neon_plot(fig_receita_mensal)
              st.plotly_chart(fig_receita_mensal, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)

    # CSS customizado para a tabela no tema dark
    st.markdown("""
    <style>
        .stDataFrame th {
            background-color: #1E1E1E !important;
            color: white !important;
        }
        .stDataFrame td {
            background-color: #0E1117 !important;
            color: white !important;
        }
        .stDataFrame {
            background-color: #0E1117 !important;
        }
    </style>
    """, unsafe_allow_html=True)

    with col1:
        st.subheader("Tempo de Processamento")
        # Tabela com estilo dark aplicado
        st.dataframe(
            tempo_medio_processamento[["Tipo de Documento", "tempo em dias"]]
            .sort_values("tempo em dias",ascending=False)
            .style
            .set_properties(**{
                'background-color': '#0E1117',
                'color': 'white',
                'border-color': '#1E1E1E'
            })
            .set_table_styles([{
                'selector': 'th',
                'props': [('background-color', '#1E1E1E'), ('color', 'white')]
            }])
        )

    with col2:
        st.subheader("Distribuição do Tempo")
        fig_tempo_medio = px.scatter(
            tempo_medio_processamento,
            x='Tipo de Documento',
            y='tempo em dias',
            color='Tipo de Documento',
            template='plotly_dark',
            title='Tempo médio de processamento de cada tipo de documento',
            color_discrete_sequence=['#00f2ff', '#ff00a0', '#00ff47', '#ffeb3b', '#9c27b0'],
            size='tempo em dias',
            hover_name='Tipo de Documento'
        )
        fig_tempo_medio = create_neon_plot(fig_tempo_medio)
        st.plotly_chart(fig_tempo_medio, use_container_width=True)

tipo_documento_mais_traduzido = df['Tipo de Documento'].value_counts().reset_index(name="Quantidade")

with tab3:
     col1, col2 = st.columns(2)
     with col1:
        st.subheader("Documentos mais Traduzidos")
        st.dataframe(df['Tipo de Documento'].value_counts().reset_index(name="Quantidade"))
     #Criando uma lista para destacar a maior fatia
     maior_categoria = tipo_documento_mais_traduzido.loc[tipo_documento_mais_traduzido["Quantidade"].idxmax(), "Tipo de Documento"]
     pull_list = [0.1 if doc == maior_categoria else 0 for doc in tipo_documento_mais_traduzido["Tipo de Documento"]]

     with col2:
         fig_tipo_documento = px.pie(
    tipo_documento_mais_traduzido,
    names="Tipo de Documento",
    values="Quantidade",
    title= "Distribuição dos Documentos mais Traduzidos",
    color='Tipo de Documento',
    template='plotly_dark',
    hole=0.5,
    color_discrete_sequence=px.colors.sequential.Plasma)
         fig_tipo_documento.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
        plot_bgcolor='rgba(0,0,0,0)',   # Área do gráfico transparente
        font=dict(color='white'),       # Cor do texto branca
        title_font=dict(color='white'), # Cor do título branca
        legend=dict(
            font=dict(color='white'),   # Cor da legenda branca
            bgcolor='rgba(0,0,0,0)'     # Fundo da legenda transparente
        )
    )
         fig_tipo_documento.update_traces(
            pull=pull_list,  # Destaca apenas a maior fatia
            textinfo="percent+label",  # Mostra % e nome da categoria
            textfont_size=12,
            marker=dict(line=dict(color="white", width=2)),  # Borda branca
            hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}")
         st.plotly_chart(fig_tipo_documento, use_container_width=True)


with tab4:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("$ Receita total dos documentos")
        st.dataframe(df.groupby('Tipo de Documento')['Valor Total'].sum().reset_index(name='valor total'))
        receita_documento = df.groupby('Tipo de Documento')['Valor Total'].sum().reset_index(name='valor total')
        receita_total = df["Valor Total"].sum()
        receita_documento['Percentual da participação na Receita Total'] = (receita_documento['valor total'] / receita_total) * 100
        receita_documento['Percentual formatado'] = receita_documento['Percentual da participação na Receita Total'].round(2).astype(str) + '%'

    with col2:
        st.subheader("% Distribuição")
        max_value = receita_documento['valor total'].max()
        pull_list = [0.1 if val == max_value else 0 for val in receita_documento['valor total']]

        fig_receita_documento = px.pie(
    receita_documento,
    names='Tipo de Documento',
    values='valor total',  # Usar o valor absoluto, não o percentual formatado
    color='Tipo de Documento',
    color_discrete_sequence=px.colors.sequential.Plasma,
    template="plotly_dark",
    title="Percentual da participação dos tipos de documento na receita total",
    hole=0.5,  # Para efeito de donut
    labels={'valor total': 'Valor Total'},
    hover_data=['Percentual formatado']  # Mostra o percentual formatado no hover
)

# Ajustes finais de layout
        fig_receita_documento.update_traces(
            pull=pull_list,
            textposition='inside',
            textinfo='percent+label',
            insidetextorientation='radial',
            textfont_size=14,
            textfont_color='white',
            marker=dict(line=dict(color='white', width=2)
                        )
        )

        fig_receita_documento.update_layout(
            font=dict(size=12, color='white'),
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05
            ),
            margin=dict(l=50, r=50, b=50, t=80)
        )
        fig_receita_documento = create_neon_plot(fig_receita_documento)
        st.plotly_chart(fig_receita_documento, use_container_width=True)

    