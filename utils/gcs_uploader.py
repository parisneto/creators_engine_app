#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-03-27: Utilitário para upload de arquivos no Google Cloud Storage
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from google.cloud import storage

from utils.config import GCS_BUCKET, GCS_VISION_PREFIX

# Configure logging
logger = logging.getLogger(__name__)



def has_required_schema(data: Dict[str, Any]) -> bool:
    """
    Check if the result has all required top-level keys.

    Args:
        data: Dictionary with vision and moderation results

    Returns:
        bool: True if all required keys are present
    """
    required_keys = {"labelAnnotations", "safeSearchAnnotation", "openaiModeration"}
    return all(key in data for key in required_keys)


def get_file_hash(content: bytes) -> str:
    """
    Gera um hash SHA-256 do conteúdo do arquivo.

    Args:
        content (bytes): Conteúdo do arquivo

    Returns:
        str: Hash SHA-256 em hexadecimal
    """
    return hashlib.sha256(content).hexdigest()


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza um nome de arquivo para uso seguro no GCS.

    Args:
        filename (str): Nome original do arquivo

    Returns:
        str: Nome de arquivo sanitizado
    """
    # Remove invalid characters
    valid_chars = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    sanitized = "".join(c for c in filename if c in valid_chars)

    # Ensure filename isn't too long
    if len(sanitized) > 50:
        base, ext = os.path.splitext(sanitized)
        sanitized = base[:46] + ext if ext else base[:50]

    return sanitized


def check_image_exists(user_email: str, file_hash: str) -> tuple[bool, dict, str]:
    """
    Verifica se uma imagem com o mesmo hash já existe no GCS.

    Args:
        user_email (str): Email do usuário
        file_hash (str): Hash SHA-256 do arquivo

    Returns:
        tuple[bool, dict, str]: (Existe?, Resultados se encontrado, Caminho GCS se encontrado)
    """
    # Criar cliente GCS
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)

    # Prefixo para o usuário
    user_prefix = f"{GCS_VISION_PREFIX}/{user_email}"

    # Procurar diretamente por arquivos que contenham o hash (primeiros 8 caracteres)
    hash_short = file_hash[:8]

    print(f"Checking for existing image with hash: {hash_short}")

    # Lista todos os arquivos na pasta de imagens do usuário
    blobs = list(client.list_blobs(bucket, prefix=f"{user_prefix}/images/"))

    # Procurar por arquivo com o mesmo hash (primeiros 8 chars)
    for blob in blobs:
        if hash_short in blob.name:
            print(f"Found existing image: {blob.name}")
            # Extrair nome do arquivo de imagem
            image_filename = os.path.basename(blob.name)

            # Construir o caminho do arquivo de resultados esperado
            results_path = f"{user_prefix}/results/{image_filename}_results.json"

            # Verificar se o arquivo de resultados existe
            results_blob = bucket.blob(results_path)
            if results_blob.exists():
                # Carregar resultados
                try:
                    results = json.loads(results_blob.download_as_string())
                    return True, results, blob.name
                except Exception as e:
                    print(f"Error loading results: {e}")

    print("No existing image found")
    return False, None, None


def upload_to_gcs(
    user_email: str, content: bytes, original_filename: str
) -> tuple[str, str]:
    """
    Faz upload de um arquivo para o Google Cloud Storage.

    Args:
        user_email (str): Email do usuário
        content (bytes): Conteúdo do arquivo
        original_filename (str): Nome original do arquivo

    Returns:
        tuple[str, str]: (URL pública do arquivo, caminho do arquivo no GCS)
    """
    # Criar cliente GCS
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)

    # Gerar hash do arquivo
    file_hash = get_file_hash(content)

    # Verificar se já existe um arquivo com o mesmo hash
    exists, _, existing_path = check_image_exists(user_email, file_hash)
    if exists:
        # Se já existe, retornar o caminho existente
        blob = bucket.blob(existing_path)
        return blob.public_url, f"gs://{GCS_BUCKET}/{existing_path}"

    # Sanitizar nome do arquivo
    sanitized_filename = sanitize_filename(original_filename)

    # Gerar nome final de arquivo com timestamp e hash
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file_hash[:8]}_{sanitized_filename}"

    # Gerar caminho completo
    blob_path = f"{GCS_VISION_PREFIX}/{user_email}/images/{filename}"

    # Fazer upload do arquivo
    blob = bucket.blob(blob_path)
    blob.upload_from_string(content)
    # st.toast('Your edited image was saved!', icon='😍')

    return blob.public_url, f"gs://{GCS_BUCKET}/{blob_path}"


def upload_vision_results(
    user_email: str,
    results: dict,
    image_path: str,
    openai_results: Optional[dict] = None,
) -> str:
    """
    Faz upload dos resultados do Vision AI e OpenAI Moderation para o GCS.

    Args:
        user_email (str): Email do usuário
        results (dict): Resultados do Vision AI
        image_path (str): Caminho completo da imagem no GCS
        openai_results (dict, optional): Resultados do OpenAI Moderation

    Returns:
        str: Caminho do arquivo de resultados no GCS
    """
    # Criar cliente GCS
    client = storage.Client()
    bucket = client.bucket(GCS_BUCKET)

    # Extrair nome do arquivo de imagem do caminho
    image_filename = os.path.basename(image_path)

    # Gerar nome do arquivo de resultados
    results_filename = f"{image_filename}_results.json"

    # Gerar caminho completo
    blob_path = f"{GCS_VISION_PREFIX}/{user_email}/results/{results_filename}"

    # Verificar se já existe um arquivo de resultados
    existing_results = {}
    try:
        blob = bucket.blob(blob_path)
        if blob.exists():
            existing_results = json.loads(blob.download_as_text())

            # Criar backup do arquivo existente
            backup_blob = bucket.blob(f"{blob_path}_old")
            if not backup_blob.exists():
                backup_blob.upload_from_string(
                    json.dumps(existing_results, indent=2),
                    content_type="application/json",
                )
    except Exception as e:
        logger.warning(f"Could not read existing results: {e}")

    # Preparar resultados para upload
    upload_data = {
        **existing_results,  # Manter dados existentes
        "labelAnnotations": results.get("labelAnnotations", []),
        "safeSearchAnnotation": results.get("safeSearchAnnotation", {}),
    }

    # Adicionar resultados do OpenAI se fornecidos
    if openai_results:
        upload_data["openaiModeration"] = openai_results

    # Fazer upload dos resultados
    blob = bucket.blob(blob_path)
    blob.upload_from_string(
        json.dumps(upload_data, indent=2), content_type="application/json"
    )

    logger.info(f"Results uploaded to gs://{GCS_BUCKET}/{blob_path}")
    return f"gs://{GCS_BUCKET}/{blob_path}"


def check_image_processed(user_email: str, content: bytes) -> tuple[bool, dict]:
    """
    Verifica se uma imagem já foi processada anteriormente.

    Args:
        user_email (str): Email do usuário
        content (bytes): Conteúdo da imagem

    Returns:
        tuple[bool, dict]: (True e resultados se encontrado, False e None se não)
    """
    # Gerar hash da imagem
    file_hash = get_file_hash(content)

    # Verificar se a imagem existe
    exists, results, _ = check_image_exists(user_email, file_hash)

    return exists, results
