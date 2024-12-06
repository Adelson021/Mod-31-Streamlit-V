# Importações necessárias
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO

# Configuração inicial da página
st.set_page_config(
    page_title='RFV - Segmentação com Clusters',
    layout="wide",
    initial_sidebar_state='expanded'
)

# Funções auxiliares
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

# Função Principal
def main():
    # Título e descrição
    st.title("RFV - Segmentação com Clusters")
    st.markdown("""
    **Recência, Frequência e Valor** são métricas fundamentais para segmentar clientes. 
    Aqui, utilizamos essas métricas para criar clusters e identificar perfis de clientes.
    """)

    st.sidebar.header("📥 Upload de Dados")
    data_file = st.sidebar.file_uploader("Envie um arquivo CSV", type=['csv'])

    if data_file:
        df = pd.read_csv(data_file)
        st.subheader("📊 Dados Carregados")
        st.dataframe(df.head())

        # Verificação de colunas obrigatórias
        colunas_necessarias = ['ID_cliente', 'Recencia', 'Frequencia', 'Valor']
        if not all(col in df.columns for col in colunas_necessarias):
            st.error(f"As colunas obrigatórias são: {', '.join(colunas_necessarias)}")
            st.stop()

        # Seleção do número de clusters
        st.sidebar.header("🔢 Configuração de Clusterização")
        n_clusters = st.sidebar.slider(
            "Escolha a quantidade de clusters",
            min_value=2,
            max_value=10,
            value=4,
            step=1
        )

        # Escalando as variáveis RFV
        scaler = StandardScaler()
        rfv_scaled = scaler.fit_transform(df[['Recencia', 'Frequencia', 'Valor']])

        # Aplicação do KMeans
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        df['Cluster'] = kmeans.fit_predict(rfv_scaled)

        # Silhouette Score
        silhouette_avg = silhouette_score(rfv_scaled, df['Cluster'])
        st.sidebar.metric(label="Silhouette Score", value=f"{silhouette_avg:.2f}")

        # Exibição dos clusters
        st.subheader("📋 Dados Segmentados")
        st.dataframe(df)

        # Gráfico de dispersão
        st.subheader("📈 Visualização dos Clusters")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.scatterplot(
            data=df,
            x='Frequencia', 
            y='Valor',
            hue='Cluster', 
            palette='viridis', 
            ax=ax
        )
        ax.set_title("Clusters com base em Frequência e Valor")
        st.pyplot(fig)

        # Baixar resultados
        st.download_button(
            label="🔽 Baixar Tabela com Clusters (CSV)",
            data=convert_df(df),
            file_name="clientes_segmentados_rfv.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
