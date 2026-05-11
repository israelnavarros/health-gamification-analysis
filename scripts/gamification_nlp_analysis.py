import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re

# 1. CONFIGURAÇÃO DE CAMINHOS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW_PATH = os.path.join(BASE_DIR, 'data', 'app_reviews_data', 'mfp_reviews.csv')
VISUALS_DIR = os.path.join(BASE_DIR, 'visuals')

# Garante que a pasta visuals exista
os.makedirs(VISUALS_DIR, exist_ok=True)

# 2. LISTAS DE PALAVRAS (INGLÊS, PORTUGUÊS)
GAMIFICATION_CONSERVATIVE = {
    "goals_targets": [
        "goal", "goals", "target", "targets", "daily goal", "milestone",
        "meta", "metas", "objetivo", "objetivos", "marco"
    ],
    "streak_consistency": [
        "streak", "streaks", "days in a row", "consecutive", "consistency", "motivation",
        "ofensiva", "ofensivas", "racha", "rachas", "consistência", "motivação", "dias seguidos"
    ],
    "rewards_achievements": [
        "badge", "badges", "achievement", "achievements", "reward", "rewards", "medal", "medals",
        "conquista", "conquistas", "recompensa", "recompensas", "medalha", "medalhas", "logro", "logros", "insignia"
    ],
    "social_community": [
        "community", "friends", "support", "challenge", "leaderboard", "compete",
        "comunidade", "amigos", "apoio", "desafio", "competir", "placar"
    ]
}

GAMIFICATION_BROAD = {
    **GAMIFICATION_CONSERVATIVE,  # Inclui tudo da conservadora e adiciona mais
    "progress_tracking": [
        "progress", "tracking", "track", "routine", "daily", "habit", "habits", "graph", "chart",
        "progresso", "rotina", "diário", "hábito", "hábitos", "progreso", "rutina", "gráfico"
    ],
    "health_utility": [
        "weight loss", "weight", "calories", "macros", "diet", "nutrition", "steps", "workout",
        "perda de peso", "peso", "calorias", "dieta", "nutrição", "passos", "treino"
    ]
}

# 3. FUNÇÕES DE TRATAMENTO E BUSCA
def clean_text(text):
    """Converte para minúsculas e remove pontuação básica para facilitar o match."""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove pontuações comuns mantendo letras e números
    text = re.sub(r'[^\w\s]', ' ', text)
    return text

def contains_keywords(text, keyword_dict):
    """Verifica se o texto contém alguma das palavras do dicionário (usando word boundaries \b)."""
    if not text:
        return False
    
    for group, words in keyword_dict.items():
        for word in words:
            # \b garante que pegamos a palavra exata (ex: 'walk' não vai dar match em 'sidewalk')
            if re.search(r'\b' + re.escape(word) + r'\b', text):
                return True
    return False

# 4. CARREGAMENTO E ANÁLISE DOS DADS
def main():
    print("Carregando o dataset de reviews...")
    try:
        df = pd.read_csv(REVIEW_PATH)
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {REVIEW_PATH}")
        return

    # Filtrando apenas para o MyFitnessPal
    df = df[df['appId'] == 'com.myfitnesspal.android'].copy()
    
    # NOVO: Filtrando apenas as reviews POSITIVAS (4 e 5 estrelas)
    df = df[df['score'] >= 4].copy()
    
    if df.empty:
        print("Aviso: Nenhuma review do MyFitnessPal (com.myfitnesspal.android) foi encontrada no CSV atual.")
        print("Adicione as reviews do app ou remova o filtro temporariamente para testar.")
        return

    print(f"Total de reviews POSITIVAS (4-5 estrelas) do MyFitnessPal: {len(df)}")

    # Aplica a limpeza de dados
    df['content_clean'] = df['content'].apply(clean_text)

    # Aplica a classificação
    print("Classificando reviews...")
    df['has_gamification_conservative'] = df['content_clean'].apply(lambda x: contains_keywords(x, GAMIFICATION_CONSERVATIVE))
    df['has_gamification_broad'] = df['content_clean'].apply(lambda x: contains_keywords(x, GAMIFICATION_BROAD))

    # Calcula resultados
    total_reviews = len(df)
    cons_count = df['has_gamification_conservative'].sum()
    broad_count = df['has_gamification_broad'].sum()

    print("\n--- RESULTADOS ---")
    print(f"Lista Conservadora: {cons_count} menções ({(cons_count/total_reviews)*100:.2f}%)")
    print(f"Lista Ampla: {broad_count} menções ({(broad_count/total_reviews)*100:.2f}%)")

    # Gerando relatório de texto com frequência de palavras
    word_freq = {}
    for group, words in GAMIFICATION_BROAD.items():
        for word in words:
            pattern = r'\b' + re.escape(word) + r'\b'
            # Contando em quantas reviews a palavra exata aparece
            count = df['content_clean'].str.contains(pattern, regex=True).sum()
            if count > 0:
                word_freq[word] = count
                
    # Ordenando da palavra mais frequente para a menos frequente
    word_freq = dict(sorted(word_freq.items(), key=lambda item: item[1], reverse=True))

    report_txt_path = os.path.join(VISUALS_DIR, 'relatorio_gamificacao_reviews.txt')
    with open(report_txt_path, 'w', encoding='utf-8') as f:
        f.write("=== RELATÓRIO DE GAMIFICAÇÃO - REVIEWS POSITIVAS (MYFITNESSPAL) ===\n")
        f.write(f"Total de reviews positivas analisadas (4 ou 5 estrelas): {total_reviews}\n\n")
        f.write("--- RESULTADOS GERAIS ---\n")
        f.write(f"Menções na Lista Conservadora: {cons_count} ({(cons_count/total_reviews)*100:.2f}%)\n")
        f.write(f"Menções na Lista Ampla: {broad_count} ({(broad_count/total_reviews)*100:.2f}%)\n\n")
        f.write("--- FREQUÊNCIA DE PALAVRAS ---\n")
        f.write("(Número de reviews em que a palavra foi mencionada)\n")
        for w, c in word_freq.items():
            f.write(f"- {w}: {c}\n")
            
    print(f"Relatório TXT salvo com sucesso em: {report_txt_path}")

    # 5. GERANDO O GRÁFICO
    sns.set_theme(style="whitegrid")
    
    # Dados para o gráfico
    categories = ['Conservadora', 'Ampla']
    counts = [cons_count, broad_count]
    percentages = [(cons_count/total_reviews)*100, (broad_count/total_reviews)*100]

    plt.figure(figsize=(8, 6))
    ax = sns.barplot(x=categories, y=percentages, palette="viridis")
    
    plt.title('Percentual de Reviews Mencionando Gamificação', fontsize=14, pad=15)
    plt.ylabel('Percentual das Reviews (%)', fontsize=12)
    plt.xlabel('Abordagem da Lista de Palavras', fontsize=12)
    plt.ylim(0, max(percentages) + 10) # Dá um espaço extra no topo

    # Adicionando os rótulos de dados no topo de cada barra
    for i, p in enumerate(ax.patches):
        ax.annotate(f'{counts[i]} reviews\n({percentages[i]:.1f}%)', 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 15), 
                    textcoords='offset points')

    # Salva na pasta visuals
    chart_path = os.path.join(VISUALS_DIR, 'comparacao_gamificacao_reviews.png')
    plt.savefig(chart_path, bbox_inches='tight')
    print(f"\nGráfico salvo com sucesso em: {chart_path}")

if __name__ == "__main__":
    main()
