#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-19: Fixed button styling to be white and left-aligned
# 2024-04-19: Updated "AI" to "IA" to match Portuguese language
# 2024-04-19: Added inline navigation button and improved layout with dividers
# 2024-04-14: Fixed image parameter to use width instead of use_container_width
# 2024-03-27: Página inicial do MDM Vision AI App
"""

import streamlit as st
from components.navigation import render_navigation
from utils.google_tag_manager import inject_gtm
from urllib.parse import quote

def render():
    """
    Renderiza a página inicial com mensagem de boas-vindas e logo.
    """

    # Inject GTM script
    inject_gtm()

    # Título principal
    st.title("🏠 Bem-vindos ao Creators Engine App 2025") #, divider="rainbow")
    st.subheader("exclusivo para Creators 2025", divider="rainbow")

    # Imagem da página inicial
    # st.image("img/home.jpg", width=150)

    # Texto de boas-vindas
    st.markdown("""

    Esta ferramenta contém vários módulos para potencializar os resultados de conteúdo no YouTube,  usando métodos testados, captura e ciência de dados, aliados com  diferentes IA's  para:

    - Avaliação de Metadados
    - Qualificação de:
        - Aspectos Criativos ( cores, composição, estética)
        - Canal ( marca/logotipo, fit com o conteúdo)
        - Elementos na imagem - rostos, pessoas, objetos, textos, ícones etc
    - Detecção de conteúdo sensível e/ou inapropriado
    - Avaliação de performance do thumbnail
    - Avaliação de performance do Canal, Video, Playlist

    e muito mais.

    Importante : não atuamos nos aspectos da produção de conteúdo, roteiros e estratégias.
    Nosso foco é  maximizar o potencial do seu conteúdo, de forma automatizada e objetiva.

    Como você pode ver, a ferramenta é projetada para ajudar os criadores a melhorar seus resultados no YouTube.
    """)

    # # Renderizar o botão de navegação inline para telas responsivas
    # # Botão como dois-liner, branco e alinhado à esquerda
    # if st.button(" Ir para\nCreators Engine IA", type="secondary", use_container_width=False):
    #     st.session_state["nav_active"] = "creators_engine_ia"
    #     st.query_params["page"] = quote("creators_engine_ia")
    #     st.rerun()

    # st.markdown("""
    # 1. Clique no botão acima ou no menu lateral
    # 2. Faça upload de uma imagem ou forneça uma URL do YouTube
    # 3. Visualize os resultados da análise

    # e repetir, e repetir, e repetir... até que você tenha um bom thumbnail.

    # """)
    # st.warning(""" Atenção:
    # Recomendamos que suas miniaturas personalizadas:
    # - tenham uma resolução de 1280x720 (com largura mínima de 640 pixels);
    # - sejam enviadas em formatos de imagem, como JPG, GIF ou PNG;
    # - tenham menos de 2 MB para vídeos ou 10 MB para podcasts;
    # - tenham proporção de 16:9, a mais usada em players e prévias do YouTube;
    # - tenham proporção de 1:1 para playlists de podcast, em vez de 16:9 (1280 x 1280 pixels).
    # https://support.google.com/youtube/answer/72431?hl=pt-BR&co=GENIE.Platform%3DAndroid&sjid=9721443515878038422-SA#zippy=%2Cthumbnail-policies%2Cimage-size-resolution%2Ctamanho-e-resolu%C3%A7%C3%A3o-da-imagem
    # """)
    # st.divider()

    st.markdown("""
    ### <- Recursos disponíveis na barra lateral, clique e explore.

- **🧱 Thumbs Safety** : garantia que seu thumbnail não atrapalhe o vídeo com elementos sensiveis a olho nú
- **🎨 Creative I.A.nalysis** : um spa e clínica para melhorar o seu thumnail de acordo com o seu Titulo e Descrição
- **🚀 Data Stories** : Navegue por histórias de dados e insights do seu canal
- **📊 Analytics** : Análise de dados avançadas do seu canal
- **🎵 Playlists** : Tudo sobre playlists do seu canal
- **🧪 3D Slope** : data science Lab para Nerds

    """)

    st.divider()