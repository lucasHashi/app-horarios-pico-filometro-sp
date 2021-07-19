import streamlit as st
import streamlit.components.v1 as components
import PIL

import carrega_analise_filometro

import os

CAMINHO_BASE_PROJETO = os.getcwd()

def main():
    st.set_page_config(
        page_title="Horarios de pico - Filômetro",
        layout="wide"
    )

    carrega_analises = iniciar_classe_de_analise()

    st.write('# Horarios de pico - Filômetro SP')

    PAGINA_ATUAL = st.selectbox('Páginas / Perguntas', [
        'Início',
        'Qual é o melhor horario para ir no meu posto?',
        'Qual é o posto mais vazio na minha região?',
        'Os postos estão ficando sem vacinas?',
        'Mel ou Petit',
        'Quem fez esse app?'
    ])


    if PAGINA_ATUAL == 'Início':
        carregar_pagina_inicial(carrega_analises)

    elif PAGINA_ATUAL == 'Qual é o melhor horario para ir no meu posto?':
        carregar_pagina_melhor_horario_por_posto(carrega_analises)

    elif PAGINA_ATUAL == 'Qual é o posto mais vazio na minha região?':
        carregar_pagina_melhor_posto_por_regiao(carrega_analises)
    
    elif PAGINA_ATUAL == 'Os postos estão ficando sem vacinas?':
        carregar_pagina_falta_de_vacinas(carrega_analises)
    
    elif PAGINA_ATUAL == 'Mel ou Petit':
        carregar_pagina_mel_ou_petit()
    
    elif PAGINA_ATUAL == 'Quem fez esse app?':
        carregar_pagina_contato()



def carregar_pagina_inicial(carrega_analises):
    # carregar_pagina_inicial()
    data_da_ultima_atualizacao = carrega_analises._carregar_data_da_ultima_atualizacao()
    data_da_ultima_atualizacao = data_da_ultima_atualizacao.strftime('%d/%m/%Y')

    st.write('### Ultima atualização dos dados: **{}**'.format(data_da_ultima_atualizacao))


    st.write('## De olho na fila ou Filômetro')
    st.write('A prefeitura de SP disponibilizou o site "De olho na fila", que atualizar a cada 2 horas a situação da fila em cada posto de vacinação de Covid-19 na cidade.')
    st.write('[De olho na fila](https://deolhonafila.prefeitura.sp.gov.br/)')
    st.write('Fui coletando esses dados horários e juntei aqui pra ajudar as pessoas escolherem o posto mais vazio.')


    st.write('## O que os números dos gráficos significam')

    st.write('As lotações dos postos foram enumeradas como na imagem, os valores dos gráficos são as médias dessas lotações')

    img_descricao = PIL.Image.open(os.path.join(CAMINHO_BASE_PROJETO, 'imagens', 'imagem_descricao_valores.jpg'))
    st.image(img_descricao)


def carregar_pagina_melhor_horario_por_posto(carrega_analises):
    st.title('Qual é o melhor horario para ir no meu posto?')

    lista_completa_postos = carrega_analises.df_dados_completo.sort_values('titulo')['titulo'].unique()
    lista_completa_postos = list(lista_completa_postos)

    postos_escolhidos = st.multiselect('Selecione os postos próximos', lista_completa_postos)

    if postos_escolhidos:
        st.write('## Lotação média por horário')

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

    st.write('## **Melhores 10** postos para o horario das **{}**'.format(horario_escolhido))

    fig_melhores_postos_por_regiao = carrega_analises.carregar_grafico_heatmap_melhores_postos_da_regiao_escolhida(10, regiao_escolhida, horario_escolhido)

    st.plotly_chart(fig_melhores_postos_por_regiao, True)


    st.write('## **Piores 5** postos')

    fig_piores_postos_por_regiao = carrega_analises.carregar_grafico_heatmap_piores_postos_da_regiao_escolhida(5, regiao_escolhida, horario_escolhido)

    st.plotly_chart(fig_piores_postos_por_regiao, True)

def carregar_pagina_falta_de_vacinas(carrega_analises):
    st.title('Os postos estão ficando sem vacinas?')

    categoria_escolhida = st.selectbox('Minha região', ['drive-thru', 'megaposto', 'posto volante', 'centro', 'leste', 'norte', 'oeste', 'sul'])


    # analise = carrega_analises.analise_final_falta_de_vacina_por_categoria(categoria_escolhida)

    # st.write(analise)


    st.write('## Dias com falta de vacina ao longo do tempo')

    heatmap_falta_vacina_por_categoria = carrega_analises.carregar_grafico_heatmap_falta_de_vacinas_por_categoria(categoria_escolhida)

    st.plotly_chart(heatmap_falta_vacina_por_categoria, True)


    st.write('## Quantidade de postos com falta de vacina ao longo do tempo')

    scatter_falta_de_vacina_soma_dias = carrega_analises.carregar_grafico_scatter_falta_de_vacinas_por_categoria()

    st.plotly_chart(scatter_falta_de_vacina_soma_dias, True)

def carregar_pagina_mel_ou_petit():
    components.iframe('https://docs.google.com/forms/d/e/1FAIpQLSdy1lI52ubQ0Gs0qcdy-Q-G3h_JtFDBTtLRWHzfQ3mHCHnbiQ/viewform?embedded=true', width=640, height=900)

def carregar_pagina_contato():
    st.title('Quem fez esse app?')

    img_eu = PIL.Image.open(os.path.join(CAMINHO_BASE_PROJETO, 'imagens', 'eu.jpg'))
    st.image(img_eu, 'Eu.png')

    st.write('Oi, tudo bem? Sou **Lucas Belmonte**, cientista de dados, pensei que coletar esses dados e disponibilizar com gráficos e tudo mais seria legal')
    st.write('Espero ter ajudado você a escolher um **melhor horário pra vacinar**')
    st.write('Meu trabalho em geral é pegar dados e **auxiliar em boas decições**')
    st.write('Enfim, seguem **links** pra onde mais **me encontrar e encontrar os códigos desse app**')

    st.write('''
        ### [Linkedin](https://www.linkedin.com/in/lucas-d-belmonte/)\n
        ### [Instagram](https://www.instagram.com/lucashashi_pk/)\n
        ### [Insta dos meus cães](https://www.instagram.com/mel_e_petit/)\n
        ### [Códigos desse app](https://github.com/lucasHashi/app-horarios-pico-filometro-sp)\n
        ### [Github](https://github.com/lucasHashi)\n
        ### [Site pessoal](http://www.lucasbelmonte.com.br/)\n
    ''')

    st.write('## Me ajude com a hospedagem desse site')
    st.write('Se achou esse site útil, tem alguns trocados que não fariam falta e gostaria de ajudar pra esse site não cair ou falhar muito, considere manda um pix.')
    st.write('Nesse momento estou custeando o servidor por conta, mas só posso continuar até certo tempo.')

    st.write('Chave aleatória:\n### 0df2925f-1523-4c84-8794-5935354d8f32')
    img_pix = PIL.Image.open(os.path.join(CAMINHO_BASE_PROJETO, 'imagens', 'pix_c6.png'))
    st.image(img_pix)

    st.write('Enfim, agora sim acabou, **obrigado por passar por aqui**.')


@st.cache
def iniciar_classe_de_analise():
    carrega_analises = carrega_analise_filometro.carrega_analise_filometro()

    return carrega_analises


if __name__ == '__main__':
    main()