#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# 2024-03-27: Configurações compartilhadas do MDM Vision AI App
"""

import re
import os
from os import environ

env = os.getenv("APPMODE")
if env == "DEV":
    APPMODE = "DEV"
elif env == "PROD":
    APPMODE = "PROD"
else:
    APPMODE = "UNKNOWN"

# Configurações de cores para SafeSearch
LOW_RISK_COLOR = "#33FF00"  # Verde para baixo risco (valor 1)
HIGH_RISK_COLOR = "#FF0066"  # Vermelho para alto risco (valor 5)
UNKNOWN_COLOR = "#FFFF00"    # Amarelo para desconhecido (valor 0)

# Configurações de imagem
MAX_IMAGE_SIZE_MB = 2  # Tamanho máximo de imagem em MB
YOUTUBE_THUMBNAIL_URL = "https://img.youtube.com/vi/{}/maxresdefault.jpg"

#GCP
GCP_PROJECT_ID = "fleet-gamma-448616-m1"
GCP_REGION = "us-central1"

# Configurações do GCS
GCS_BUCKET = "creators_engine_production"
GCS_VISION_PREFIX = "creators_engine_vision"


def sanitize_email_for_path(email: str) -> str:
    """
    Sanitiza um email para uso em caminhos do GCS.

    Args:
        email (str): Email do usuário

    Returns:
        str: Email sanitizado para uso em paths
    """
    # Remover caracteres não permitidos em paths do GCS
    sanitized = re.sub(r'[^a-zA-Z0-9-_.]', '_', email)
    return sanitized.lower()

def get_user_gcs_path(email: str) -> str:
    """
    Gera o caminho base do usuário no GCS.

    Args:
        email (str): Email do usuário

    Returns:
        str: Caminho base do usuário no GCS
    """
    sanitized_email = sanitize_email_for_path(email)
    return f"gs://{GCS_BUCKET}/{GCS_VISION_PREFIX}/{sanitized_email}"

# Regex para extrair ID do YouTube
YOUTUBE_URL_REGEX = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'

# Dicionário de valores de probabilidade
LIKELIHOOD_VALUES = {
    'UNKNOWN': {'value': 0, 'name': 'Desconhecido', 'description': 'Não foi possível determinar'},
    'VERY_UNLIKELY': {'value': 1, 'name': 'Muito Improvável', 'description': 'Altamente improvável'},
    'UNLIKELY': {'value': 2, 'name': 'Improvável', 'description': 'Improvável'},
    'POSSIBLE': {'value': 3, 'name': 'Possível', 'description': 'Possibilidade moderada'},
    'LIKELY': {'value': 4, 'name': 'Provável', 'description': 'Provável'},
    'VERY_LIKELY': {'value': 5, 'name': 'Muito Provável', 'description': 'Altamente provável'}
}

# Categorias SafeSearch
SAFESEARCH_CATEGORIES = {
    'adult': {
        'label': 'Conteúdo Adulto',
        'description': 'Representa a probabilidade de conteúdo adulto para a imagem. Conteúdo adulto pode conter elementos como nudez, imagens ou desenhos pornográficos, ou atividades sexuais.'
    },
    'spoof': {
        'label': 'Plágio ou Paródia',
        'description': 'Probabilidade de falsificação. A probabilidade de uma modificação ter sido feita na imagem para torná-la engraçada ou ofensiva.'
    },
    'medical': {
        'label': 'Médico',
        'description': 'Probabilidade de que este seja um conteúdo médico ou clínico.'
    },
    'violence': {
        'label': 'Violência',
        'description': 'Probabilidade de que esta imagem contenha conteúdo violento. Conteúdo violento pode incluir morte, danos graves ou ferimentos a indivíduos ou grupos de indivíduos.'
    },
    'racy': {
        'label': 'Picante ou Atrevido',
        'description': 'Conteúdo provocativo ou sugestivo. Conteúdo picante pode incluir (mas não se limita a) roupas curtas ou transparentes, nudez estrategicamente coberta, poses obscenas ou provocativas ou closes de áreas sensíveis do corpo.'
    }
}