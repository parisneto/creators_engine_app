#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-19: Removed reprocessed image indicator from labels table
# 2024-04-14: Fixed dataframe parameter to remove use_container_width
# 2024-03-27: Componentes de tabela para exibição de resultados
"""

import streamlit as st
import pandas as pd


def likelihood_color_map():
    """Return a dictionary mapping likelihood values to colors"""
    return {
        0: "#999999",  # Light yellow - Unknown
        1: "#CCFFCC",  # Light green - Very Unlikely
        2: "#E6FFCC",  # Yellowish green - Unlikely
        3: "#FFFFCC",  # Very light yellow - Possible
        4: "#FFEBCC",  # Light orange - Likely
        5: "#FFCCCC",  # Light red - Very Likely
    }


def render_safesearch_table(safesearch_data):
    """
    Render SafeSearch results as a Streamlit dataframe with color highlighting.

    Args:
        safesearch_data: Dictionary of SafeSearch results
    """
    # Import inside function to avoid circular import
    from utils.config import SAFESEARCH_CATEGORIES, LIKELIHOOD_VALUES

    # Create data for table
    rows = []

    for category, likelihood in safesearch_data.items():
        if category in SAFESEARCH_CATEGORIES:
            # Get category info
            label = SAFESEARCH_CATEGORIES[category]['label']
            desc = SAFESEARCH_CATEGORIES[category]['description']

            # Get likelihood info
            likelihood_info = LIKELIHOOD_VALUES.get(likelihood, {
                'name': 'Desconhecido',
                'value': 0,
                'description': 'Valor não reconhecido'
            })

            # Add to rows
            rows.append({
                'Categoria': label,
                'Probabilidade': likelihood_info['name'],
                'Valor Numérico': likelihood_info['value'],
                'Descrição': desc,
                '_value': likelihood_info['value']  # Used for styling
            })

    # Create dataframe
    if rows:
        df = pd.DataFrame(rows)

        # Get color map
        colors = likelihood_color_map()

        # Create HTML table for colored display
        html_table = "<table style='width:100%; border-collapse: collapse;'>"
        html_table += "<tr><th>Categoria</th><th>Probabilidade</th><th>Valor Numérico</th><th>Descrição</th></tr>"

        for _, row in df.iterrows():
            value = row['_value']
            bg_color = colors[value]
            html_table += f"<tr style='background-color: {bg_color}'>"
            html_table += f"<td>{row['Categoria']}</td>"
            html_table += f"<td>{row['Probabilidade']}</td>"
            html_table += f"<td>{row['Valor Numérico']}</td>"
            html_table += f"<td>{row['Descrição']}</td>"
            html_table += "</tr>"

        html_table += "</table>"

        # Display HTML table
        st.markdown(html_table, unsafe_allow_html=True)

        # Alternative approach using dataframe without styling
        # st.dataframe(
        #     df[['Categoria', 'Probabilidade', 'Descrição']],
        #     hide_index=True
        # )
        # add a markdown text with the following text:
            # st.markdown("""
            # <div style="text-align: justify; font-size: 14px;">
            # <p>&nbsp;</p>
            # <p>
            # A análise de escala acima, listada pelo nosso processo de validação da imagem, é uma forma de representarmos como que o YouTube possivelmente "enxerga" a imagem do thumbnail.
            # Um dos elementos mais importante para que o vídeo seja publicado na primeira página e sugerido para o internauta, é a qualidade da thumbnail.
            # Ao ser classicado com qualquer elemento diferente de VERY UNLIKELY, o engine do YouTube talvez não selecione o vídeo para usuários não conhecidos por ele.
            # Em estudos realizados, entre 40% e 60% das pessoas acessam a plataforma sem estarem conectadas na conta do Google.
            # Lembre-se que um vídeo pode ser sugerido em qualquer lugar do mundo, portanto diferenças culturais podem ser o maior desafio para a confecção da imagem.
            # </p>
            # </div>
            # """, unsafe_allow_html=True)

        st.warning("Atenção, qualquer elemento com valor acima de 3 não é recomendado")
        # st.divider()
        st.markdown("""
A análise de escala acima, listada pelo nosso processo de validação da imagem, é uma forma de representarmos como que o YouTube possivelmente "enxerga" a imagem do thumbnail.
Um dos elementos mais importante para que o vídeo seja publicado na primeira página e sugerido para o internauta, é a qualidade da thumbnail.
Ao ser classicado com qualquer elemento diferente de VERY UNLIKELY, o engine do YouTube talvez não selecione o vídeo para usuários não conhecidos por ele.
Em estudos realizados, entre 40% e 60% das pessoas acessam a plataforma sem estarem conectadas na conta do Google.
Lembre-se que um vídeo pode ser sugerido em qualquer lugar do mundo, portanto diferenças culturais podem ser o maior desafio para a confecção da imagem.
        """)
        st.divider()


        # # Display a color legend
        st.subheader("Escala de Probabilidade")
        render_likelihood_scale()

    else:
        st.warning("Não há dados de SafeSearch disponíveis.")


def render_likelihood_scale():
    """
    Render likelihood scale as a Streamlit dataframe with color coding.
    """
    # Import inside function to avoid circular import
    from utils.config import LIKELIHOOD_VALUES

    # Create data for table
    rows = []

    # Sort by value for better display
    sorted_likelihoods = sorted(
        LIKELIHOOD_VALUES.items(),
        key=lambda x: x[1]['value']
    )

    # Get color map
    colors = likelihood_color_map()

    for key, info in sorted_likelihoods:
        rows.append({
            'Valor': key,
            'Significado': info['description'],
            'Valor Numérico':info['value'] ,
            '_value': info['value']  # Used for styling
        })

    # Create dataframe
    if rows:
        df = pd.DataFrame(rows)

        # Create HTML table for colored display

        html_table = "<table style='width:100%; border-collapse: collapse;'>"
        html_table += "<tr><th>Valor</th><th>Significado</th><th>Valor Numérico</th></tr>"

        for _, row in df.iterrows():
            value = row['_value']
            bg_color = colors[value]
            html_table += f"<tr style='background-color: {bg_color}'>"
            html_table += f"<td>{row['Valor']}</td>"
            html_table += f"<td>{row['Significado']}</td>"
            html_table += f"<td>{row['Valor Numérico']}</td>"
            html_table += "</tr>"

        html_table += "</table>"


        # Display HTML table
        st.markdown(html_table, unsafe_allow_html=True)



        # Alternative approach using dataframe without styling
        # st.dataframe(
        #     df[['Valor', 'Significado', 'Descrição']],
        #     hide_index=True
        # )
    else:
        st.warning("Não há informações de escala de probabilidade disponíveis.")


def render_labels_table(labels):
    """
    Render detected labels as a Streamlit dataframe.

    Args:
        labels: List of label dictionaries
    """
    # Create data for table
    rows = []

    for i, label in enumerate(labels):
        # Get label data with defaults for safety
        description = label.get('description', 'N/A')

        # Special handling for numeric scores
        score = 0.0
        if 'score' in label:
            try:
                score = float(label['score'])
            except (ValueError, TypeError):
                score = 0.0

        # Format confidence level
        confidence = "Alta" if score > 0.8 else "Média" if score > 0.5 else "Baixa"

        # Add to rows
        rows.append({
            'Label': description,
            'Score': f"{score:.1%}",
            'Confiança': confidence
        })

    # Create dataframe
    if rows:
        df = pd.DataFrame(rows)

        # Display the table
        st.dataframe(
            df,
            hide_index=True
        )
    else:
        st.warning("Não há labels detectados disponíveis.")