import pandas as pd
import numpy as np
import os

import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime, timedelta

CAMINHO_BASE_PROJETO = os.getcwd()

PALETAS = {
    'base': {
        'baixo': '#1FA61B',
        'medio': '#F9AE0D',
        'alto': '#E21A1A'
    },
    'alternativa': {
        'baixo': '#69D3F2',
        'medio': '#EA418A',
        'alto': '#E20019'
    }
}

HORARIOS_TEXTO_SEQUENCIA_CERTA = [
    '00h - 02h', '02h - 04h',
    '04h - 06h', '06h - 08h',
    '08h - 10h', '10h - 12h',
    '12h - 14h', '14h - 16h',
    '16h - 18h', '18h - 20h',
    '20h - 22h', '22h - 24h'
]

TEXTOS_DAS_MEDIAS_POR_CATEGORIAS = {
    'centro': 'Média do centro',
    'sul': 'Média da zona sul',
    'leste': 'Média da zona leste',
    'norte': 'Média da zona norte',
    'oeste': 'Média da zona oeste',
    'drive-thru': 'Média dos drive-thru',
    'megaposto': 'Média dos megapostos',
    'posto volante': 'Média dos postos volante'
}


def carregar_media_todos_postos():
    df_media_todos_postos = pd.read_pickle(os.path.join(CAMINHO_BASE_PROJETO, 'dados_mais_recentes', 'media_horaria_todos_postos.pickle'))

    return df_media_todos_postos

def carregar_analise_media_todos_postos():
    df_analise_media_todos_postos = pd.read_pickle(os.path.join(CAMINHO_BASE_PROJETO, 'dados_mais_recentes', 'analise_media_todos_postos.pickle'))

    return df_analise_media_todos_postos

def carregar_falta_vacina_preenchido():
    df_falta_vacina_preenchido = pd.read_pickle(os.path.join(CAMINHO_BASE_PROJETO, 'dados_mais_recentes', 'falta_vacina_preenchido.pickle'))

    return df_falta_vacina_preenchido




def carregar_grafico_heatmap_pontuacao_dos_postos_escolhidos(paleta_escolhida, postos_escolhidos):
    df_media_postos_escolhidos = carregar_media_todos_postos()

    df_media_postos_escolhidos_aux = df_media_postos_escolhidos[
        df_media_postos_escolhidos.index.get_level_values('titulo').isin(postos_escolhidos)
    ]

    categorias_dos_postos_escolhidos = df_media_postos_escolhidos_aux['categoria'].unique()

    # Para otimizar a memoria
    del df_media_postos_escolhidos_aux

    categorias_dos_postos_escolhidos = [TEXTOS_DAS_MEDIAS_POR_CATEGORIAS[categoria] for categoria in categorias_dos_postos_escolhidos]

    # Adicionar os postos escolhidos e as categorias que fazem parte
    postos_escolhidos = postos_escolhidos + ['Média de SP'] + categorias_dos_postos_escolhidos

    df_media_postos_escolhidos = df_media_postos_escolhidos[
        df_media_postos_escolhidos.index.get_level_values('titulo').isin(postos_escolhidos)
    ]

    heatmap_pontuacao_posto_escolhido = go.Heatmap(
        z = df_media_postos_escolhidos['situacao_pontuacao'],
        y = df_media_postos_escolhidos.index.get_level_values('titulo'),
        x = df_media_postos_escolhidos.index.get_level_values('horario_texto'),
        colorscale = [
            PALETAS[paleta_escolhida]['baixo'],
            PALETAS[paleta_escolhida]['medio'],
            PALETAS[paleta_escolhida]['alto']
        ]
    )

    layout = go.Layout(
        height = round(70 * (len(postos_escolhidos) + 2)),
        xaxis = {
            'categoryorder': 'category ascending'
        }
    )
    

    fig = go.Figure(
        data = [heatmap_pontuacao_posto_escolhido],
        layout = layout
    )

    return fig


def carregar_grafico_heatmap_melhores_e_piores_postos_da_regiao_escolhida(paleta_escolhida, quantidade_melhores, quantidade_piores, regiao_escolhida, horario_escolhido):
    df_media_postos_da_regiao_escolhida = carregar_media_todos_postos()

    df_media_postos_da_regiao_escolhida_aux = df_media_postos_da_regiao_escolhida[
        (df_media_postos_da_regiao_escolhida['categoria'] == regiao_escolhida) &
        (df_media_postos_da_regiao_escolhida.index.get_level_values('horario_texto') == horario_escolhido) &
        (~df_media_postos_da_regiao_escolhida.index.get_level_values('titulo').isin(list(TEXTOS_DAS_MEDIAS_POR_CATEGORIAS.values())))
    ]

    df_media_postos_da_regiao_escolhida_aux.sort_values('situacao_pontuacao', ascending=True, inplace=True)

    lista_melhores_postos = list(df_media_postos_da_regiao_escolhida_aux.head(quantidade_melhores).index.get_level_values('titulo'))
    lista_piores_postos = list(df_media_postos_da_regiao_escolhida_aux.tail(quantidade_piores).index.get_level_values('titulo'))

    del df_media_postos_da_regiao_escolhida_aux

    df_melhores_postos_da_regiao_escolhida = df_media_postos_da_regiao_escolhida[df_media_postos_da_regiao_escolhida.index.get_level_values('titulo').isin(lista_melhores_postos)]
    df_piores_postos_da_regiao_escolhida = df_media_postos_da_regiao_escolhida[df_media_postos_da_regiao_escolhida.index.get_level_values('titulo').isin(lista_piores_postos)]



    # Gerando grafico dos melhores postos
    heatmap_pontuacao_melhores_postos_na_regiao = go.Heatmap(
        z = df_melhores_postos_da_regiao_escolhida['situacao_pontuacao'],
        y = df_melhores_postos_da_regiao_escolhida.index.get_level_values('titulo'),
        x = df_melhores_postos_da_regiao_escolhida.index.get_level_values('horario_texto'),
        colorscale = [
            PALETAS[paleta_escolhida]['baixo'],
            PALETAS[paleta_escolhida]['medio'],
            PALETAS[paleta_escolhida]['alto']
        ]
    )

    layout_melhores = go.Layout(
        height = 800,
        xaxis = {
            'categoryorder': 'category ascending'
        }
    )

    

    fig_melhores = go.Figure(
        data = [heatmap_pontuacao_melhores_postos_na_regiao],
        layout = layout_melhores
    )



    # Gerando grafico dos piores postos
    heatmap_pontuacao_piores_postos_na_regiao = go.Heatmap(
        z = df_piores_postos_da_regiao_escolhida['situacao_pontuacao'],
        y = df_piores_postos_da_regiao_escolhida.index.get_level_values('titulo'),
        x = df_piores_postos_da_regiao_escolhida.index.get_level_values('horario_texto'),
        colorscale = [
            PALETAS[paleta_escolhida]['baixo'],
            PALETAS[paleta_escolhida]['medio'],
            PALETAS[paleta_escolhida]['alto']
        ]
    )

    layout_piores = go.Layout(
        height = 510,
        xaxis = {
            'categoryorder': 'category ascending'
        }
    )

    fig_piores = go.Figure(
        data = [heatmap_pontuacao_piores_postos_na_regiao],
        layout = layout_piores
    )

    return fig_melhores, fig_piores


def carregar_grafico_heatmap_falta_de_vacinas_por_categoria(paleta_escolhida, categoria_escolhida):
    df_falta_vacina_preenchido = carregar_falta_vacina_preenchido()

    df_falta_de_vacina = df_falta_vacina_preenchido[df_falta_vacina_preenchido['categoria'] == categoria_escolhida]

    heatmap_falta_de_vacina = go.Heatmap(
        z = df_falta_de_vacina['sem_vacina'],
        y = df_falta_de_vacina['titulo'],
        x = df_falta_de_vacina['data_atualizacao'],
        colorscale = [
            PALETAS[paleta_escolhida]['baixo'],
            PALETAS[paleta_escolhida]['alto']
        ]
    )

    layout = go.Layout(
        height = 800
    )

    

    fig = go.Figure(
        data = [heatmap_falta_de_vacina],
        layout = layout
    )

    return fig

def carregar_grafico_scatter_falta_de_vacinas_por_categoria():
    df_falta_de_vacina = df_dados_completo[df_dados_completo['sem_vacina'] >= 0]

    df_falta_de_vacina_soma_dias = df_falta_de_vacina.groupby(['categoria', 'titulo', 'data_atualizacao']).agg({'sem_vacina': sum})

    # Caso a media de maior que 0, entao pelo menos em um horario tivemos falta de vacina no posto
    df_falta_de_vacina_soma_dias['sem_vacina'] = df_falta_de_vacina_soma_dias['sem_vacina'].apply(lambda media: 1 if media > 0 else 0)

    df_falta_de_vacina_soma_dias.reset_index(inplace=True)

    df_falta_de_vacina_soma_dias = df_falta_de_vacina_soma_dias.groupby(['categoria', 'data_atualizacao']).agg({'sem_vacina': sum})

    data = []
    for categoria in df_falta_de_vacina_soma_dias.index.get_level_values('categoria').unique():
        df_falta_de_vacina_soma_dias_categoria = df_falta_de_vacina_soma_dias[df_falta_de_vacina_soma_dias.index.get_level_values('categoria') == categoria]

        curva_contagem_dias_sem_vacina = go.Scatter(
            x = df_falta_de_vacina_soma_dias_categoria.index.get_level_values('data_atualizacao'),
            y = df_falta_de_vacina_soma_dias_categoria['sem_vacina'],
            mode = 'markers+lines',
            name = categoria
        )

        data.append(curva_contagem_dias_sem_vacina)

    fig = go.Figure(
        data = data
    )

    return fig





def analise_final_pontuacao_dos_postos_escolhidos(postos_escolhidos):
    df_analise_media_postos_escolhidos = carregar_analise_media_todos_postos()

    df_analise_media_postos_escolhidos = df_analise_media_postos_escolhidos[
        df_analise_media_postos_escolhidos.index.get_level_values('titulo').isin(postos_escolhidos)
    ]

    lista_quotes_postos = list(df_analise_media_postos_escolhidos['markdown_resultado'])

    return lista_quotes_postos


if __name__ == '__main__':
    pass