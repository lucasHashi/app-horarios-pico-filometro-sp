import streamlit as st
import streamlit.components.v1 as components

import pandas as pd
import plotly.graph_objs as go

import carrega_analise_filometro

import os

CAMINHO_BASE_PROJETO = os.getcwd()

# PAGINA_ATUAL = 'inicio'

def main():
    st.set_page_config(
        page_title="Horarios de pico - Filometro",
        layout="wide"
    )

    carrega_analises = iniciar_classe_de_analise()

    st.write('# Horarios de pico - Filometro SP')

    PAGINA_ATUAL = st.selectbox('Páginas / Perguntas', [
        'Início',
        'Qual é o melhor horario para ir no meu posto?',
        'Qual é o posto mais vazio na minha região?',
        'Os postos estão ficando sem vacina?',
        'Mel ou Petit',
        'Contato'
    ])


    if PAGINA_ATUAL == 'Início':
        carregar_pagina_inicial(carrega_analises)

    elif PAGINA_ATUAL == 'Qual é o melhor horario para ir no meu posto?':
        carregar_pagina_melhor_horario_por_posto(carrega_analises)

    elif PAGINA_ATUAL == 'Qual é o posto mais vazio na minha região?':
        carregar_pagina_melhor_posto_por_regiao(carrega_analises)
    
    elif PAGINA_ATUAL == 'Os postos estão ficando sem vacina?':
        carregar_pagina_falta_de_vacinas(carrega_analises)
    
    elif PAGINA_ATUAL == 'Mel ou Petit':
        carregar_pagina_mel_ou_petit()
    
    elif PAGINA_ATUAL == 'Contato':
        carregar_pagina_contato()



def carregar_pagina_inicial(carrega_analises):
    # carregar_pagina_inicial()
    data_da_ultima_atualizacao = carrega_analises._carregar_data_da_ultima_atualizacao()
    data_da_ultima_atualizacao = data_da_ultima_atualizacao.strftime('%d/%m/%Y')

    st.write('### Ultima atualização dos dados: **{}**'.format(data_da_ultima_atualizacao))


def carregar_pagina_melhor_horario_por_posto(carrega_analises):
    st.title('Qual é o melhor horario para ir no meu posto?')

    lista_completa_postos = carrega_analises.df_dados_completo.sort_values('titulo')['titulo'].unique()
    lista_completa_postos = list(lista_completa_postos)

    postos_escolhidos = st.multiselect('Selecione os postos próximos', lista_completa_postos)

    if postos_escolhidos:
        st.write('## Mapa de calor da lotação média por horário')

        fig_heatmap_media_postos_escolhidos = carrega_analises.carregar_grafico_heatmap_pontuacao_dos_postos_escolhidos(postos_escolhidos)

        st.plotly_chart(fig_heatmap_media_postos_escolhidos, True)


        st.write('## Resumo por posto (do melhor para o pior)')

        lista_quotes_postos = carrega_analises.analise_final_pontuacao_dos_postos_escolhidos(postos_escolhidos)

        for quote_posto in lista_quotes_postos:
            st.markdown(quote_posto)

def carregar_pagina_melhor_posto_por_regiao(carrega_analises):
    st.title('Qual é o posto mais vazio na minha região?')

    regiao_escolhida = st.selectbox('Minha região', ['centro', 'leste', 'norte', 'oeste', 'sul'])

    horario_escolhido = st.selectbox('Horário de preferencia', [
        '06h - 08h', '08h - 10h',
        '10h - 12h', '12h - 14h',
        '14h - 16h', '16h - 18h',
        '18h - 20h', '20h - 22h',
        '22h - 24h'
    ])

    st.write('## Mapa de calor da lotação média por horário, **melhores 10** postos para o horario das **{}**'.format(horario_escolhido))

    fig_melhores_postos_por_regiao = carrega_analises.carregar_grafico_heatmap_melhores_postos_da_regiao_escolhida(regiao_escolhida, horario_escolhido)

    st.plotly_chart(fig_melhores_postos_por_regiao, True)

def carregar_pagina_falta_de_vacinas(carrega_analises):
    st.title('Os postos estão ficando sem vacina?')

    categoria_escolhida = st.selectbox('Minha região', ['drive-thru', 'megaposto', 'posto volante', 'centro', 'leste', 'norte', 'oeste', 'sul'])


    # analise = carrega_analises.analise_final_falta_de_vacina_por_categoria(categoria_escolhida)

    # st.write(analise)


    st.write('## Mapa de calor da falta de vacina ao longo do tempo')

    heatmap_falta_vacina_por_categoria = carrega_analises.carregar_grafico_heatmap_falta_de_vacinas_por_categoria(categoria_escolhida)

    st.plotly_chart(heatmap_falta_vacina_por_categoria, True)


    st.write('## Quantidade de postos com falta de vacina ao longo do tempo')

    scatter_falta_de_vacina_soma_dias = carrega_analises.carregar_grafico_scatter_falta_de_vacinas_por_categoria()

    st.plotly_chart(scatter_falta_de_vacina_soma_dias, True)

def carregar_pagina_mel_ou_petit():
    components.iframe('https://docs.google.com/forms/d/e/1FAIpQLSdy1lI52ubQ0Gs0qcdy-Q-G3h_JtFDBTtLRWHzfQ3mHCHnbiQ/viewform?embedded=true', width=640, height=900)

def carregar_pagina_contato():
    st.title('Contatos')


@st.cache
def iniciar_classe_de_analise():
    carrega_analises = carrega_analise_filometro.carrega_analise_filometro()

    return carrega_analises

if __name__ == '__main__':
    main()