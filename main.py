"""Script principal para execução do Pipeline."""

import os
import pandas as pd

from src.pipeline import SpatialDistrictResolver
from src.analytics import RealEstateAnalytics
from src.visualization import RealEstateDashboard

BRUTO_DATA_PATH = os.path.join("data", "bruto", "alvaras_por_lote.xlsx")
TRATADO_DATA_PATH = os.path.join("data", "tratado", "alvaras_mapeados.xlsx")
FIGURE_OUTPUT_PATH = os.path.join("reports", "figures", "painel_4_fenomenos_gentrificacao.png")


def main():
    print("Executando Pipeline")
    if not os.path.exists(BRUTO_DATA_PATH):
        raise FileNotFoundError(f"Arquivo não encontrado em: {BRUTO_DATA_PATH}")

    df_raw = pd.read_excel(BRUTO_DATA_PATH)
    resolver = SpatialDistrictResolver(cutoff_fuzzy=0.85)
    df_mapped = resolver.execute(df_raw)

    os.makedirs(os.path.dirname(TRATADO_DATA_PATH), exist_ok=True)
    df_mapped.to_excel(TRATADO_DATA_PATH, index=False)

    print("Preparando Métricas")
    analytics = RealEstateAnalytics()
    df_clean = analytics.prepare_dataset(df_mapped)

    print("Gerando Dashboard de Visualização")
    dashboard = RealEstateDashboard()
    dashboard.build_panel(df_clean, output_path=FIGURE_OUTPUT_PATH)

    print("\nProcesso concluído com sucesso!")
    print("Dados Mapeados: {PROCESSED_DATA_PATH}")
    print("Dashboard Salvo: {FIGURE_OUTPUT_PATH}")


if __name__ == "__main__":
    main()