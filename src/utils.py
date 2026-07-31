"""Utilitários para normalização de texto."""

import re
import unicodedata
from typing import Optional
import pandas as pd


def clean_text(text: Optional[str]) -> str:
    """Normaliza texto: remove acentos, caracteres especiais e converte para caixa alta."""
    if pd.isna(text) or not text:
        return ""
    text_str = str(text).upper()
    text_normalized = ''.join(
        c for c in unicodedata.normalize('NFD', text_str) 
        if unicodedata.category(c) != 'Mn'
    )
    clean_str = re.sub(r'[^A-Z\s]', '', text_normalized)
    return ' '.join(clean_str.split())


def extract_setor_quadra(sql: Optional[str]) -> Optional[str]:
    """Extrai os 6 primeiros dígitos do código SQL/INCRA (Setor + Quadra)."""
    if pd.isna(sql):
        return None
    sql_clean = str(sql).replace('.', '').replace('-', '').strip()
    return sql_clean[:6] if len(sql_clean) >= 6 else None


def extract_street_name(endereco: Optional[str]) -> Optional[str]:
    """Extrai o nome do logradouro removendo prefixos comuns (Rua, Av, etc.)."""
    if pd.isna(endereco):
        return None
    end_limpo = clean_text(endereco)
    pattern = r'\b(PC|R|RUA|AV|AVENIDA|TRAVESSA|AL|ALAMEDA|ESTR|ESTRADA|PCA|PRACA)\b'
    end_limpo = re.sub(pattern, '', end_limpo)
    return ' '.join(end_limpo.split())
