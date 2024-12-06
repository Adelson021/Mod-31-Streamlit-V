# Importações necessárias
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns

# Configuração inicial da página
st.set_page_config(
    page_title='RFV - Segmentação de Clientes',
    layout="wide",
    initial_sidebar_state='expanded'
)

# Funções de Cache para otimizar o desempenho
@st.cache_data
def convert_df(df):
    """Converte o DataFrame para CSV."""
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def to_excel(df):
    """Converte o DataFrame para Excel."""
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='RFV_Segmentado')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# Funções para Classificação de Quartis
def recencia_class(x, r, q_dict):
    """Classifica a Recência (menor é melhor)."""
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'

def freq_val_class(x, fv, q_dict):
    """Classifica Frequência e Valor (maior é melhor)."""
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'

# Função Principal da Aplicação
def main():
    # Título e Descrição
    st.title("RFV - Segmentação de Clientes")
    st.write(""" 
    **RFV (Recência, Frequência, Valor)** é uma técnica utilizada para segmentação de clientes com base no comportamento 
    de compras. Isso permite ações de marketing e CRM mais direcionadas, ajudando na personalização do conteúdo e 
    na retenção de clientes.
    """)
    st.markdown("---")

    # Upload do Arquivo
    st.sidebar.header("📥 Envie seu arquivo de dados")
    data_file = st.sidebar.file_uploader("Escolha um arquivo CSV ou Excel", type=['csv', 'xlsx'])

    if data_file:
        # Tentativa de Leitura do Arquivo
        try:
            if data_file.name.endswith('.csv'):
                df_compras = pd.read_csv(data_file, parse_dates=['DiaCompra'], infer_datetime_format=True)
            else:
                df_compras = pd.read_excel(data_file, parse_dates=['DiaCompra'], infer_datetime_format=True)
        except Exception as e:
            st.error(f"⚠️ Erro ao carregar o arquivo: {e}")
            st.stop()

        # Verificação de Colunas Necessárias
        colunas_necessarias = ['ID_cliente', 'DiaCompra', 'CodigoCompra', 'ValorTotal']
        if not all(col in df_compras.columns for col in colunas_necessarias):
            st.error(f"⚠️ O arquivo deve conter as seguintes colunas: {', '.join(colunas_necessarias)}")
            st.stop()

        # Cálculo da Recência
        dia_atual = df_compras['DiaCompra'].max()
        df_recencia = df_compras.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
        df_recencia['Recencia'] = (dia_atual - df_recencia['DiaCompra']).dt.days
        df_recencia.drop(columns=['DiaCompra'], inplace=True)

        # Cálculo da Frequência
        df_frequencia = df_compras.groupby('ID_cliente', as_index=False)['CodigoCompra'].nunique()
        df_frequencia.columns = ['ID_cliente', 'Frequencia']

        # Cálculo do Valor
        df_valor = df_compras.groupby('ID_cliente', as_index=False)['ValorTotal'].sum()
        df_valor.columns = ['ID_cliente', 'Valor']

        # Merge das Componentes RFV
        df_RFV = df_recencia.merge(df_frequencia, on='ID_cliente').merge(df_valor, on='ID_cliente')

        # Cálculo dos Quartis
        quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])

        # Aplicação das Funções de Classificação
        df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class, args=('Recencia', quartis))
        df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class, args=('Frequencia', quartis))
        df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class, args=('Valor', quartis))
        df_RFV['RFV_Score'] = df_RFV['R_quartil'] + df_RFV['F_quartil'] + df_RFV['V_quartil']

        # Normalização dos Dados para Clusterização
        scaler = StandardScaler()
        rfv_normalizado = scaler.fit_transform(df_RFV[['Recencia', 'Frequencia', 'Valor']])

        # Aplicação do K-Means com 4 Clusters
        kmeans = KMeans(n_clusters=4, random_state=42)
        df_RFV['Cluster'] = kmeans.fit_predict(rfv_normalizado)

        # Nomeando os Clusters com Base nos Perfis
        dict_clusters = {
            0: "Clientes mais frequentes e com alto gasto, mas com recência moderada.",
            1: "Clientes com pouca frequência, alto gasto e alta recência.",
            2: "Clientes de baixo gasto, com alta recência.",
            3: "Clientes com baixo gasto e baixa frequência."
        }
        df_RFV['Perfil_Cluster'] = df_RFV['Cluster'].map(dict_clusters)

        # Visualização dos Clusters
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            x=df_RFV['Recencia'], y=df_RFV['Valor'], hue=df_RFV['Cluster'], palette='viridis', ax=ax
        )
        ax.set_title('Clusters de Clientes com Base em RFV', fontsize=16)
        st.pyplot(fig)

        # Download dos Resultados
        st.download_button(
            label="🔽 Baixar Tabela RFV com Clusters em Excel",
            data=to_excel(df_RFV),
            file_name="clientes_segmentados_rfv_clusters.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()