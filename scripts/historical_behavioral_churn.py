import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuração de caminhos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'myfitnesspal_data', 'data.tsv')
VISUALS_DIR = os.path.join(BASE_DIR, 'visuals', '2015')
os.makedirs(VISUALS_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'visuals', 'conclusoes'), exist_ok=True)

def main():
    print("Carregando logs de uso históricos de 2014 (data.tsv)...")
    try:
        df = pd.read_csv(DATA_PATH, sep='\t')
    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {DATA_PATH}")
        return

    if 'date' not in df.columns or 'user_id' not in df.columns:
        print("Erro: O arquivo TSV precisa ter as colunas 'user_id' e 'date'.")
        return

    # Conversão de data segura
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.dropna(subset=['date', 'user_id'], inplace=True)

    # 1. Encontrar o Primeiro e o Último dia de log de cada usuário
    user_stats = df.groupby('user_id').agg(
        first_day=('date', 'min'),
        last_day=('date', 'max')
    ).reset_index()

    # Calcula o "Tempo de Vida" (Lifetime) do usuário no aplicativo
    user_stats['lifetime_days'] = (user_stats['last_day'] - user_stats['first_day']).dt.days

    # 2. Separar os usuários em Cohorts de Retenção
    user_stats['status'] = user_stats['lifetime_days'].apply(
        lambda x: 'Desistentes (Saíram em <= 30 dias)' if x <= 30 else 'Retidos (> 30 dias)'
    )

    # 3. Analisar a Consistência / Streak (Nos primeiros 15 dias)
    # Focamos nos primeiros 15 dias para comparar os dois grupos de forma justa
    df_merged = pd.merge(df, user_stats[['user_id', 'first_day']], on='user_id')
    df_merged['day_of_life'] = (df_merged['date'] - df_merged['first_day']).dt.days

    # Filtra apenas os logs que ocorreram nos dias 0 a 15 de cada usuário
    df_first_15 = df_merged[df_merged['day_of_life'] <= 15]

    # Conta em quantos dias ÚNICOS o usuário acessou (Isso simula a mecânica de "Streak" diário)
    consistency = df_first_15.groupby('user_id')['day_of_life'].nunique().reset_index()
    consistency.columns = ['user_id', 'active_days_first_15']

    analysis_df = pd.merge(user_stats[['user_id', 'status']], consistency, on='user_id', how='left')
    analysis_df['active_days_first_15'].fillna(1, inplace=True) # Todo mundo tem pelo menos o Dia 0

    # 4. Resumo e Estatísticas
    summary = analysis_df.groupby('status')['active_days_first_15'].mean().reset_index()
    
    # 5. Gerar o Gráfico
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(9, 6))

    ax = sns.barplot(x='status', y='active_days_first_15', data=summary, palette="Set2")
    plt.title('Por que saíram em 2014? A quebra de Consistência\nEngajamento médio nos primeiros 15 dias de uso', fontsize=14, pad=15)
    plt.xlabel('Status do Usuário (Baseado na Retenção)', fontsize=12)
    plt.ylabel('Média de Dias Ativos (Streak inicial de 0 a 15)', fontsize=12)

    # Adicionar os valores nas barras
    for i, p in enumerate(ax.patches):
        ax.annotate(f"{p.get_height():.1f} dias", 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', xytext=(0, 10), textcoords='offset points', fontweight='bold')

    plt.tight_layout()
    chart_path = os.path.join(VISUALS_DIR, 'comportamento_churn_2014.png')
    plt.savefig(chart_path)
    print(f"\nSucesso! Gráfico comportamental salvo em: {chart_path}")

if __name__ == "__main__":
    main()