import logging
import difflib
from typing import Optional
import pandas as pd

from src.config import DISTRITOS_SP, DICIONARIO_MANUAL, CENTRO_EXPANDIDO, COLUNAS_FINAIS
from src.utils import clean_text, extract_setor_quadra, extract_street_name

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SpatialDistrictResolver:
    """Realiza a limpeza e resolução encadeada (Multi-level Cascade) do Distrito Urbano."""

    def __init__(self, cutoff_fuzzy: float = 0.85):
        self.cutoff_fuzzy = cutoff_fuzzy
        self.logger = logging.getLogger(self.__class__.__name__)

    def _preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica higienização inicial e extração de chaves geográficas."""
        self.logger.info("Executando pré-processamento de texto e extração de chaves...")
        
        df = df.copy()
        df['bairro_limpo'] = df['bairro'].apply(clean_text)
        
        # Expansão de abreviações padrão
        df['bairro_limpo'] = (
            df['bairro_limpo']
            .str.replace(r'\bVL\b', 'VILA', regex=True)
            .str.replace(r'\bJD\b', 'JARDIM', regex=True)
        )

        df['setor_quadra'] = df['sql_incra'].apply(extract_setor_quadra)
        df['nome_rua'] = df['endereco_ultimo'].apply(extract_street_name)
        
        # Aplicação do Dicionário Manual
        df['bairro_preparado'] = df['bairro_limpo'].apply(
            lambda x: DICIONARIO_MANUAL.get(x, x)
        )
        return df

    def _match_direto_ou_fuzzy(self, bairro: str) -> Optional[str]:
        """Nível 1: Match Direto / Fuzzy Matching."""
        if not bairro:
            return None
        if bairro in DISTRITOS_SP:
            return bairro
        matches = difflib.get_close_matches(bairro, DISTRITOS_SP, n=1, cutoff=self.cutoff_fuzzy)
        return matches[0] if matches else None

    def execute(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """Executa a cascata de resolução (Nível 1 ao Nível 4) e filtragem."""
        df = self._preprocess(df_raw)

        # --- NÍVEL 1: Match Direto / Fuzzy ---
        self.logger.info("Nível 1: Match Direto/Fuzzy...")
        df['distrito_nivel1'] = df['bairro_preparado'].apply(self._match_direto_ou_fuzzy)

        # --- NÍVEL 2: Inferência por Quarteirão (Setor + Quadra) ---
        self.logger.info("Nível 2: Inferência por Quarteirão...")
        mapa_quarteirao = (
            df.dropna(subset=['distrito_nivel1'])
            .groupby('setor_quadra')['distrito_nivel1']
            .first()
            .to_dict()
        )
        df['distrito_nivel2'] = df['distrito_nivel1'].fillna(df['setor_quadra'].map(mapa_quarteirao))

        # --- NÍVEL 3: Inferência por Rua ---
        self.logger.info("Nível 3: Inferência por Nome da Rua...")
        mapa_rua = (
            df.dropna(subset=['distrito_nivel2'])
            .groupby('nome_rua')['distrito_nivel2']
            .first()
            .to_dict()
        )
        df['distrito_final'] = df['distrito_nivel2'].fillna(df['nome_rua'].map(mapa_rua)).fillna('REVISAO MANUAL')

        # --- NÍVEL 4: Inferência por Setor (3 Dígitos) ---
        self.logger.info("Nível 4: Inferência Dominante por Setor (3 dígitos)...")
        df['setor'] = df['setor_quadra'].apply(lambda x: x[:3] if x else None)
        
        df_resolvidos = df[df['distrito_final'] != 'REVISAO MANUAL']
        mapa_setor = (
            df_resolvidos.groupby('setor')['distrito_final']
            .apply(lambda x: x.mode()[0] if not x.mode().empty else None)
            .to_dict()
        )

        mask_revisao = df['distrito_final'] == 'REVISAO MANUAL'
        df['distrito_definitivo'] = df['distrito_final']
        df.loc[mask_revisao, 'distrito_definitivo'] = df.loc[mask_revisao, 'setor'].map(mapa_setor).fillna('SEM SALVACAO')

        # --- FILTRAGEM: Centro Expandido ---
        self.logger.info("Filtrando imóveis do Centro Expandido...")
        df_centro = df[df['distrito_definitivo'].isin(CENTRO_EXPANDIDO)].copy()
        
        self.logger.info(f"Sucesso: {len(df_centro)} alvarás localizados no Centro Expandido.")
        
        # Seleção de colunas finais tratadas
        return df_centro[COLUNAS_FINAIS]