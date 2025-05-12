#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-03-27: Funções de validação para o MDM Vision AI App
"""

import re
from utils.config import YOUTUBE_URL_REGEX, MAX_IMAGE_SIZE_MB

def validate_youtube_id(input_text: str) -> tuple[bool, str]:
    """
    Valida e extrai o ID do YouTube de uma URL ou ID direto.

    Args:
        input_text (str): URL do YouTube ou ID

    Returns:
        tuple[bool, str]: (sucesso, id ou mensagem de erro)
    """
    # Remover espaços
    input_text = input_text.strip()

    # Se for um ID direto (11 caracteres)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', input_text):
        return True, input_text

    # Se for uma URL
    match = re.match(YOUTUBE_URL_REGEX, input_text)
    if match:
        return True, match.group(1)

    return False, "ID ou URL do YouTube inválido"

def validate_image_size(file_size_bytes: int) -> tuple[bool, str]:
    """
    Valida o tamanho do arquivo de imagem.

    Args:
        file_size_bytes (int): Tamanho do arquivo em bytes

    Returns:
        tuple[bool, str]: (sucesso, mensagem de erro se falhar)
    """
    max_size_bytes = MAX_IMAGE_SIZE_MB * 1024 * 1024

    if file_size_bytes > max_size_bytes:
        return False, f"Imagem muito grande. Máximo permitido: {MAX_IMAGE_SIZE_MB}MB"

    return True, ""

def validate_image_url(url: str) -> bool:
    """
    Valida se a URL parece ser de uma imagem.

    Args:
        url (str): URL da imagem

    Returns:
        bool: True se parece ser uma URL de imagem válida
    """
    # Extensões de imagem comuns
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    return url.lower().endswith(image_extensions)