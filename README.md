# Pipeline Dados Imobiliários de São Paulo

Pipeline desenvolvido em Python para limpeza e análise quantitativa da base de **Alvarás de Construção** da cidade de São Paulo.

O projeto resolve o problema de dados públicos bagunçados, aplicando um algoritmo de resolução em cascata (4 níveis) para mapear os distritos e extrair informações sobre adensamento, tamanho de unidades e vetores de desenvolvimento imobiliário no Centro Expandido.

## Algoritmo de Para Determinar o Distrito em 4 Níveis
Os dados sobre bairros na planilha do Insper possuem divergencia de grafia ou informações imprecisas. Para fazer a localização correta dos alvarás, esse pipeline implementa um algorítimo de indentificação em 4 níveis:
1. Nível 1 (Match Direto): Normalização de texto e procura correspondência com a lista de distritos oficiais de SP;
2. Nível 2 (Dedução por Quadra): Se não resolveu no Nível 1, consulta o código do IPTU (SQL/INCRA - apenas os 6 primeiros dígitos correspondentes a Quadra) e atribui o distrito de outros imóveis já identificados do mesmo quarteirão.
3. Nível 3 (Dedução por Rua): Se não resolveu no Nível 2, consulta o logradouro e atribui o distrito de outros imóveis já identificados da mesma rua.
4. Nível 4 (Dedução por Setor): Varifica os 3 primeiros dígitos do SQL (Setor Urbano) para deduzir o distrito que corresponde a moda.

## Dashboard
O módulo ```analytics``` gera um painel de visualização com 4 gráficos:
1. Remembramento: Mostra o tamanho médio do terreno por legistação.
2. Frebre dos Estúdios: Mostra o percentual de imóveis por faixa de área ao longo dos anos.
3. ERM vs. ERP: Mostra a quantidade de unidades comerciais (ERM) e unidades populares (ERP) ao longo dos anos.
4. Adensamento Urbano: Visualiza o Coeficiente de Aproveitamento (CA) por faixa de tamanho.

## Arquitetura do Projeto

O código foi estruturado seguindo as estratégias de clareza, orientação a objetos (OOP) e modularidade:

```text
mercado_imobiliario_sp/
├── data/
│   ├── bruto/                      # Dados brutos (alvaras_por_lote.xlsx)
│   └── tratado/                    # Dados limpos e mapeados (alvaras_mapeados.xlsx)
├── reports/
│   ├── figures/                    # gráficos gerados (.png)
│   └── Report.pdf                  # Relatório
├── src/
│   ├── __init__.py
│   ├── config.py                   # Mapeamentos geográficos, constantes e listas
│   ├── utils.py                    # Normalização de texto e expressões
│   ├── pipeline.py                 # Resolução espacial em 4 Níveis
│   ├── analytics.py                # Engenharia de atributos, faixas e agregações
│   └── visualizacao.py             # Módulo de plotagem
├── main.py                         # Ponto de entrada
├── requirements.txt                # Dependências do projeto
└── README.md                       # Documentação do repositório
```

## Como Executar o Projeto
**Pré-requisitos:**
- Python 3.10 ou superior instalado.
1. clone o respositório
```bash
git clone [https://github.com/seu-usuario/mercado_imobiliario_sp.git](https://github.com/seu-usuario/sp-realestate-quant.git)
cd mercado_imobiliario_sp
```

2. Criar e ativar um ambiente virtual
```bash
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```
3. Instalar as dependências
```bash
pip install -r requirements.txt
```

4. Executar o pipeline
```bash
python main.py
```

Autor: Daniel Pereira Lima
Linkedin: [Daniel Pereira Lima](https://www.linkedin.com/in/daniel-pereira-lima-b92a52324/)
E-mail: daniellima.1415965@gmail.com
