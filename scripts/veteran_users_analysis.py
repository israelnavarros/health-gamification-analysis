import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_PATH = os.path.join(BASE_DIR, 'data', 'app_reviews_data', 'mfp_reviews.csv')
VISUALS_DIR = os.path.join(BASE_DIR, 'visuals', '2026')
os.makedirs(VISUALS_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'visuals', 'conclusoes'), exist_ok=True)

# Importa a limpeza e os temas do seu script já existente
from review_complaints_analysis import THEMES, clean_text

def is_veteran_user(text):
    """Verifica se o usuário indica usar o app há muitos anos."""
    if not text:
        return False
    
    # Padrões que indicam um usuário antigo (10+ anos, desde 201X, etc)
    veteran_patterns = [
        r"10 years", r"11 years", r"12 years", r"years ago", 
        r"since 201", r"since 200", r"many years", r"long time user",
        r"using it for years", r"used to love", r"used to be",
        r"anos", r"desde 201" # Para pegar alguns em português se houver
    ]
    
    for pattern in veteran_patterns:
        if re.search(pattern, text):
            return True
    return False

def main():
    print("Carregando dataset de reviews do MyFitnessPal...")
    df = pd.read_csv(REVIEW_PATH)
    
    # Limpeza do texto
    df['content_clean'] = df['content'].apply(clean_text)
    
    # Filtra apenas os usuários que identificamos como "Veteranos"
    df['is_veteran'] = df['content_clean'].apply(is_veteran_user)
    df_veterans = df[df['is_veteran'] == True].copy()
    
    print(f"Total de reviews gerais: {len(df)}")
    print(f"Total de usuários identificados como 'Veteranos': {len(df_veterans)}")
    
    if df_veterans.empty:
        print("Nenhum usuário veterano encontrado com os padrões atuais.")
        return

    # Vamos focar apenas nos veteranos insatisfeitos (Score 1 e 2)
    df_vet_negative = df_veterans[df_veterans['score'] <= 2].copy()
    
    # Contagem de temas (Por que os usuários de 2014 estão saindo hoje?)
    theme_counts = {theme: 0 for theme in THEMES.keys()}
    for text in df_vet_negative['content_clean']:
        for theme, words in THEMES.items():
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    theme_counts[theme] += 1
                    break # Marca o tema uma vez por review

    total_negatives = len(df_vet_negative)
    print(f"Usuários veteranos que deram nota baixa (1-2 estrelas): {total_negatives}")

    # --- GERANDO O GRÁFICO ---
    sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
    
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    themes_names = [t[0].replace('_', ' ').title() for t in sorted_themes]
    themes_vals = [t[1] for t in sorted_themes]
    
    ax = sns.barplot(x=themes_vals, y=themes_names, palette="flare")
    plt.title("Motivos de Churn dos Usuários 'Veteranos'\n(Usuários que estão no app há anos e agora dão nota baixa)", fontsize=14, pad=15)
    plt.xlabel('Número de Menções', fontsize=12)
    plt.ylabel('Tema da Reclamação', fontsize=12)
    
    plt.tight_layout()
    chart_path = os.path.join(VISUALS_DIR, 'grafico_churn_veteranos.png')
    plt.savefig(chart_path)
    print(f"\nGráfico da Velha Guarda salvo com sucesso em: {chart_path}")

if __name__ == "__main__":
    main()
