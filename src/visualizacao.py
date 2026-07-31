"""Módulo para geração de dashboards e gráficos."""

import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from src.analytics import RealEstateAnalytics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RealEstateDashboard:
    """Gerencia a estilização e plotagem do painel analítico de 4 fenômenos."""

    def __init__(self, style: str = "seaborn-v0_8-whitegrid"):
        self.style = style
        self.logger = logging.getLogger(self.__class__.__name__)

    def build_panel(self, df_clean: pd.DataFrame, output_path: str = "reports/figures/painel_4_fenomenos_gentrificacao.png") -> None:
        """Gera o painel 2x2 com gráficos de Remembramento, Studios, ERM vs ERP e Adensamento."""
        self.logger.info("Construindo o painel gráfico 2x2...")
        
        plt.style.use(self.style)
        fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=300)

        # ----------------------------------------------------
        # GRÁFICO A: Remembramento (Tamanho Médio de Terreno por Legislação)
        # ----------------------------------------------------
        sns.barplot(
            data=df_clean, x='legislacao', y='area_do_terreno',
            ax=axes[0, 0], palette='Blues_d', errorbar=None
        )
        axes[0, 0].set_title('A. Remembramento: Tamanho Médio do Terreno (m²) por Legislação', fontsize=11, fontweight='bold', pad=10)
        axes[0, 0].set_xlabel('')
        axes[0, 0].set_ylabel('Área Média do Terreno (m²)')
        axes[0, 0].tick_params(axis='x', rotation=15)

        # ----------------------------------------------------
        # GRÁFICO B: "Febre dos Studios" (% de Unidades por Faixa de Tamanho)
        # ----------------------------------------------------
        studios_pct = RealEstateAnalytics.calculate_studio_evolution(df_clean)
        studios_pct.plot(kind='bar', stacked=True, ax=axes[0, 1], colormap='viridis', width=0.75)
        axes[0, 1].set_title('B. "Febre dos Studios": Evolução da Metragem das Unidades (% do Total)', fontsize=11, fontweight='bold', pad=10)
        axes[0, 1].set_xlabel('Ano de Emissão do Alvará')
        axes[0, 1].set_ylabel('% das Unidades Lançadas')
        axes[0, 1].legend(title='Tamanho Aptos', bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
        axes[0, 1].tick_params(axis='x', rotation=0)

        # ----------------------------------------------------
        # GRÁFICO C: ERM vs ERP (Evolução de Mercado vs Social)
        # ----------------------------------------------------
        erm_erp = RealEstateAnalytics.calculate_market_vs_social(df_clean)
        erm_erp.plot(kind='line', marker='o', ax=axes[1, 0], linewidth=2.2, markersize=5)
        axes[1, 0].set_title('C. Produção de Unidades: Mercado (ERM) vs. Social/Popular (ERP)', fontsize=11, fontweight='bold', pad=10)
        axes[1, 0].set_xlabel('Ano de Emissão do Alvará')
        axes[1, 0].set_ylabel('Total de Unidades Autorizadas')
        axes[1, 0].grid(True, linestyle='--', alpha=0.5)

        # ----------------------------------------------------
        # GRÁFICO D: Coeficiente de Aproveitamento Médio por Faixa
        # ----------------------------------------------------
        sns.boxplot(
            data=df_clean, x='faixa_tamanho', y='ca_total',
            ax=axes[1, 1], palette='Set2'
        )
        axes[1, 1].set_title('D. Adensamento: Coeficiente de Aproveitamento por Tamanho de Apto', fontsize=11, fontweight='bold', pad=10)
        axes[1, 1].set_xlabel('Faixa de Metragem')
        axes[1, 1].set_ylabel('Coeficiente de Aproveitamento (CA)')
        axes[1, 1].set_ylim(0, 8)

        plt.tight_layout()

        # Garante a existência do diretório de saída
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        self.logger.info(f"Painel salvo com sucesso em: {output_path}")