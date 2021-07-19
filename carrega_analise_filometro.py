import pandas as pd
import numpy as np
import os

import plotly.graph_objects as go
import plotly.express as px

from datetime import datetime, timedelta


class carrega_analise_filometro(object):
    CAMINHO_BASE_PROJETO = os.getcwd()

    ARQUIVO_CONSOLIDADO_FILOMETRO = 'dados_consolidados.pickle'
    CAMINHO_ARQUIVO_DADOS_CONSOLIDADOS = os.path.join(CAMINHO_BASE_PROJETO, 'dados_mais_recentes', ARQUIVO_CONSOLIDADO_FILOMETRO)

    PONTUACAO_POR_SITUACAO = {
        'sem_fila': 0,
        'fila_pequena': 1,
        'fila_media': 2,
        'fila_grande': 3,
        'aguardando_abastecimento': -1,
        'nao_funcionando': -2,
        'sem_informacao': -2
    }

    PONTUACAO_POR_FALTA_DE_VACINA = {
        'sem_fila': 0,
        'fila_pequena': 0,
        'fila_media': 0,
        'fila_grande': 0,
        'aguardando_abastecimento': 1,
        'nao_funcionando': -1,
        'sem_informacao': -1
    }

    TEXTOS_HORARIOS = {
        0: '00h - 02h',
        2: '02h - 04h',
        4: '04h - 06h',
        6: '06h - 08h',
        8: '08h - 10h',
        10: '10h - 12h',
        12: '12h - 14h',
        14: '14h - 16h',
        16: '16h - 18h',
        18: '18h - 20h',
        20: '20h - 22h',
        22: '22h - 24h',
        np.nan: np.nan
    }

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


    def __init__(self, modo_daltonico = False):
        self.df_dados_completo = self._carregar_dados_completos()
        
        self.modo_daltonico = modo_daltonico

        self.paleta_escolhida = 'alternativa' if modo_daltonico else 'base'




    def _carregar_dados_completos(self):
        df_dados_completo = pd.read_pickle('./dados_mais_recentes/dados_consolidados.pickle')

        df_dados_completo['data_atualizacao'] = pd.to_datetime(df_dados_completo['data_atualizacao'], format='%d/%m/%Y', errors='coerce')

        df_dados_completo['horario_atualizacao'] = pd.to_datetime(df_dados_completo['horario_atualizacao'], format='%H:%M', errors='coerce')
        df_dados_completo['horario_aproximado'] = pd.to_datetime(df_dados_completo['horario_aproximado'], format='%H:%M', errors='coerce')

        df_dados_completo['situacao_pontuacao'] = df_dados_completo['situacao'].apply(lambda situacao: self.PONTUACAO_POR_SITUACAO[situacao])

        df_dados_completo['horario_aproximado_par'] = df_dados_completo['horario_aproximado'].apply(lambda horario: horario if horario.hour % 2 == 0 else horario - timedelta(hours=1))

        df_dados_completo['horario_texto'] = df_dados_completo['horario_aproximado_par'].apply(lambda horario: self.TEXTOS_HORARIOS[horario.hour])

        df_dados_completo['sem_vacina'] = df_dados_completo['situacao'].apply(lambda situacao: self.PONTUACAO_POR_FALTA_DE_VACINA[situacao])

        return df_dados_completo
    
    def _carregar_data_da_ultima_atualizacao(self):
        data_da_ultima_atualizacao = self.df_dados_completo['data_atualizacao'].max()

        return data_da_ultima_atualizacao



    def _carregar_df_media_pontuacao_por_postos_escolhidos(self, postos_escolhidos):
        df_postos_escolhidos = self.df_dados_completo[
            (self.df_dados_completo['titulo'].isin(postos_escolhidos)) &
            (self.df_dados_completo['situacao_pontuacao'] >= 0)
        ]

        categorias_postos_escolhidos = df_postos_escolhidos['categoria'].unique()

        df_postos_escolhidos = df_postos_escolhidos.groupby(['titulo', 'horario_texto']).mean()

        df_postos_escolhidos_categoria = self._carregar_media_categorias_escolhidas(categorias_postos_escolhidos)
        df_media_geral = self._carregar_media_geral()

        df_posto_heatmap = pd.concat([df_postos_escolhidos, df_postos_escolhidos_categoria, df_media_geral])

        return df_posto_heatmap
    
    def _carregar_df_melhores_postos_por_regiao_escolhida(self, quantidade_postos, regiao_escolhida, horario_escolhido):
        melhores_postos = self._carregar_melhores_postos_por_regiao_e_horario(quantidade_postos, regiao_escolhida, horario_escolhido)

        # Filtra os dados completos dos 10 melhores no horario especificado
        df_melhores_postos_da_regiao = self.df_dados_completo[
            (self.df_dados_completo['titulo'].isin(melhores_postos)) &
            (self.df_dados_completo['situacao_pontuacao'] >= 0)
        ]

        df_melhores_postos_da_regiao = df_melhores_postos_da_regiao.groupby(['titulo', 'horario_texto']).mean()

        df_posto_escolhido_categoria = self._carregar_media_categorias_escolhidas([regiao_escolhida])
        df_media_geral = self._carregar_media_geral()

        df_heatmap_melhores_postos_na_regiao = pd.concat([df_melhores_postos_da_regiao, df_posto_escolhido_categoria, df_media_geral])

        return df_heatmap_melhores_postos_na_regiao
    
    def _carregar_df_piores_postos_por_regiao_escolhida(self, quantidade_postos, regiao_escolhida, horario_escolhido):
        piores_postos = self._carregar_piores_postos_por_regiao_e_horario(quantidade_postos, regiao_escolhida, horario_escolhido)

        # Filtra os dados completos dos 10 melhores no horario especificado
        df_piores_postos_da_regiao = self.df_dados_completo[
            (self.df_dados_completo['titulo'].isin(piores_postos)) &
            (self.df_dados_completo['situacao_pontuacao'] >= 0)
        ]

        df_piores_postos_da_regiao = df_piores_postos_da_regiao.groupby(['titulo', 'horario_texto']).mean()

        #df_posto_escolhido_categoria = self._carregar_media_categorias_escolhidas([regiao_escolhida])
        #df_media_geral = self._carregar_media_geral()

        #df_heatmap_piores_postos_na_regiao = pd.concat([df_piores_postos_da_regiao, df_posto_escolhido_categoria, df_media_geral])
        df_heatmap_piores_postos_na_regiao = df_piores_postos_da_regiao.copy()

        return df_heatmap_piores_postos_na_regiao



    def _carregar_media_geral(self):
        """Calcula a media geral da pontuacao dos postos em specifito

        Returns:
            DataFrame: df da media de pontuacao
        """
        df_media_geral = self.df_dados_completo[self.df_dados_completo['situacao_pontuacao'] >= 0]

        df_media_geral = df_media_geral.groupby(['horario_texto']).mean()

        df_media_geral = pd.concat({'Média de SP': df_media_geral}, names=['titulo'])

        return df_media_geral
    
    def _carregar_media_categorias_escolhidas(self, categorias_postos_escolhidos):
        df_postos_escolhidos_categoria = self.df_dados_completo[
            (self.df_dados_completo['categoria'].isin(categorias_postos_escolhidos)) &
            (self.df_dados_completo['situacao_pontuacao'] >= 0)
        ]

        df_postos_escolhidos_categoria = df_postos_escolhidos_categoria.groupby(['categoria', 'horario_texto']).mean()
        
        df_postos_escolhidos_categoria.rename(index = self.TEXTOS_DAS_MEDIAS_POR_CATEGORIAS, inplace=True)

        return df_postos_escolhidos_categoria
    
    def _carregar_melhores_postos_por_regiao_e_horario(self, quantidade_postos, regiao_escolhida, horario_escolhido):
        # Filtra os postos dessa regiao e apenas o horario em questao
        df_regiao_escolhida = self.df_dados_completo[
            (self.df_dados_completo['categoria'] == regiao_escolhida) &
            (self.df_dados_completo['situacao_pontuacao'] >= 0) &
            (self.df_dados_completo['horario_texto'] == horario_escolhido)
        ]

        # Calcula a media e pega os N melhores
        melhores_postos = df_regiao_escolhida.groupby(['titulo']).mean()
        melhores_postos.sort_values('situacao_pontuacao', inplace=True)
        melhores_postos = melhores_postos.head(quantidade_postos)
        melhores_postos = melhores_postos.index.get_level_values('titulo')
        melhores_postos = list(melhores_postos)

        return melhores_postos
    
    def _carregar_piores_postos_por_regiao_e_horario(self, quantidade_postos, regiao_escolhida, horario_escolhido):
        # Filtra os postos dessa regiao e apenas o horario em questao
        df_regiao_escolhida = self.df_dados_completo[
            (self.df_dados_completo['categoria'] == regiao_escolhida) &
            (self.df_dados_completo['situacao_pontuacao'] >= 0) &
            (self.df_dados_completo['horario_texto'] == horario_escolhido)
        ]

        # Calcula a media e pega os N melhores
        piores_postos = df_regiao_escolhida.groupby(['titulo']).mean()
        piores_postos.sort_values('situacao_pontuacao', inplace=True)
        piores_postos = piores_postos.tail(quantidade_postos)
        piores_postos = piores_postos.index.get_level_values('titulo')
        piores_postos = list(piores_postos)

        return piores_postos
    


    def carregar_grafico_heatmap_pontuacao_dos_postos_escolhidos(self, postos_escolhidos):
        df_media_postos_escolhidos = self._carregar_df_media_pontuacao_por_postos_escolhidos(postos_escolhidos)

        heatmap_pontuacao_posto_escolhido = go.Heatmap(
            z = df_media_postos_escolhidos['situacao_pontuacao'],
            y = df_media_postos_escolhidos.index.get_level_values('titulo'),
            x = df_media_postos_escolhidos.index.get_level_values('horario_texto'),
            colorscale = [
                self.PALETAS[self.paleta_escolhida]['baixo'],
                self.PALETAS[self.paleta_escolhida]['medio'],
                self.PALETAS[self.paleta_escolhida]['alto']
            ]
        )

        layout = go.Layout(
            height = round(110 * (len(postos_escolhidos) + 2))
        )

        fig = go.Figure(
            data = [heatmap_pontuacao_posto_escolhido],
            layout = layout
        )

        return fig
    

    def carregar_grafico_heatmap_melhores_postos_da_regiao_escolhida(self, quantidade_postos, regiao_escolhida, horario_escolhido):
        df_heatmap_melhores_postos_na_regiao = self._carregar_df_melhores_postos_por_regiao_escolhida(quantidade_postos, regiao_escolhida, horario_escolhido)

        df_heatmap_melhores_postos_na_regiao.sort_values('situacao_pontuacao', ascending=True)

        heatmap_pontuacao_melhores_postos_na_regiao = go.Heatmap(
            z = df_heatmap_melhores_postos_na_regiao['situacao_pontuacao'],
            y = df_heatmap_melhores_postos_na_regiao.index.get_level_values('titulo'),
            x = df_heatmap_melhores_postos_na_regiao.index.get_level_values('horario_texto'),
            colorscale = [
                self.PALETAS[self.paleta_escolhida]['baixo'],
                self.PALETAS[self.paleta_escolhida]['medio'],
                self.PALETAS[self.paleta_escolhida]['alto']
            ]
        )

        layout = go.Layout(
            height = 800
        )

        fig = go.Figure(
            data = [heatmap_pontuacao_melhores_postos_na_regiao],
            layout = layout
        )

        return fig

    def carregar_grafico_heatmap_piores_postos_da_regiao_escolhida(self, quantidade_postos, regiao_escolhida, horario_escolhido):
        df_heatmap_piores_postos_na_regiao = self._carregar_df_piores_postos_por_regiao_escolhida(quantidade_postos, regiao_escolhida, horario_escolhido)

        df_heatmap_piores_postos_na_regiao.sort_values('situacao_pontuacao', ascending=True)

        heatmap_pontuacao_melhores_postos_na_regiao = go.Heatmap(
            z = df_heatmap_piores_postos_na_regiao['situacao_pontuacao'],
            y = df_heatmap_piores_postos_na_regiao.index.get_level_values('titulo'),
            x = df_heatmap_piores_postos_na_regiao.index.get_level_values('horario_texto'),
            colorscale = [
                self.PALETAS[self.paleta_escolhida]['baixo'],
                self.PALETAS[self.paleta_escolhida]['medio'],
                self.PALETAS[self.paleta_escolhida]['alto']
            ]
        )

        layout = go.Layout(
            height = 510
        )

        fig = go.Figure(
            data = [heatmap_pontuacao_melhores_postos_na_regiao],
            layout = layout
        )

        return fig
    

    def carregar_grafico_heatmap_falta_de_vacinas_por_categoria(self, categoria_escolhida):
        df_falta_de_vacina = self.df_dados_completo[
            (self.df_dados_completo['sem_vacina'] >= 0) &
            (self.df_dados_completo['categoria'] == categoria_escolhida)
        ]

        df_falta_de_vacina_media = df_falta_de_vacina.pivot_table(
            index = 'titulo',
            columns = 'data_atualizacao',
            values = 'sem_vacina',
            aggfunc = sum
        )

        df_falta_de_vacina_media.fillna(0, inplace=True)
        df_falta_de_vacina_media.reset_index(inplace=True)

        df_falta_de_vacina_media = df_falta_de_vacina_media.melt('titulo', value_name='sem_vacina', var_name='data_atualizacao')

        # Caso a media de maior que 0, entao pelo menos em um horario tivemos falta de vacina no posto
        df_falta_de_vacina_media['sem_vacina'] = df_falta_de_vacina_media['sem_vacina'].apply(lambda media: 1 if media > 0 else 0)

        heatmap_falta_de_vacina = go.Heatmap(
            z = df_falta_de_vacina_media['sem_vacina'],
            y = df_falta_de_vacina_media['titulo'],
            x = df_falta_de_vacina_media['data_atualizacao'],
            colorscale = [
                self.PALETAS[self.paleta_escolhida]['baixo'],
                self.PALETAS[self.paleta_escolhida]['alto']
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

    def carregar_grafico_scatter_falta_de_vacinas_por_categoria(self):
        df_falta_de_vacina = self.df_dados_completo[self.df_dados_completo['sem_vacina'] >= 0]

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
    




    def analise_final_pontuacao_dos_postos_escolhidos(self, postos_escolhidos):
        df_media_postos_escolhidos = self._carregar_df_media_pontuacao_por_postos_escolhidos(postos_escolhidos)

        df_media_postos_escolhidos.reset_index(inplace=True)

        df_media_postos_escolhidos = df_media_postos_escolhidos.groupby('titulo').mean()

        df_media_postos_escolhidos.sort_values('situacao_pontuacao', ascending=True, inplace=True)


        media_geral = df_media_postos_escolhidos[df_media_postos_escolhidos.index == 'Média de SP']['situacao_pontuacao'].iloc[0]

        lista_quotes_postos = []
        for titulo_posto in df_media_postos_escolhidos[df_media_postos_escolhidos.index.isin(postos_escolhidos)].index:

            media_posto_atual = df_media_postos_escolhidos[df_media_postos_escolhidos.index == titulo_posto]['situacao_pontuacao'].iloc[0]

            diferenca_media_geral = media_posto_atual / media_geral

            lotacao_direcao = 'menor' if diferenca_media_geral < 1 else 'maior' if diferenca_media_geral > 1 else 'igual'

            if diferenca_media_geral >= 2:
                lotacao_texto = 'muito superior'
            elif diferenca_media_geral >= 1.5:
                lotacao_texto = 'superior'
            elif diferenca_media_geral > 1:
                lotacao_texto = 'um pouco superior'
            elif diferenca_media_geral == 1:
                lotacao_texto = 'igual'
            elif diferenca_media_geral >= 0.75:
                lotacao_texto = 'um pouco inferior'
            elif diferenca_media_geral >= 0.5:
                lotacao_texto = 'inferior'
            else:
                lotacao_texto = 'muito inferior'

            quote_analise_posto = '''
                > O posto **{}** tem\n
                > lotação média **{}** da média de SP ({}% {})
            '''.format(titulo_posto, lotacao_texto, int(round(abs((diferenca_media_geral - 1)) * 100)), lotacao_direcao)

            lista_quotes_postos.append(quote_analise_posto)

        return lista_quotes_postos
    
    def analise_final_falta_de_vacina_por_categoria(self, categoria_escolhida):
        pass



if __name__ == '__main__':
    pass