# Importações necessárias
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
from io import BytesIO

# Configuração inicial da página
st.set_page_config(
    page_title='RFV - Segmentação de Clientes',
    layout="wide",
    initial_sidebar_state='expanded'
)

# Funções de Cache
@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

@st.cache_data
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='RFV_Segmentado')
    writer.close()
    return output.getvalue()

# Funções para Classificação
def recencia_class(x, r, q_dict):
    if x <= q_dict[r][0.25]:
        return 'A'
    elif x <= q_dict[r][0.50]:
        return 'B'
    elif x <= q_dict[r][0.75]:
        return 'C'
    else:
        return 'D'

def freq_val_class(x, fv, q_dict):
    if x <= q_dict[fv][0.25]:
        return 'D'
    elif x <= q_dict[fv][0.50]:
        return 'C'
    elif x <= q_dict[fv][0.75]:
        return 'B'
    else:
        return 'A'

# Função Principal
def main():
    st.title("RFV - Segmentação de Clientes")
    st.write("""
    **RFV (Recência, Frequência, Valor)** é uma técnica para segmentação de clientes com base no comportamento de compras.
    """)
    st.markdown("---")
    
    # Upload do Arquivo
    st.sidebar.header("📥 Envie seu arquivo de dados")
    data_file = st.sidebar.file_uploader("Escolha um arquivo CSV ou Excel", type=['csv', 'xlsx'])

    if data_file:
        try:
            if data_file.name.endswith('.csv'):
                df_compras = pd.read_csv(data_file, parse_dates=['DiaCompra'], infer_datetime_format=True)
            else:
                df_compras = pd.read_excel(data_file, parse_dates=['DiaCompra'], infer_datetime_format=True)
        except Exception as e:
            st.error(f"⚠️ Erro ao carregar o arquivo: {e}")
            st.stop()

        colunas_necessarias = ['ID_cliente', 'DiaCompra', 'CodigoCompra', 'ValorTotal']
        if not all(col in df_compras.columns for col in colunas_necessarias):
            st.error(f"⚠️ O arquivo deve conter as colunas: {', '.join(colunas_necessarias)}")
            st.stop()

        st.subheader("📊 Prévia dos Dados Carregados")
        st.dataframe(df_compras.head())

        # Recência
        dia_atual = df_compras['DiaCompra'].max()
        df_recencia = df_compras.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
        df_recencia['Recencia'] = (dia_atual - df_recencia['DiaCompra']).dt.days
        df_recencia.drop(columns=['DiaCompra'], inplace=True)

        # Frequência
        df_frequencia = df_compras.groupby('ID_cliente', as_index=False)['CodigoCompra'].nunique()
        df_frequencia.columns = ['ID_cliente', 'Frequencia']

        # Valor
        df_valor = df_compras.groupby('ID_cliente', as_index=False)['ValorTotal'].sum()
        df_valor.columns = ['ID_cliente', 'Valor']

        # Merge das Componentes RFV
        df_RFV = df_recencia.merge(df_frequencia, on='ID_cliente').merge(df_valor, on='ID_cliente')

        # Quartis e Classificação
        quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])
        df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class, args=('Recencia', quartis))
        df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class, args=('Frequencia', quartis))
        df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class, args=('Valor', quartis))
        df_RFV['RFV_Score'] = df_RFV['R_quartil'] + df_RFV['F_quartil'] + df_RFV['V_quartil']

        # Escolha da Quantidade de Clusters
        st.sidebar.header("🔢 Configuração de Clusterização")
        n_clusters = st.sidebar.slider(
            "Escolha a quantidade de clusters",
            min_value=2,
            max_value=10,
            value=4,
            step=1
        )

        # Clusterização
        scaler = StandardScaler()
        rfv_scaled = scaler.fit_transform(df_RFV[['Recencia', 'Frequencia', 'Valor']])
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df_RFV['Cluster'] = kmeans.fit_predict(rfv_scaled)

        # Descrição dos Clusters
        st.subheader("📋 Tabela RFV com Clusterização")
        st.dataframe(df_RFV.head())

        st.write('### 📊 Resumo dos Clusters RFV')
        cluster_summary = df_RFV.groupby('Cluster')[['Recencia', 'Frequencia', 'Valor']].mean()
        st.dataframe(cluster_summary)

        st.write('### 📈 Visualização dos Clusters RFV')
        plt.figure(figsize=(10, 6))
        for cluster in range(n_clusters):
            plt.scatter(
                rfv_scaled[df_RFV['Cluster'] == cluster, 0],
                rfv_scaled[df_RFV['Cluster'] == cluster, 1],
                label=f'Cluster {cluster}'
            )
        plt.xlabel('Recência (Normalizada)')
        plt.ylabel('Frequência (Normalizada)')
        plt.title(f'Clusters RFV ({n_clusters} grupos)')
        plt.legend()
        st.pyplot(plt)

        st.download_button(
            label="🔽 Baixar Tabela RFV Segmentada",
            data=to_excel(df_RFV),
            file_name="clientes_segmentados_rfv.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()


