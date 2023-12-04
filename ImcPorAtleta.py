from math import isnan
from dash.dependencies import Input, Output

from pandas import read_csv
import plotly.express as px
from dash import Dash, html, dcc

from components import header as DefaultHeader

# Função auxiliar para converter medalhas em pontos


def converter_medalha_em_pontos(medal):
    if medal == "Gold":
        return 3
    elif medal == "Silver":
        return 2
    elif medal == "Bronze":
        return 1
    else:
        return 0

# Função auxiliar para verificar se um evento é um recorde mundial fictício


def is_recorde_mundial(evento):
    return "World Record" in evento

# Função auxiliar para mapear gênero para contagem


def mapear_genero(genero):
    if genero == "M":
        return "Masculino"
    elif genero == "F":
        return "Feminino"
    else:
        return "Outro"


def contar_medalhas_por_pais(dados):
    contagem_medalhas = dados.groupby("NOC")["Medal"].apply(
        lambda x: sum(converter_medalha_em_pontos(m) for m in x)).to_dict()
    return contagem_medalhas

# verificar recorde mundial


def verificar_recorde_mundial(dados):
    recorde_mundial = any(is_recorde_mundial(evento)
                          for evento in dados["Event"])
    return recorde_mundial

# contar atletas por gênero


def contar_atletas_por_genero(dados):
    dados["Genero"] = dados["Sex"].apply(mapear_genero)
    contagem_genero = dados.groupby("Genero")["ID"].nunique().to_dict()
    return contagem_genero


def calcular_media_idade_atletas(dadosUnicosPorPessoa):
    media_idade = calcular_media_idade(dadosUnicosPorPessoa)
    return media_idade


def calcular_media_idade(atletas):
    if not atletas:
        return 0
    return sum(atleta["Age"] for atleta in atletas) / len(atletas)


dados = read_csv("dados/athlete_events.csv", delimiter=",")

dadosUnicosPorPessoa = []
idsLidosPorAno = {}

# Agrupamento dos dados
# ------------------------------------------------------------
for linha in dados.values:
    if isnan(linha[4]) or isnan(linha[5]):
        continue

    id = linha[0]  # Identificador Único
    nome = linha[1]
    altura = linha[4] / 100
    peso = linha[5]
    time = linha[6]
    ano = linha[9]

    if idsLidosPorAno.get(ano) == None:
        idsLidosPorAno[ano] = set()
    elif id in idsLidosPorAno[ano]:
        continue

    imc = peso / (altura ** 2)

    dadosUnicosPorPessoa.append({"nome": nome, "imc": imc, "ano": ano})
    idsLidosPorAno[ano].add(id)
# ------------------------------------------------------------

# Ordenação dos dados por IMC
# ------------------------------------------------------------
# Ordena o array de acordo com o imc
dadosUnicosPorPessoa.sort(key=lambda item: item["imc"])
# ------------------------------------------------------------

# Criação do DataFrame agrupado por ano
# ------------------------------------------------------------
dataFrameAgrupadoPorAno = {}
for dado in dadosUnicosPorPessoa:
    ano = dado["ano"]
    nome = dado["nome"]
    imc = dado["imc"]

    if dataFrameAgrupadoPorAno.get(ano) == None:
        dataFrameAgrupadoPorAno[ano] = {"nome": [], "imc": []}

    dataFrameAgrupadoPorAno[ano]["nome"].append(nome)
    dataFrameAgrupadoPorAno[ano]["imc"].append(imc)
# ------------------------------------------------------------

# Ordenação dos anos de forma decrescente
# ------------------------------------------------------------
anos = list(dataFrameAgrupadoPorAno.keys())
anos.sort(reverse=True)  # Ordena os anos de forma decrescente
# ------------------------------------------------------------

# Criação do layout (visualização)
# ------------------------------------------------------------
app = Dash(__name__)
app.layout = html.Div(
    className="container",
    children=[
        DefaultHeader,
        html.H1("IMC por Atleta"),
        dcc.Dropdown(
            id="anoSelecionado",
            options=[{"label": str(ano), "value": ano} for ano in anos],
            value=anos[0],
            style={"width": "100px"},
        ),
        dcc.RadioItems(
            id="ordemSelecionada",
            options=[
                {"label": "Decrescente", "value": "maior"},
                {"label": "Crescente", "value": "menor"},
            ],
            value="menor",
        ),
        dcc.Graph(
            id="grafico",
            figure=[],
        ),
    ]
)
# ------------------------------------------------------------

# Criação do callback (função que é chamada sempre que um dos inputs são alterados)
# ------------------------------------------------------------


@app.callback(
    Output(component_id="grafico", component_property="figure"),
    [
        Input(component_id="anoSelecionado", component_property="value"),
        Input(component_id="ordemSelecionada", component_property="value"),
    ],
)
def atualizarGrafico(anoSelecionado, ordemSelecionada):
    df = dataFrameAgrupadoPorAno[anoSelecionado].copy()
    if ordemSelecionada == "menor":
        df["nome"] = df["nome"][0:10]
        df["imc"] = df["imc"][0:10]
    else:
        df["nome"] = df["nome"][::-1][0:10]
        df["imc"] = df["imc"][::-1][0:10]

    grafico = px.bar(df, x="nome", y="imc")
    return grafico
# ------------------------------------------------------------


# Rodar o servidor
# ------------------------------------------------------------
app.run_server(port=3003)
# ------------------------------------------------------------
