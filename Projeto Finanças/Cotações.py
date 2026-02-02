# Importação das Bibliotecas 
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import timedelta
# python -m streamlit run cotações.py 

st.set_page_config(
    page_title="Performance das Ações",
    page_icon="📊",
    layout="wide",
)


#Criar as funções de carregamentos de dados 
    #Base da dados 
#implentanção de chache para otimizar os dados do streamlit(otimização e velociade para os dados)
@st.cache_data
def carregar_dados(empresas):
    texto_tickers = " ".join(empresas)#funão de listas, juntando os vales
    dados_acao = yf.Tickers(texto_tickers)
    cotacoes_acao = dados_acao.history(start="2023-01-01", end="2024-12-26") #data pode ser alterada
    #print(cotacoes_acao)
    cotacoes_acao = cotacoes_acao["Close"]
    return cotacoes_acao

@st.cache_data
def carregar_tickers_acoes():
    base_tickers = pd.read_csv("IBOV.csv", sep=";") #usando o parametro ";" para o codigo entender o parametro da tabela, pois o Pandas lê tabelas somente com ","
    tickers = list (base_tickers["Código"])
    tickers = [item + ".SA" for item in tickers]
    return tickers
   


acoes = carregar_tickers_acoes()
dados = carregar_dados(acoes)

#Criação da Interface da Streamlit  
st.write("""
# Análise e Visualização de Ações
O gráfico abaixo representa a evolução do preço das ações ao longo dos anos        
         """)  #markdown

#Preparação das Vizualizações = Filtros
st.sidebar.header("Filtros")

#Filtro de ações
lista_acoes = st.sidebar.multiselect(("Escolha as ações para visalizar"), dados.columns)
if lista_acoes:
    dados = dados[lista_acoes]
    if len(lista_acoes) == 1:
       acao_unica = lista_acoes[0]
       dados = dados.rename(columns={acao_unica:"Close"})     
       
#Filtro de Datas
data_inicial = dados.index.min().to_pydatetime()#pydatetime resolve o problema do tabela pandas
data_final = dados.index.max().to_pydatetime()#pydatetime resolve o problema do tabela pandas
        
intervalo_data = st.sidebar.slider("Selecione o período desejado", 
                                   min_value=data_inicial,
                                   max_value=data_final,
                                   value=(data_inicial, data_final),
                                   step=timedelta(days=1),  format="DD/MM/YY") #pode ser alterado conforme a nescidade do avanço nas datas  st.sidebar


dados = dados.loc[intervalo_data[0]:intervalo_data[1]]   


    


#criar o Grafico 
st.line_chart(dados)

#calculo de performance

texto_performance_ativos = ""

if len(lista_acoes)==0:
    lista_acoes = list(dados.columns)
elif len(lista_acoes)==1:
     dados = dados.rename(columns={"Close" :acao_unica})
     
carteira = [1000 for acao in lista_acoes]
total_inicial_carteira = sum(carteira)  

for i, acao in enumerate (lista_acoes):
    performance_ativo = dados[acao].iloc[-1] / dados[acao].iloc[0] - 1 #iloc permite localizar o valor dentro de uma tabela no pandas
    performance_ativo = float(performance_ativo)
    
    carteira[i] = carteira[i] *(1 + performance_ativo )
    
    if performance_ativo > 0:
        #:cor[texto]
       texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :green[{performance_ativo:.1%}]"
    elif performance_ativo < 0:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :red[{performance_ativo:.1%}]"
    else:
        texto_performance_ativos = texto_performance_ativos + f"  \n{acao}: :blue[{performance_ativo:.1%}]"

total_final_carteira = sum(carteira)
performance_carteira = total_final_carteira / total_inicial_carteira - 1


if performance_carteira > 0:
    #:cor[texto]
    texto_performance_carteira =  f" Perfomance da carteira com todos os ativos: :green[{performance_ativo:.1%}]"
elif performance_ativo < 0:
    texto_performance_carteira =  f" Perfomance da carteira com todos os ativos: :red[{performance_ativo:.1%}]"
else:
    texto_performance_carteira =  f" Perfomance da carteira com todos os ativos: :blue[{performance_ativo:.1%}]"

   
st.write(f"""
## Performance dos Ativos 
Essa foi a performance de cada ativo no período selecionado:
         
{texto_performance_ativos}         
         
{texto_performance_carteira}         
         """)  #markdown


