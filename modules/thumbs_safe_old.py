#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-04-19: Updated "AI" to "IA" to match Portuguese language
# 2024-04-19: Updated title to "Creators Engine AI" and added rainbow dividers for better section separation
# 2024-04-19: Renamed "Labels Detectados" to "Elementos Encontrados" and removed redundant "already processed" labels
# 2024-04-14: Removed width parameter from buttons since it's not supported
# 2024-04-14: Fixed image and button parameters to use width instead of use_container_width
# 2024-03-27: Página principal do Computer Vision AI
"""

import base64
import logging
import tempfile
from pathlib import Path

import numpy as np
import openai
import pandas as pd
import requests
import streamlit as st
from google.cloud import vision_v1
from google.protobuf.json_format import MessageToDict

from components.tables import render_labels_table, render_safesearch_table
from utils.config import LIKELIHOOD_VALUES, YOUTUBE_THUMBNAIL_URL
from utils.gcs_uploader import (
    check_image_processed,
    upload_to_gcs,
    upload_vision_results,
)
from utils.google_tag_manager import inject_gtm
from utils.validation import (
    validate_image_size,
    validate_image_url,
    validate_youtube_id,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_image_with_vision_ai(content: bytes) -> dict:
    """
    Processa uma imagem com o Vision AI.

    Args:
        content (bytes): Conteúdo da imagem

    Returns:
        dict: Resultados da análise
    """
    # Criar cliente Vision AI
    client = vision_v1.ImageAnnotatorClient()

    # Criar imagem para o Vision AI
    image = vision_v1.Image(content=content)

    # Configurar recursos desejados
    features = [
        vision_v1.Feature(type_=vision_v1.Feature.Type.SAFE_SEARCH_DETECTION),
        vision_v1.Feature(type_=vision_v1.Feature.Type.LABEL_DETECTION),
    ]

    # Fazer requisição
    request = vision_v1.AnnotateImageRequest(image=image, features=features)

    # Processar imagem
    response = client.annotate_image(request=request)

    # Converter resposta para dicionário
    return MessageToDict(response._pb)


def fetch_image_from_url(url: str) -> bytes:
    """
    Baixa uma imagem de uma URL.

    Args:
        url (str): URL da imagem

    Returns:
        bytes: Conteúdo da imagem
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def analyze_with_second_api(image_content: bytes) -> dict:
    """
    Analyze image using OpenAI's Moderation API.

    Args:
        image_content (bytes): Image content to analyze

    Returns:
        dict: Analysis results from OpenAI
    """
    try:
        # Save image to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(image_content)

        # Encode the image to base64
        b64_image = base64.b64encode(Path(temp_path).read_bytes()).decode("utf-8")

        # Initialize OpenAI client
        client = openai.OpenAI()

        # Call the moderation API
        moderation_result = client.moderations.create(
            model="omni-moderation-2024-09-26",
            input=[
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                }
            ],
        )

        # Convert result to dict for JSON serialization
        result_dict = moderation_result.model_dump()

        # Clean up temporary file
        Path(temp_path).unlink(missing_ok=True)

        return {"status": "success", "data": result_dict}

    except Exception as e:
        logger.error(f"Error in OpenAI moderation: {str(e)}", exc_info=True)
        return {"status": "error", "message": str(e)}


def display_analysis_results(results, is_reprocessed=False):
    """
    Exibe os resultados da análise de imagem.

    Args:
        results (dict): Resultados da análise
        is_reprocessed (bool): Se a imagem foi reprocessada
    """
    # Exibir resultados SafeSearch
    st.subheader("Análise de Conteúdo Sensível", divider="rainbow")
    if "safeSearchAnnotation" in results:
        # Get the SafeSearch scores
        safesearch_data = results["safeSearchAnnotation"]

        # Map likelihood strings to numeric values using the same mapping from LIKELIHOOD_VALUES
        scores = []
        for category, likelihood in safesearch_data.items():
            if likelihood in LIKELIHOOD_VALUES:
                scores.append(LIKELIHOOD_VALUES[likelihood]["value"])

        # Render the table
        render_safesearch_table(safesearch_data)

        # Add celebration effect based on scores
        if any(score >= 3 for score in scores):
            st.snow()
            st.toast("Cuidado! Este thumbnail pode atrapalhar o seu vídeo!", icon="🚨")
        else:
            st.balloons()
            st.toast("Ótimo! Este thumbnail pode ser bem aceito!", icon="😎")
    else:
        st.warning("Não foi possível realizar análise de conteúdo sensível.")

    # Exibir Labels detectados
    st.subheader("Elementos Encontrados", divider="rainbow")
    if "labelAnnotations" in results:
        # Não adicionar mais o label de reprocessamento
        labels_to_show = list(results["labelAnnotations"])
        render_labels_table(labels_to_show)
    else:
        st.warning("Não foi possível detectar elementos na imagem.")

    # Display second API analysis
    st.divider()
    st.subheader("Teste - OpenAI Content Moderation API", divider="rainbow")

    if st.session_state.image_content:
        with st.spinner("Processando com 2a API..."):
            try:
                second_api_results = analyze_with_second_api(
                    st.session_state.image_content
                )
                # st.json(second_api_results)
                # or use a function :
                display_openai_results(second_api_results)

            except Exception as e:
                st.error(f"Erro ao processar com a 2a API: {str(e)}")


def display_openai_results(results, use_log_scale: bool = False):
    """
    Exibe os resultados da análise da OpenAI Moderation API.

    Args:
        results (dict): Resultados da análise da API
        use_log_scale (bool): Se True, usa escala logarítmica para a barra de progresso
    """
    if "data" not in results:
        st.warning("Dados de análise não encontrados na resposta.")
        return

    try:
        # Get the moderation results
        res = results["data"]["results"][0]
        categories = res["categories"]
        scores = res["category_scores"]

        # Display flagged status
        st.subheader("Status da Moderação", divider="rainbow")
        flagged = res.get("flagged", False)
        status_emoji = "❌" if flagged else "✅"
        status_text = (
            "Conteúdo sinalizado como inadequado" if flagged else "Conteúdo aprovado"
        )
        st.write(f"{status_emoji} **{status_text}**")

        # Prepare data for the tables
        table_data = []
        for category, is_flagged in categories.items():
            risk_score = scores.get(category, 0)
            safety_score = 1 - risk_score  # Convert to safety score (0-1)
            table_data.append(
                {
                    "Categoria": category.replace("_", " ").title(),
                    "Status": "✅ Aprovado" if not is_flagged else "❌ Sinalizado",
                    "Risco (%)": risk_score * 100,  # Store as percentage
                    "Segurança (%)": safety_score * 100,  # Store as percentage
                }
            )

        # Sort by risk score descending
        table_data.sort(key=lambda x: x["Risco (%)"], reverse=True)

        # Create DataFrames for both views
        df_detailed = pd.DataFrame(table_data)

        # --- Detailed View ---
        st.subheader("Análise Detalhada", divider="rainbow")

        # Apply styling for the detailed view
        def highlight_flagged(val):
            return "background-color: #ffdddd" if val == "❌ Sinalizado" else ""

        # Create a copy of the detailed view without the safety score
        df_detailed_view = df_detailed.drop(columns=["Segurança (%)"]).copy()

        # Fixed scale for better color comparison (0% to 10%)
        styled_df = (
            df_detailed_view.style.apply(
                lambda x: [highlight_flagged(val) for val in x], subset=["Status"]
            )
            .background_gradient(
                subset=["Risco (%)"],
                cmap="PuBu",
                vmin=0,
                vmax=10,  # Fixed scale up to 10%
            )
            .format({"Risco (%)": "{:.2f}%"})
        )

        st.dataframe(styled_df, use_container_width=True, hide_index=True)

        # Show warning if any category is flagged
        if flagged:
            st.warning(
                "⚠️ Este conteúdo contém elementos que podem ser considerados inadequados."
            )

        # --- Summary View ---
        st.divider()
        st.subheader("Visão Resumida", divider="rainbow")

        # Calculate max value for scaling
        max_risk = max(x["Risco (%)"] for x in table_data) if table_data else 10

        # Apply log scale if requested
        if use_log_scale and max_risk > 0:
            # Add small epsilon to avoid log(0)
            log_scale = np.log10(max_risk + 0.0001) + 1
            max_scale = 10**log_scale
        else:
            max_scale = max(10, max_risk)  # Minimum scale of 10%

        # Display the table with progress bars
        st.dataframe(
            df_detailed.rename(columns={"Risco (%)": "Risco"}),
            column_config={
                "Categoria": "Categoria",
                "Status": "Status",
                "Risco": st.column_config.ProgressColumn(
                    "Segurança",
                    help="Quanto maior a barra, mais seguro é o conteúdo",
                    format="%.0f%%",
                    min_value=0,
                    max_value=100,  # Always show as percentage
                ),
            },
            hide_index=True,
            use_container_width=True,
        )

        # Show current scale info
        scale_type = "logarítmica" if use_log_scale else "linear"
        st.caption(f"Escala: {scale_type} | Máximo risco: {max_risk:.2f}%")

    except Exception as e:
        st.error(f"Erro ao processar os resultados: {str(e)}")
        with st.expander("Ver resposta bruta para depuração"):
            st.json(results)


def render():
    """
    Renderiza a página do Vision AI.
    """

    # Inject GTM script
    inject_gtm()

    st.subheader("🧠 CE.IA - Análise de Miniaturas/Thumbnails - Conteúdos Sensíveis")
    # st.subheader("Inteligência artificial a serviço dos criadores") #, divider="rainbow")

    # Inicializar estado da sessão
    if "image_content" not in st.session_state:
        st.session_state.image_content = None
        st.session_state.image_source = None
        st.session_state.analysis_results = None
        st.session_state.selected_input = None
        st.session_state.is_reprocessed = False
        st.session_state.image_gcs_path = None

    # Botões para seleção do método de entrada
    st.divider()
    st.write("##### Selecione o método de entrada:")
    col1, col2, col3 = st.columns(3)

    with col1:
        upload_active = st.session_state.selected_input == "upload"
        if st.button(
            "📤 Upload de Arquivo", type="primary" if upload_active else "secondary"
        ):
            st.session_state.selected_input = "upload"
            st.session_state.image_content = None
            st.session_state.is_reprocessed = False
            st.session_state.image_gcs_path = None

    with col2:
        url_active = st.session_state.selected_input == "url"
        if st.button("🔗 URL da Imagem", type="primary" if url_active else "secondary"):
            st.session_state.selected_input = "url"
            st.session_state.image_content = None
            st.session_state.is_reprocessed = False
            st.session_state.image_gcs_path = None

    with col3:
        youtube_active = st.session_state.selected_input == "youtube"
        if st.button(
            "▶️ ID do YouTube", type="primary" if youtube_active else "secondary"
        ):
            st.session_state.selected_input = "youtube"
            st.session_state.image_content = None
            st.session_state.is_reprocessed = False
            st.session_state.image_gcs_path = None

    st.divider()

    # Mostrar input apropriado baseado na seleção
    if st.session_state.selected_input == "upload":
        uploaded_file = st.file_uploader(
            "Escolha uma imagem",
            type=["png", "jpg", "jpeg"],
            help="Tamanho máximo: 2MB",
        )

        if uploaded_file:
            # Validar tamanho
            valid, error = validate_image_size(uploaded_file.size)
            if not valid:
                st.error(error)
            else:
                st.session_state.image_content = uploaded_file.read()
                st.session_state.image_source = "upload"
                st.session_state.original_filename = uploaded_file.name

    elif st.session_state.selected_input == "url":
        url = st.text_input("URL da imagem:")
        if url:
            if not validate_image_url(url):
                st.error("URL inválida. Certifique-se que é uma imagem (jpg, png, etc)")
            else:
                try:
                    st.session_state.image_content = fetch_image_from_url(url)
                    st.session_state.image_source = "url"
                    st.session_state.original_filename = url.split("/")[-1]
                except Exception as e:
                    st.error(f"Erro ao baixar imagem: {str(e)}")

    elif st.session_state.selected_input == "youtube":
        youtube_input = st.text_input(
            "ID ou URL do vídeo:",
            help="Ex: dQw4w9WgXcQ ou https://youtu.be/dQw4w9WgXcQ",
            autocomplete="on",
        )
        if youtube_input:
            valid, youtube_id = validate_youtube_id(youtube_input)
            if not valid:
                st.error(youtube_id)  # youtube_id contém a mensagem de erro
            else:
                try:
                    url = YOUTUBE_THUMBNAIL_URL.format(youtube_id)
                    st.session_state.image_content = fetch_image_from_url(url)
                    st.session_state.image_source = "youtube"
                    st.session_state.original_filename = f"{youtube_id}.jpg"
                except Exception as e:
                    st.error(f"Erro ao baixar thumbnail: {str(e)}")

    # Se temos uma imagem para processar
    if st.session_state.image_content:
        # Exibir preview
        st.image(st.session_state.image_content, width=800)

        # Verificar se temos email do usuário
        if "user_email" not in st.session_state:
            st.error("Erro de autenticação: Email do usuário não encontrado na sessão")
            return

        # # Exibir informações de depuração
        # with st.expander("Informações de diagnóstico", expanded=False):
        #     import hashlib
        #     file_hash = hashlib.sha256(st.session_state.image_content).hexdigest()
        #     st.write(f"SHA-256 Hash (completo): {file_hash}")
        #     st.write(f"SHA-256 Hash (8 primeiros): {file_hash[:8]}")
        #     st.write(f"Tamanho da imagem: {len(st.session_state.image_content)} bytes")
        #     st.write(f"Email do usuário: {st.session_state.user_email}")
        #     st.write(f"Nome do arquivo: {getattr(st.session_state, 'original_filename', 'image.jpg')}")

        # Verificar cache
        is_cached, cached_results = check_image_processed(
            st.session_state.user_email, st.session_state.image_content
        )

        if is_cached:
            # A imagem já existe no GCS e foi processada anteriormente
            st.success(
                "✅ Esta imagem já foi processada anteriormente. Carregando resultados existentes."
            )
            results = cached_results
            st.session_state.is_reprocessed = True
            st.session_state.analysis_results = results

            # Mostrar os resultados
            display_analysis_results(results, is_reprocessed=True)
        else:
            # Imagem nova, mostrar botão de análise
            if st.button("Analisar Imagem", type="primary"):
                with st.spinner("Processando imagem..."):
                    try:
                        # Fazer upload da imagem para GCS
                        _, gcs_path = upload_to_gcs(
                            st.session_state.user_email,
                            st.session_state.image_content,
                            getattr(st.session_state, "original_filename", "image.jpg"),
                        )

                        # Registrar o caminho da imagem
                        logger.info(f"Uploaded image to: {gcs_path}")

                        # Salvar o caminho GCS
                        st.session_state.image_gcs_path = gcs_path

                        # Processar com Vision AI
                        results = process_image_with_vision_ai(
                            st.session_state.image_content
                        )

                        # Salvar resultados
                        results_path = upload_vision_results(
                            st.session_state.user_email, results, gcs_path
                        )

                        # Registrar o caminho dos resultados
                        logger.info(f"Saved results to: {results_path}")

                        st.session_state.analysis_results = results
                        st.session_state.is_reprocessed = False

                        # Mostrar os resultados
                        display_analysis_results(results, is_reprocessed=False)
                    except Exception as e:
                        logger.exception("Error processing image")
                        st.error(f"Erro ao processar imagem: {str(e)}")
                        return
