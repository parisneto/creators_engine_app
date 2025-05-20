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

import logging

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

    # # Exibir JSON bruto em expander
    # st.divider()
    # with st.expander("Ver JSON completo"):
    #     st.json(results)
