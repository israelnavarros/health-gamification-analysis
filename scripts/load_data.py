import pandas as pd
import os

# Caminhos das pastas (ajuste se necessário conforme sua localização)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_PATH = os.path.join(BASE_DIR, 'data', 'app_reviews_data', 'reviews.csv')
MFP_DATA_PATH = os.path.join(BASE_DIR, 'data', 'myfitnesspal_data', 'data.tsv')
MFP_ITEMS_PATH = os.path.join(BASE_DIR, 'data', 'myfitnesspal_data', 'items.tsv')

def load_datasets():
    print("Carregando bases de dados...")
    
    # Verifica se os arquivos existem antes de carregar
    caminhos = [REVIEW_PATH, MFP_DATA_PATH, MFP_ITEMS_PATH]
    for caminho in caminhos:
        if not os.path.exists(caminho):
            raise FileNotFoundError(f"Arquivo não encontrado no seu Windows:\n -> {caminho}\n"
                                    "Verifique se o nome da pasta está correto e se o arquivo foi descompactado.")

    # Lendo o CSV de Reviews (separador padrão é vírgula)
    df_reviews = pd.read_csv(REVIEW_PATH)
    
    # Lendo os TSVs do MyFitnessPal (separador é TAB)
    df_mfp_usage = pd.read_csv(MFP_DATA_PATH, sep='\t')
    df_mfp_items = pd.read_csv(MFP_ITEMS_PATH, sep='\t')
    
    print(f"Reviews carregados: {len(df_reviews)} linhas")
    print(f"Logs de uso carregados: {len(df_mfp_usage)} linhas")
    print(f"Itens carregados: {len(df_mfp_items)} linhas")
    
    return df_reviews, df_mfp_usage, df_mfp_items

if __name__ == "__main__":
    reviews, usage, items = load_datasets()
    
    # Visualização rápida para conferir as colunas
    print("\nColunas do Uso (MyFitnessPal):")
    print(usage.columns.tolist())