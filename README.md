# 📊 RFV - Segmentação de Clientes

Este projeto permite segmentar clientes com base na técnica **RFV (Recência, Frequência, Valor)** utilizando uma interface interativa construída com [Streamlit](https://streamlit.io/).

## 🚀 Sobre o Projeto

A segmentação RFV é uma poderosa ferramenta de marketing que analisa o comportamento de compra dos clientes, permitindo direcionar ações específicas para diferentes perfis de consumo.

### Componentes da Análise RFV:

- **Recência (R)**: Quantidade de dias desde a última compra (quanto menor, melhor).
- **Frequência (F)**: Número total de compras realizadas (quanto maior, melhor).
- **Valor (V)**: Valor total gasto em compras (quanto maior, melhor).

## 🛠 Funcionalidades

- Upload de arquivos `.csv` ou `.xlsx` contendo dados de compra dos clientes.
- Cálculo automático dos indicadores RFV para cada cliente.
- Segmentação dos clientes com base em quartis (A-D).
- Visualização dos dados em tabelas e gráficos.
- Sugestões de ações de marketing com base no score RFV.
- Exportação dos dados segmentados em Excel ou CSV.

## 📂 Estrutura Esperada do Arquivo

O arquivo de entrada deve conter obrigatoriamente as seguintes colunas:

| Coluna         | Descrição                                     |
|----------------|-----------------------------------------------|
| `ID_cliente`   | Identificador único do cliente                |
| `DiaCompra`    | Data da compra (formato de data reconhecível)|
| `CodigoCompra` | Código identificador da compra                |
| `ValorTotal`   | Valor total gasto na compra                   |

## 📸 Demonstração

RFV
https://mod-31-streamlit-vs.onrender.com

RFV com clusterização
https://mod-31-streamlit-v.onrender.com/

## 📦 Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/nome-do-repositorio.git
cd nome-do-repositorio
```

2. Crie um ambiente virtual e ative:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Execute a aplicação:

```bash
streamlit run app.py
```

## 🧾 Exemplo de `requirements.txt`

```text
streamlit
pandas
numpy
xlsxwriter
```

## 📤 Exportação

Após o processamento, você poderá fazer download dos dados segmentados nos formatos:

- `.xlsx` (Excel)
- `.csv`

## 🎯 Exemplos de Ações de Marketing

| Score RFV | Ação Recomendada                                 |
|-----------|--------------------------------------------------|
| AAA       | Enviar cupons de desconto e amostras grátis      |
| AAB       | Ofertas especiais para manter engajamento        |
| ABC       | Oferecer incentivos para aumentar a frequência   |
| DDD       | Clientes inativos – sem ações planejadas         |
| ...       | Adapte conforme necessário                       |

## 📌 Observações

- Os dados de data devem estar em formato reconhecido (`YYYY-MM-DD`, por exemplo).
- A aplicação utiliza cache para melhorar o desempenho ao processar os dados.
- O score RFV é construído por letras, indo de **A (melhor)** a **D (pior)** para cada dimensão (R, F, V).

## 🧑‍💻 Autor

**Adelson** – Cientista de Dados  
[LinkedIn](https://linkedin.com/in/adelson21)  
[GitHub](https://github.com/Adelson021)




