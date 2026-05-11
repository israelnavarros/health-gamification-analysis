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


# PPalavras-chave

THEMES = {
    # Motivos de Churn / Reclamações (Por que estão saindo?)
    "paywall_e_monetizacao": [
        "pay", "paid", "premium", "subscription", "money", "expensive", "paywall", "charge", "scam", "ads", "ad", "popup", "popups", "greedy"
    ],
    "funcionalidades_removidas_ou_pagas": [
        "barcode", "scanner", "scan", "bring back", "used to be", "removed", "missing", "bring it back"
    ],
    "piora_na_interface_ux": [
        "ui", "ux", "update", "interface", "layout", "clicks", "clunky", "hard to use", "unusable", "confusing", "design", "slow", "lag", "laggy"
    ],
    "bugs_e_perda_de_dados": [
        "bug", "glitch", "crash", "sync", "lost", "deleted", "duplicate", "freeze", "frozen", "log out", "force close"
    ],
    
    # Mecânicas de Gamificação e Engajamento do MFP
    "streaks_e_consistencia": [
        "streak", "streaks", "days in a row", "consecutive", "habit"
    ],
    "metas_e_progresso": [
        "goal", "goals", "progress", "projection", "maintain", "target", "weight loss"
    ]
}

def clean_text(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def count_themes(text):
    found_themes = []
    for theme, words in THEMES.items():
        for word in words:
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                found_themes.append(theme)
                break # Se achou uma palavra do tema, já marca o tema e vai pro próximo
    return found_themes

def main():
    print("Carregando dataset de reviews do MyFitnessPal...")
    df = pd.read_csv(REVIEW_PATH)
    
    # Limpeza
    df['content_clean'] = df['content'].apply(clean_text)
    
    # Identificando temas em todas as reviews
    df['themes'] = df['content_clean'].apply(count_themes)
    
    # Vamos focar a análise de "reclamações" apenas nas reviews negativas (Score 1 e 2)
    df_negative = df[df['score'] <= 2].copy()
    
    # Contagem para o Relatório
    theme_counts = {theme: 0 for theme in THEMES.keys()}
    for themes in df_negative['themes']:
        for t in themes:
            theme_counts[t] += 1
            
    total_negatives = len(df_negative)
    
    # ---------------------------------------------------------
    # GERANDO O RELATÓRIO TXT
    # ---------------------------------------------------------
    report_path = os.path.join(VISUALS_DIR, 'relatorio_motivos_churn.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== ANÁLISE DE CHURN E RECLAMAÇÕES (MYFITNESSPAL) ===\n")
        f.write(f"Total de reviews analisadas: {len(df)}\n")
        f.write(f"Total de reviews negativas (1 ou 2 estrelas): {total_negatives}\n\n")
        
        f.write("--- O QUE OS USUÁRIOS MAIS RECLAMAM? ---\n")
        # Ordena do maior para o menor
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        for theme, count in sorted_themes:
            pct = (count / total_negatives) * 100 if total_negatives > 0 else 0
            f.write(f"- {theme.upper()}: {count} menções ({pct:.1f}% das avaliações negativas)\n")
            
        f.write("\n--- FREQUÊNCIA DE PALAVRAS ---\n")
        f.write("(Número de reviews em que a palavra foi mencionada)\n")
        word_freq = {}
        for group, words in THEMES.items():
            for word in words:
                pattern = r'\b' + re.escape(word) + r'\b'
                count = df_negative['content_clean'].str.contains(pattern, regex=True).sum()
                if count > 0:
                    word_freq[word] = count
        word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1], reverse=True))
        for w, c in word_freq.items():
            f.write(f"- {w}: {c}\n")

        f.write("\nInsight: Palavras-chave como 'bring back' e 'barcode' indicam frustração com a monetização de mecânicas que antes eram gratuitas.\n")

    print(f"\nRelatório TXT salvo com sucesso em: {report_path}")

    # ---------------------------------------------------------
    # GERANDO O GRÁFICO
    # ---------------------------------------------------------
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    
    themes_names = [t[0].replace('_', ' ').title() for t in sorted_themes]
    themes_vals = [t[1] for t in sorted_themes]
    
    ax = sns.barplot(x=themes_vals, y=themes_names, palette="magma")
    plt.title('Principais Motivos de Reclamação/Churn no MFP\n(Reviews de 1 e 2 Estrelas)', fontsize=14, pad=15)
    plt.xlabel('Número de Menções', fontsize=12)
    plt.ylabel('Tema da Reclamação', fontsize=12)
    
    plt.tight_layout()
    chart_path = os.path.join(VISUALS_DIR, 'grafico_motivos_churn.png')
    plt.savefig(chart_path)
    print(f"Gráfico principal salvo com sucesso em: {chart_path}")
    plt.close() # Fecha a figura principal para não sobrepor os próximos gráficos

    # ---------------------------------------------------------
    # GERANDO GRÁFICOS DE PALAVRAS POR TEMA
    # ---------------------------------------------------------
    print("\nGerando gráficos de palavras para cada tema...")
    word_counts = {theme: {word: 0 for word in words} for theme, words in THEMES.items()}
    
    for text in df_negative['content_clean']:
        if not text: continue
        for theme, words in THEMES.items():
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    word_counts[theme][word] += 1
                    
    for theme, words_dict in word_counts.items():
        # Filtra palavras com pelo menos 1 menção para não poluir o gráfico
        active_words = {k: v for k, v in words_dict.items() if v > 0}
        if not active_words:
            continue
            
        sorted_words = sorted(active_words.items(), key=lambda x: x[1], reverse=True)
        word_names = [w[0] for w in sorted_words]
        word_vals = [w[1] for w in sorted_words]
        
        plt.figure(figsize=(8, 5))
        sns.barplot(x=word_vals, y=word_names, palette="mako")
        
        theme_title = theme.replace('_', ' ').title()
        plt.title(f'Palavras mais frequentes no tema:\n{theme_title}', fontsize=14, pad=15)
        plt.xlabel('Número de Menções', fontsize=12)
        plt.ylabel('Palavra-chave', fontsize=12)
        
        plt.tight_layout()
        sub_chart_path = os.path.join(VISUALS_DIR, f'grafico_palavras_{theme}.png')
        plt.savefig(sub_chart_path)
        plt.close() # Fecha a figura atual para liberar memória
        
    print("Gráficos de palavras por tema salvos com sucesso na pasta visuals/")

if __name__ == "__main__":
    main()