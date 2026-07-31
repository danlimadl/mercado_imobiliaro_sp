"""Módulo de cálculo de métricas imobiliárias."""

import logging
from typing import List, Optional
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RealEstateAnalytics:

    DEFAULT_BINS = [0, 30, 45, 70, 1000]
    DEFAULT_LABELS = ['<30m²', '30-45m²', '45-70m²', '>70m²']

    def __init__(self, bins: Optional[List[float]] = None, labels: Optional[List[str]] = None):
        self.bins = bins or self.DEFAULT_BINS
        self.labels = labels or self.DEFAULT_LABELS
        self.logger = logging.getLogger(self.__class__.__name__)

    def prepare_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filtra outliers e cria a variável categórica de faixa de tamanho."""
        self.logger.info("Removendo outliers e criando faixas de metragem...")
        
        df_clean = df[df['ind_outlier'] == False].copy()
        df_clean['faixa_tamanho'] = pd.cut(
            df_clean['area_da_unidade'], 
            bins=self.bins, 
            labels=self.labels
        )
        return df_clean

    @staticmethod
    def calculate_studio_evolution(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula o share percentual de unidades por faixa de tamanho ao longo dos anos."""
        studios_time = (
            df.groupby(['ano_execucao', 'faixa_tamanho'], observed=False)['n_unidades']
            .sum()
            .unstack(fill_value=0)
        )
        return studios_time.div(studios_time.sum(axis=1), axis=0) * 100

    @staticmethod
    def calculate_market_vs_social(df: pd.DataFrame) -> pd.DataFrame:
        """Calcula a produção anual de unidades entre Mercado (ERM) e Social (ERP/HIS)."""
        return (
            df.groupby(['ano_execucao', 'categoria_de_uso_grupo'])['n_unidades']
            .sum()
            .unstack(fill_value=0)
        )