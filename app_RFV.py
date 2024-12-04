# Importações necessárias
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

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
    
    **Componentes RFV:**
    - **Recência (R):** Quantidade de dias desde a última compra.
    - **Frequência (F):** Quantidade total de compras no período.
    - **Valor (V):** Total de dinheiro gasto nas compras do período.
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

        # Exibição de Prévia dos Dados
        st.subheader("📊 Prévia dos Dados Carregados")
        st.dataframe(df_compras.head())

        # Cálculo da Recência
        st.write('## 📅 Recência (R)')
        dia_atual = df_compras['DiaCompra'].max()
        st.write(f'Data Atual Considerada: **{dia_atual.date()}**')
        df_recencia = df_compras.groupby('ID_cliente', as_index=False)['DiaCompra'].max()
        df_recencia['Recencia'] = (dia_atual - df_recencia['DiaCompra']).dt.days
        df_recencia.drop(columns=['DiaCompra'], inplace=True)
        st.write('### Recência por Cliente')
        st.dataframe(df_recencia.head())

        # Cálculo da Frequência
        st.write('## 📈 Frequência (F)')
        df_frequencia = df_compras.groupby('ID_cliente', as_index=False)['CodigoCompra'].nunique()
        df_frequencia.columns = ['ID_cliente', 'Frequencia']
        st.write('### Frequência de Compras por Cliente')
        st.dataframe(df_frequencia.head())

        # Cálculo do Valor
        st.write('## 💰 Valor (V)')
        df_valor = df_compras.groupby('ID_cliente', as_index=False)['ValorTotal'].sum()
        df_valor.columns = ['ID_cliente', 'Valor']
        st.write('### Valor Total Gasto por Cliente')
        st.dataframe(df_valor.head())

        # Merge das Componentes RFV
        df_RFV = df_recencia.merge(df_frequencia, on='ID_cliente').merge(df_valor, on='ID_cliente')
        st.write('## 📋 Tabela RFV Final')
        st.dataframe(df_RFV.head())

        # Cálculo dos Quartis
        quartis = df_RFV.quantile(q=[0.25, 0.5, 0.75])
        st.write('## 📊 Quartis para RFV')
        st.dataframe(quartis)

        # Aplicação das Funções de Classificação
        df_RFV['R_quartil'] = df_RFV['Recencia'].apply(recencia_class, args=('Recencia', quartis))
        df_RFV['F_quartil'] = df_RFV['Frequencia'].apply(freq_val_class, args=('Frequencia', quartis))
        df_RFV['V_quartil'] = df_RFV['Valor'].apply(freq_val_class, args=('Valor', quartis))
        df_RFV['RFV_Score'] = df_RFV['R_quartil'] + df_RFV['F_quartil'] + df_RFV['V_quartil']
        st.write('## 🏷️ Tabela Segmentada RFV')
        st.dataframe(df_RFV.head())

        # Contagem de Clientes por Score RFV
        st.write('## 📊 Quantidade de Clientes por RFV Score')
        st.bar_chart(df_RFV['RFV_Score'].value_counts())

        # Clientes de Destaque
        st.write('### 🌟 Clientes com Melhor Segmento (AAA)')
        clientes_top = df_RFV[df_RFV['RFV_Score'] == 'AAA'].sort_values('Valor', ascending=False)
        st.dataframe(clientes_top.head(10))

        # Ações de Marketing por Segmento
        st.write('## 📢 Ações de Marketing/CRM por Segmento')
        dict_acoes = {
            'AAA': 'Enviar cupons de desconto e amostras grátis.',
            'AAB': 'Enviar ofertas especiais para manter o engajamento.',
            'AAC': 'Enviar conteúdos personalizados para fidelização.',
            'ABA': 'Realizar campanhas de reativação.',
            'ABB': 'Monitorar clientes com potencial de churn.',
            'ABC': 'Oferecer incentivos para aumentar a frequência.',
            'BAA': 'Realizar pesquisas de satisfação.',
            'BAD': 'Implementar estratégias de retenção.',
            'DDD': 'Clientes inativos, sem ações planejadas.'
            # Adicione mais mapeamentos conforme necessário
        }
        df_RFV['Ações de Marketing'] = df_RFV['RFV_Score'].map(dict_acoes).fillna('Ação padrão para segmentos não definidos.')
        # Corrigir o erro no rename e aplicar a contagem corretamente
        contagem_segmentos = df_RFV[['RFV_Score', 'Ações de Marketing']].value_counts().reset_index(name='Contagem')
        contagem_segmentos.columns = ['RFV_Score', 'Ações de Marketing', 'Contagem']
        st.dataframe(contagem_segmentos)

        # Download dos Resultados
        st.download_button(
            label="🔽 Baixar Tabela RFV em Excel",
            data=to_excel(df_RFV),
            file_name="clientes_segmentados_rfv.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.download_button(
            label="🔽 Baixar Tabela RFV em CSV",
            data=convert_df(df_RFV),
            file_name="clientes_segmentados_rfv.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
