import pandas as pd
pd.options.mode.chained_assignment = None

import streamlit as st
import streamlit.components.v1 as components
import PIL

import carrega_analise_filometro_otimizado as carrega_dados_otimizados

import os
import pickle

CAMINHO_BASE_PROJETO = os.getcwd()

PAGINA_ATUAL = 'Como esse app funciona?'

def main():
    st.set_page_config(
        page_title="Horários de pico - Filômetro",
        layout="wide"
    )

    st.write('# Horários de pico - Filômetro SP')

    st.write('### Selecione uma pergunta:')

    PAGINA_ATUAL = st.selectbox('', [
        'Como esse app funciona?',
        'Qual é o melhor horário para ir no meu posto?',
        'Qual é o posto mais vazio na minha região?',
        'Os postos estão ficando sem vacinas?',
        # 'Mel ou Petit?',
        'Quem fez esse app?'
    ])

    if not PAGINA_ATUAL in ['Como esse app funciona?', 'Mel ou Petit?', 'Quem fez esse app?']:
        if st.checkbox('Cores alternativas'):
            paleta_escolhida = 'alternativa'
        else:
            paleta_escolhida = 'base'


    if PAGINA_ATUAL == 'Como esse app funciona?':
        carregar_pagina_inicial()

    elif PAGINA_ATUAL == 'Qual é o melhor horário para ir no meu posto?':
        carregar_pagina_melhor_horario_por_posto(paleta_escolhida)

    elif PAGINA_ATUAL == 'Qual é o posto mais vazio na minha região?':
        carregar_pagina_melhor_posto_por_regiao(paleta_escolhida)
    
    elif PAGINA_ATUAL == 'Os postos estão ficando sem vacinas?':
        carregar_pagina_falta_de_vacinas(paleta_escolhida)
    
    # elif PAGINA_ATUAL == 'Mel ou Petit?':
    #     carregar_pagina_mel_ou_petit()
    
    elif PAGINA_ATUAL == 'Quem fez esse app?':
        carregar_pagina_contato()


def main2():
    st.set_page_config(
        page_title="Horários de pico - Filômetro",
        layout="wide"
    )

    PAGINA_ATUAL = cache_pagina_atual()

    st.title('Horários de pico - Filômetro SP')

    st.write('## Selecione uma pergunta:')

    # Botoes bem aparentes para selecionar onde ir
    # Cada um altera um valor em cache para o codigo da pagina
    if st.button('Como esse app funciona?'):
        PAGINA_ATUAL['pagina'] = 'Como esse app funciona?'

    if st.button('Qual é o melhor horário para ir no meu posto?'):
        PAGINA_ATUAL['pagina'] = 'Qual é o melhor horário para ir no meu posto?'

    if st.button('Qual é o posto mais vazio na minha região?'):
        PAGINA_ATUAL['pagina'] = 'Qual é o posto mais vazio na minha região?'

    if st.button('Os postos estão ficando sem vacinas?'):
        PAGINA_ATUAL['pagina'] = 'Os postos estão ficando sem vacinas?'

    # if st.button('Mel ou Petit?'):
    #     PAGINA_ATUAL['pagina'] = 'Mel ou Petit?'

    if st.button('Quem fez esse app?'):
        PAGINA_ATUAL['pagina'] = 'Quem fez esse app?'


    # Da a opcao de cores alternativas apenas para as paginas com graficos
    if not PAGINA_ATUAL['pagina'] in ['Como esse app funciona?', 'Mel ou Petit?', 'Quem fez esse app?']:
        st.write('## Escala de cores')
        if st.checkbox('Cores alternativas'):
            paleta_escolhida = 'alternativa'
        else:
            paleta_escolhida = 'base'


    # Carrega o resto da pagina, dependendo da pegunta escolhida
    if PAGINA_ATUAL['pagina'] == 'Como esse app funciona?':
        carregar_pagina_inicial()

    elif PAGINA_ATUAL['pagina'] == 'Qual é o melhor horário para ir no meu posto?':
        carregar_pagina_melhor_horario_por_posto(paleta_escolhida)

    elif PAGINA_ATUAL['pagina'] == 'Qual é o posto mais vazio na minha região?':
        carregar_pagina_melhor_posto_por_regiao(paleta_escolhida)
    
    elif PAGINA_ATUAL['pagina'] == 'Os postos estão ficando sem vacinas?':
        carregar_pagina_falta_de_vacinas(paleta_escolhida)
    
    # elif PAGINA_ATUAL['pagina'] == 'Mel ou Petit?':
    #     carregar_pagina_mel_ou_petit()
    
    elif PAGINA_ATUAL['pagina'] == 'Quem fez esse app?':
        carregar_pagina_contato()


def carregar_pagina_inicial():
    st.markdown('---')
    st.write('#### Ultima atualização dos dados: **19/07/2021**')

    st.write('# De olho na fila / Filômetro')
    st.write('A Prefeitura de SP disponibilizou o site **"De olho na fila"**, que **atualiza a cada 2 horas a situação da fila** em cada posto de vacinação de Covid-19 na cidade.')
    st.write('[De olho na fila](https://deolhonafila.prefeitura.sp.gov.br/)')
    st.write('**Fui coletando esses dados horários** e juntei aqui para ajudar as pessoas a **escolherem o posto mais vazio**.')


    st.write('# O que os gráficos significam')

    # st.write('As lotações dos postos foram enumeradas como na imagem, os valores dos gráficos são as médias dessas lotações')
    st.write('**Quanto mais cheio é o posto de vacinação, maior é o valor dele**. As cores dos gráficos estão como na imagem:')

    img_descricao = PIL.Image.open(os.path.join(CAMINHO_BASE_PROJETO, 'imagens', 'imagem_descricao_valores.jpg'))
    st.image(img_descricao)

    st.write('# Me ajude com a hospedagem desse site')
    st.write('Se **achou esse site útil**, tem alguns **trocados que não fariam falta** e **gostaria de ajudar** para esse site não cair ou falhar muito, considere mandar um pix.')
    st.write('Nesse momento **estou custeando o servidor por conta**, mas só posso continuar até certo tempo.')

    st.write('Chave aleatória:\n### 0df2925f-1523-4c84-8794-5935354d8f32')
    img_pix = PIL.Image.open(os.path.join(CAMINHO_BASE_PROJETO, 'imagens', 'pix_c6.png'))
    st.image(img_pix)


def carregar_pagina_melhor_horario_por_posto(paleta_escolhida):
    # st.title('Qual é o melhor horário para ir no meu posto?')
    st.title('Veja o melhor horário para ir em cada local de vacinação')

    with open(os.path.join(CAMINHO_BASE_PROJETO, 'dados_mais_recentes', 'lista_completa_postos.pickle'), 'rb') as f:
        lista_completa_postos = pickle.load(f)
    
    lista_completa_postos.sort()

    st.write('## Selecione um ou mais locais de vacinação:')
    postos_escolhidos = st.multiselect('', lista_completa_postos)

    if postos_escolhidos:
        st.write('## Lotação média por horário')

        fig_heatmap_media_postos_escolhidos = carrega_dados_otimizados.carregar_grafico_heatmap_pontuacao_dos_postos_escolhidos(paleta_escolhida, postos_escolhidos)

        st.plotly_chart(fig_heatmap_media_postos_escolhidos, True)


        st.write('## Resumo por posto (do melhor para o pior)')

        lista_quotes_postos = carrega_dados_otimizados.analise_final_pontuacao_dos_postos_escolhidos(postos_escolhidos)

        for quote_posto in lista_quotes_postos:
            st.markdown(quote_posto)

def carregar_pagina_melhor_posto_por_regiao(paleta_escolhida):
    # st.title('Qual é o posto mais vazio na minha região?')
    st.title('Veja o local mais vazio da sua região')

    st.write('## Selecione a sua região:')
    regiao_escolhida = st.selectbox('', ['centro', 'leste', 'norte', 'oeste', 'sul'])

    st.write('## Selecione um horário de preferência:')
    horario_escolhido = st.selectbox('', [
        '06h - 08h', '08h - 10h',
        '10h - 12h', '12h - 14h',
        '14h - 16h', '16h - 18h',
        '18h - 20h', '20h - 22h',
        '22h - 24h'
    ])

    fig_melhores_postos_por_regiao, fig_piores_postos_por_regiao = carrega_dados_otimizados.carregar_grafico_heatmap_melhores_e_piores_postos_da_regiao_escolhida(paleta_escolhida, 10, 5, regiao_escolhida, horario_escolhido)


    st.write('## **Melhores 10** postos para o horário das **{}**'.format(horario_escolhido))

    st.plotly_chart(fig_melhores_postos_por_regiao, True)


    st.write('## **Piores 5** postos para o horário das **{}**'.format(horario_escolhido))

    st.plotly_chart(fig_piores_postos_por_regiao, True)

def carregar_pagina_falta_de_vacinas(paleta_escolhida):
    # st.title('Os postos estão ficando sem vacinas?')
    st.title('Veja quantos postos ficaram sem vacina na sua região')

    st.write('## Selecione a sua região:')
    categoria_escolhida = st.selectbox('', ['drive-thru', 'megaposto', 'posto volante', 'centro', 'leste', 'norte', 'oeste', 'sul'])


    st.write('## Dias que faltaram vacinas ao longo do tempo')

    heatmap_falta_vacina_por_categoria = carrega_dados_otimizados.carregar_grafico_heatmap_falta_de_vacinas_por_categoria(paleta_escolhida, categoria_escolhida)

    st.plotly_chart(heatmap_falta_vacina_por_categoria, True)

# def carregar_pagina_mel_ou_petit():
#     st.title('Mel ou Petit?')
#     components.iframe('https://docs.google.com/forms/d/e/1FAIpQLSdy1lI52ubQ0Gs0qcdy-Q-G3h_JtFDBTtLRWHzfQ3mHCHnbiQ/viewform?embedded=true', width=640, height=900)

def carregar_pagina_contato():
    st.title('Quem fez esse app?')

    img_eu = PIL.Image.open(os.path.join(CAMINHO_BASE_PROJETO, 'imagens', 'eu.jpg'))
    st.image(img_eu, 'Eu.png')

    st.write('Ola, Sou **Lucas Belmonte**, estagiário em ciência de dados')
    st.write('Meu trabalho em geral é pegar dados e **auxiliar em boas decisões**.')
    st.write('Espero ter ajudado a se **planejar e evitar filas no seu dia de vacinação**.')
    st.write('Seguem **links** pra onde mais **me encontrar e encontrar os códigos desse app:**')

    st.write('''
        ### [Linkedin](https://www.linkedin.com/in/lucas-d-belmonte/)\n
        ### [Instagram](https://www.instagram.com/lucashashi_pk/)\n
        ### [Github](https://github.com/lucasHashi)\n
        ### [Códigos desse app](https://github.com/lucasHashi/app-horarios-pico-filometro-sp)\n
        ### [Site pessoal](http://www.lucasbelmonte.com.br/)\n
    ''')

    st.write('')
    st.write('Enfim, **obrigado por passar por aqui**.')




@st.cache(suppress_st_warning=True, allow_output_mutation=True)
def cache_pagina_atual():
    return {'pagina': 'Como esse app funciona?'}


if __name__ == '__main__':
    # main()
    
    main2()