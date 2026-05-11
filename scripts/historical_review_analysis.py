import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# --- Configuração ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_PATH = os.path.join(BASE_DIR, 'data', 'app_reviews_data', 'myfitnesspal_2014_2015.csv')
VISUALS_DIR = os.path.join(BASE_DIR, 'visuals', '2015')
os.makedirs(VISUALS_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'visuals', 'conclusoes'), exist_ok=True)

# Usaremos os mesmos temas do script de reclamações para manter a consistência
from review_complaints_analysis import THEMES, clean_text
from gamification_nlp_analysis import GAMIFICATION_BROAD, GAMIFICATION_CONSERVATIVE, contains_keywords

def main():
    print("--- Análise Histórica de Reviews (Período: 2014-2015) ---")
    
    try:
        df = pd.read_csv(REVIEW_PATH)
        print(f"Dataset histórico carregado com sucesso de: {REVIEW_PATH}")
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado em '{REVIEW_PATH}'")
        return

    # --- Filtragem por Ano ---
    # Garante que a coluna de data e texto estejam no formato do scraper atual
    if 'date' not in df.columns or 'text' not in df.columns:
        print("ERRO: O CSV histórico precisa das colunas 'date' e 'text'.")
        return
        
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date'], inplace=True) # Remove linhas onde a data não pôde ser convertida
        
    print(f"Analisando {len(df)} reviews encontradas do período de 2014 a 2015.")

    # --- Análise de Temas (similar ao outro script) ---
    df['content_clean'] = df['text'].apply(clean_text)
    
    # Foco nas reviews negativas deste período
    df_negative = df[df['score'] <= 2].copy()
    df_positive = df[df['score'] >= 4].copy()
    
    if df_negative.empty:
        print("Nenhuma review negativa (1-2 estrelas) encontrada neste dataset.")
        return

    # Contagem de temas
    theme_counts = {theme: 0 for theme in THEMES.keys()}
    for text in df_negative['content_clean']:
        for theme, words in THEMES.items():
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    theme_counts[theme] += 1
                    break # Conta o tema apenas uma vez por review

    word_freq_neg = {}
    for group, words in THEMES.items():
        for word in words:
            pattern = r'\b' + re.escape(word) + r'\b'
            count = df_negative['content_clean'].str.contains(pattern, regex=True).sum()
            if count > 0:
                word_freq_neg[word] = count
    word_freq_neg = dict(sorted(word_freq_neg.items(), key=lambda item: item[1], reverse=True))

    # --- Geração de Relatório e Gráfico ---
    report_path = os.path.join(VISUALS_DIR, 'relatorio_churn_2014_2015.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== ANÁLISE DE RECLAMAÇÕES (DADOS DE 2014 A 2015) ===\n")
        f.write(f"Total de reviews negativas analisadas: {len(df_negative)}\n\n")
        f.write("--- O QUE OS USUÁRIOS MAIS RECLAMAVAM? ---\n")
        sorted_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)
        for theme, count in sorted_themes:
            pct = (count / len(df_negative)) * 100
            f.write(f"- {theme.upper()}: {count} menções ({pct:.1f}%)\n")
            
        f.write("\n--- FREQUÊNCIA DE PALAVRAS ---\n")
        f.write("(Número de reviews em que a palavra foi mencionada)\n")
        for w, c in word_freq_neg.items():
            f.write(f"- {w}: {c}\n")

    print(f"Relatório de 2014-2015 salvo em: {report_path}")

    # Gráfico
    plt.figure(figsize=(10, 6))
    themes_names = [t[0].replace('_', ' ').title() for t in sorted_themes]
    themes_vals = [t[1] for t in sorted_themes]
    
    sns.barplot(x=themes_vals, y=themes_names, palette="coolwarm")
    plt.title('Principais Motivos de Reclamação no MFP (2014 - 2015)\nA Era de Ouro (App 100% Gratuito)', fontsize=14, pad=15)
    plt.xlabel('Número de Menções', fontsize=12)
    plt.ylabel('Tema da Reclamação', fontsize=12)
    
    plt.tight_layout()
    chart_path = os.path.join(VISUALS_DIR, 'grafico_churn_2014_2015.png')
    plt.savefig(chart_path)
    print(f"Gráfico da Era de Ouro salvo em: {chart_path}")
    plt.close()
    
    # ---------------------------------------------------------
    # GERANDO GRÁFICOS DE PALAVRAS POR TEMA (2014 - 2015)
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
        plt.title(f'Palavras mais frequentes no tema:\n{theme_title} (2014-2015)', fontsize=14, pad=15)
        plt.xlabel('Número de Menções', fontsize=12)
        plt.ylabel('Palavra-chave', fontsize=12)
        
        plt.tight_layout()
        sub_chart_path = os.path.join(VISUALS_DIR, f'grafico_palavras_{theme}_2015.png')
        plt.savefig(sub_chart_path)
        plt.close() # Fecha a figura atual para liberar memória
        
    print("Gráficos de palavras por tema salvos com sucesso na pasta visuals/2015/")

    # ---------------------------------------------------------
    # ANÁLISE DE GAMIFICAÇÃO (POSITIVAS 2014 - 2015)
    # ---------------------------------------------------------
    if df_positive.empty:
        return
        
    print("\n--- Analisando Gamificação (2014-2015) ---")
    df_positive['has_gamification_conservative'] = df_positive['content_clean'].apply(lambda x: contains_keywords(x, GAMIFICATION_CONSERVATIVE))
    df_positive['has_gamification_broad'] = df_positive['content_clean'].apply(lambda x: contains_keywords(x, GAMIFICATION_BROAD))
    total_pos = len(df_positive)
    cons_count = df_positive['has_gamification_conservative'].sum()
    broad_count = df_positive['has_gamification_broad'].sum()

    word_freq_pos = {}
    for group, words in GAMIFICATION_BROAD.items():
        for word in words:
            pattern = r'\b' + re.escape(word) + r'\b'
            count = df_positive['content_clean'].str.contains(pattern, regex=True).sum()
            if count > 0:
                word_freq_pos[word] = count
    word_freq_pos = dict(sorted(word_freq_pos.items(), key=lambda item: item[1], reverse=True))

    report_txt_pos = os.path.join(VISUALS_DIR, 'relatorio_gamificacao_2015.txt')
    with open(report_txt_pos, 'w', encoding='utf-8') as f:
        f.write("=== RELATÓRIO DE GAMIFICAÇÃO - REVIEWS POSITIVAS (2014-2015) ===\n")
        f.write(f"Total de reviews positivas analisadas (4 ou 5 estrelas): {total_pos}\n\n")
        f.write("--- RESULTADOS GERAIS ---\n")
        f.write(f"Menções na Lista Conservadora: {cons_count} ({(cons_count/total_pos)*100:.2f}%)\n")
        f.write(f"Menções na Lista Ampla: {broad_count} ({(broad_count/total_pos)*100:.2f}%)\n\n")
        f.write("--- FREQUÊNCIA DE PALAVRAS ---\n")
        f.write("(Número de reviews em que a palavra foi mencionada)\n")
        for w, c in word_freq_pos.items():
            f.write(f"- {w}: {c}\n")
    print(f"Relatório de Gamificação 2014-2015 salvo em: {report_txt_pos}")

    # Gráfico Geral Gamificação
    plt.figure(figsize=(8, 6))
    ax = sns.barplot(x=['Conservadora', 'Ampla'], y=[(cons_count/total_pos)*100, (broad_count/total_pos)*100], palette="viridis")
    plt.title('Percentual de Reviews Mencionando Gamificação (2014-2015)', fontsize=14, pad=15)
    plt.ylabel('Percentual das Reviews (%)', fontsize=12)
    plt.xlabel('Abordagem da Lista de Palavras', fontsize=12)
    plt.ylim(0, max((broad_count/total_pos)*100 + 10, 10))
    
    counts = [cons_count, broad_count]
    percentages = [(cons_count/total_pos)*100, (broad_count/total_pos)*100]
    for i, p in enumerate(ax.patches):
        ax.annotate(f'{counts[i]} reviews\n({percentages[i]:.1f}%)', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 15), textcoords='offset points')

    plt.savefig(os.path.join(VISUALS_DIR, 'comparacao_gamificacao_reviews_2015.png'), bbox_inches='tight')
    plt.close()

    # Gráficos de Palavras por Tema (Gamificação)
    print("\nGerando gráficos de palavras para cada categoria da Gamificação...")
    word_counts_pos = {theme: {word: 0 for word in words} for theme, words in GAMIFICATION_BROAD.items()}
    for text in df_positive['content_clean']:
        if not text: continue
        for theme, words in GAMIFICATION_BROAD.items():
            for word in words:
                if re.search(r'\b' + re.escape(word) + r'\b', text):
                    word_counts_pos[theme][word] += 1
                    
    for theme, words_dict in word_counts_pos.items():
        active_words = {k: v for k, v in words_dict.items() if v > 0}
        if not active_words: continue
            
        sorted_words = sorted(active_words.items(), key=lambda x: x[1], reverse=True)
        plt.figure(figsize=(8, 5))
        sns.barplot(x=[w[1] for w in sorted_words], y=[w[0] for w in sorted_words], palette="viridis")
        plt.title(f'Palavras mais frequentes:\n{theme.replace("_", " ").title()} (Positivas 2014-2015)', fontsize=14, pad=15)
        plt.xlabel('Número de Menções', fontsize=12)
        plt.ylabel('Palavra-chave', fontsize=12)
        plt.tight_layout()
        plt.savefig(os.path.join(VISUALS_DIR, f'grafico_palavras_gamificacao_{theme}_2015.png'))
        plt.close()
        
if __name__ == "__main__":
    main()