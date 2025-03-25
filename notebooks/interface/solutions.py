### Interface para o modelo

## Instruções para uso local e remoto
## Aqui deixaremos brevemente um passo a passo para que você usuário seja capaz de executar o código.

# # Instruções para uso no VSCode
## 1. Coloque os arquivos CSV dentro da pasta "data" desse notebook
## 2. No notebook, a célula seguinte à essa contém as leituras dos arquivos CSV com o caminho do drive do criador desse notebook.
## 3. Comente as linhas que fazem referência aos arquivos locais e descomente as linhas que fazem referência ao Google Drive. Por exemplo:


## 4. Certifique-se de que os arquivos CSV estejam localizados no diretório correto em seu ambiente. Por exemplo, se você tiver uma pasta chamada "data" no mesmo diretório do python, coloque os arquivos CSV nessa pasta e ajuste seus nomes. 
## - Possivelmente os arquivos vão seguir o seguinte padrão, mesmo no seu drive:
##    tabela_Meta = pd.read_csv("./Github/2024-2A-T12-IN03-G03/notebooks/data/dados_tratados/BASE INTELI_META-limpo.csv"")

## 5. Para fazer a instalação das bibliotecas exigidas, basta abrir o terminal integrado e inserir o seguinte:
# -  pip install pandas streamlit matplotlib scikit-learn

## 6. Agora, para rodar a aplicação, digite no terminal:
# -   streamlit run solutions.py

## Pronto! A sua aplicação já está no ar e você poderá rodar ela no seu dispositivo local.


# # Instruções para uso no Google Colab
# 1.Abrir o Google Colab:
#    - Acesse o [Google Colab](https://colab.research.google.com/) e faça login com sua conta Google.

# 2.Upload do arquivo Python:
#    - No menu superior esquerdo, clique em **Arquivo > Fazer upload do notebook** e selecione o arquivo `.py` que deseja rodar. Ou, você pode copiar e colar o código Python diretamente em uma célula de código no Google Colab.

# 3. Upload dos arquivos CSV:
#    - Clique no ícone de **Arquivos** à esquerda e faça o upload dos arquivos CSV necessários (como `BASE INTELI_META-limpo.csv`).
#    - Alternativamente, para usar arquivos do seu Google Drive, rode o seguinte código em uma célula do Colab para montar o Drive:
#      ```python
#      from google.colab import drive
#      drive.mount('/content/drive')
#      ```
#      Isso permitirá que você acesse os arquivos que estão armazenados no seu Google Drive.

# 4. Ajuste os caminhos dos arquivos CSV:
#    - Caso esteja usando arquivos armazenados no Google Drive, ajuste o caminho para algo como:
#      ```python
#      tabela_Meta = pd.read_csv("/content/drive/My Drive/seu_caminho/BASE INTELI_META-limpo.csv")
#      ```
#    - Se fez o upload diretamente no Colab, você pode usar o caminho padrão:
#      ```python
#      tabela_Meta = pd.read_csv("/content/BASE INTELI_META-limpo.csv")
#      ```

# 5. Instalação das bibliotecas:
#    - Caso precise instalar bibliotecas que não estão instaladas no ambiente do Colab, use:
#      ```python
#      !pip install pandas streamlit matplotlib scikit-learn
#      ```

# 6. Rodar a aplicação Streamlit no Colab:
#    - O Google Colab não oferece suporte nativo para Streamlit diretamente, mas você pode fazer um teste simples para visualizar a saída do código. Para rodar localmente em um ambiente real com Streamlit, siga as instruções de uso local.
#    - Caso queira rodar tudo no Colab (exceto a parte do Streamlit), execute normalmente as células do código.

# 7. Executar o código:
#    - Com tudo configurado, rode o código no Colab como faria normalmente em um notebook Jupyter.


import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


# Função para carregar e processar os dados
@st.cache_data
def load_data():
    tabela_Meta = pd.read_csv("C:/Users/Inteli/OneDrive - Etec Centro Paula Souza/Documents/Inteli/Semestre 2/Mod3/Github/2024-2A-T12-IN03-G03/notebooks/data/dados_tratados/BASE INTELI_META-limpo.csv")
    tabela_Agosto = pd.read_csv("C:/Users/Inteli/OneDrive - Etec Centro Paula Souza/Documents/Inteli/Semestre 2/Mod3/Github/2024-2A-T12-IN03-G03/notebooks/data/dados_tratados/tratada_BaseDados_ProjetoINTELI_RG_01_AGOSTO_2024.csv")

    # Pré-processamento
    ipca_padrao = tabela_Agosto.groupby(['Ano', 'Mês'])['IPCA ES'].first().reset_index()
    tabela_agosto_segmento = tabela_Agosto.groupby(['Ano', 'Mês', 'Veiculo', 'Origem', 'Segmento']).agg({
        'Vl Liquido Final': 'sum',
    }).reset_index()
    tabela_agosto_segmento = tabela_agosto_segmento.merge(ipca_padrao, on=['Ano', 'Mês'], how='left')

    categorical_columns = ['Origem', 'Veiculo', 'Segmento']
    X = tabela_agosto_segmento.drop('Vl Liquido Final', axis=1)
    y = tabela_agosto_segmento['Vl Liquido Final']

    # Aplicando OneHotEncoder
    onehot_encoder = OneHotEncoder(drop='first', sparse_output=False)
    X_encoded = onehot_encoder.fit_transform(X[categorical_columns])
    X_encoded_df = pd.DataFrame(X_encoded, columns=onehot_encoder.get_feature_names_out(categorical_columns))
    X = X.drop(categorical_columns, axis=1)
    X = pd.concat([X.reset_index(drop=True), X_encoded_df.reset_index(drop=True)], axis=1)

    # Divisão dos dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Treinamento do modelo
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=10)  # Ajuste de parâmetros
    rf_model.fit(X_train, y_train)

    return rf_model, onehot_encoder, tabela_Agosto, categorical_columns, X.columns, X_test, y_test

# Modifique o código da previsão para remover a transformação logarítmica
def main():
    st.title("Gazetech Solutions")
    st.text("Previsão de Valor Líquido Final")
    
    rf_model, onehot_encoder, tabela_Agosto, categorical_columns, feature_names, X_test, y_test = load_data()

    # Coleta de entrada do usuário
    st.sidebar.header("Escolha os parâmetros de entrada")
    anos_disponiveis = sorted(tabela_Agosto['Ano'].unique()) + [2025, 2026]
    ano = st.sidebar.selectbox("Ano", options=anos_disponiveis)
    veiculo = st.sidebar.selectbox("Veículo", options=["Todos"] + sorted(tabela_Agosto['Veiculo'].unique()))

    # Filtrando as opções de Origem
    origem_disponiveis = sorted(tabela_Agosto['Origem'].unique())
    origem_disponiveis = [origem for origem in origem_disponiveis if origem not in ['MP - MÍDIA PROGRAMÁTICA', 'RN - MERCADO NACIONAL']]
    origem = st.sidebar.selectbox("Origem", options=["Todos"] + origem_disponiveis)

    segmento = st.sidebar.selectbox("Segmento", options=["Todos"] + sorted(tabela_Agosto['Segmento'].unique()))

    if veiculo == "Todos":
        veiculo = tabela_Agosto['Veiculo'].unique()
    else:
        veiculo = [veiculo]

    if origem == "Todos":
        origem = tabela_Agosto['Origem'].unique()
    else:
        origem = [origem]

    if segmento == "Todos":
        segmento = tabela_Agosto['Segmento'].unique()
    else:
        segmento = [segmento]

    input_data = pd.DataFrame({
        "Ano": [ano],
        "Veiculo": [veiculo[0]],
        "Origem": [origem[0]],
        "Segmento": [segmento[0]],
    })

    input_encoded = onehot_encoder.transform(input_data[categorical_columns])
    input_encoded_df = pd.DataFrame(input_encoded, columns=onehot_encoder.get_feature_names_out(categorical_columns))

    input_df = pd.DataFrame({
        "Ano": [ano],
    })

    input_df = pd.concat([input_df.reset_index(drop=True), input_encoded_df.reset_index(drop=True)], axis=1)

    for col in feature_names:
        if col not in input_df.columns:
            input_df[col] = 0

    input_df = input_df[feature_names]

    # Modifique a geração do gráfico para remover os valores reais a partir de 2025
    if st.button("Prever"):
        predicted_value = rf_model.predict(input_df)
        st.success(f"Valor Líquido Final Previsto: R$ {predicted_value[0]:.2f}")

        y_test_pred = rf_model.predict(X_test)

        # Filtrar os valores reais para anos anteriores a 2025
        anos_teste = X_test['Ano']
        meses_teste = X_test['Mês']
        mask_ate_2024 = anos_teste < 2025
        y_test_filtrado = y_test[mask_ate_2024]
        y_test_pred_filtrado = y_test_pred[mask_ate_2024]
        meses_filtrados = meses_teste[mask_ate_2024]

        # Criar uma lista de meses de 1 a 12
        meses_do_ano = list(range(1, 13))

        fig, ax = plt.subplots()

        # Agrupar os valores previstos por mês
        ax.plot(meses_do_ano, y_test_pred_filtrado[:12], label='Valor Previsto', color='orange', marker='x')

        # Garantir que o eixo X mostre todos os meses (1 a 12)
        ax.set_xticks(meses_do_ano)
        ax.set_xticklabels(['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'])

        ax.set_title('Comparação entre Valores Reais e Previsto por Mês')
        ax.set_xlabel('Meses do Ano')
        ax.set_ylabel('Valor Líquido Final (R$)')
        ax.legend()
        st.pyplot(fig)

if __name__ == "__main__":
    main()
