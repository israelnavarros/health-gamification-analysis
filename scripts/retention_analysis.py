import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuração de estilo
sns.set_theme(style="whitegrid")

def gerar_curva_retencao(usage_df):
    # 1. Garantir que a data está no formato correto
    # O dataset costuma ter colunas como 'user_id' e 'date'
    usage_df['date'] = pd.to_datetime(usage_df['date'])
    
    # 2. Encontrar a primeira data de log de cada usuário (Cohort)
    first_log = usage_df.groupby('user_id')['date'].min().reset_index()
    first_log.columns = ['user_id', 'first_day']
    
    # 3. Mesclar de volta para calcular o "dia de vida" do usuário no app
    df = pd.merge(usage_df, first_log, on='user_id')
    df['seniority'] = (df['date'] - df['first_day']).dt.days
    
    # 4. Calcular a retenção por dia (até o dia 30, por exemplo)
    retention = df.groupby('seniority')['user_id'].nunique()
    retention_pct = (retention / retention.iloc[0]) * 100
    
    # 5. Gerar o Gráfico
    plt.figure(figsize=(10, 6))
    retention_pct.head(31).plot(kind='line', marker='o', color='#2ecc71', linewidth=2)
    
    plt.title('Curva de Retenção de Usuários - MyFitnessPal', fontsize=14)
    plt.xlabel('Dias após o primeiro registro', fontsize=12)
    plt.ylabel('% de Usuários Ativos', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Salvar o gráfico na sua pasta visuals
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    visuals_dir = os.path.join(base_dir, 'visuals', '2015')
    os.makedirs(visuals_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, 'visuals', 'conclusoes'), exist_ok=True)
    
    plt.savefig(os.path.join(visuals_dir, 'curva_retencao_mfp.png'))
    print("Gráfico de retenção salvo em visuals/2015/curva_retencao_mfp.png")
    
    # Gerar o relatório de texto
    report_path = os.path.join(visuals_dir, 'relatorio_retencao.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=== RELATÓRIO DE RETENÇÃO (MYFITNESSPAL) ===\n")
        f.write("Dia\tUsuários Ativos\tRetenção (%)\n")
        # Considerando os primeiros 30 dias de vida do usuário
        for day in range(31):
            if day in retention.index:
                users = retention.loc[day]
                pct = retention_pct.loc[day]
                f.write(f"Dia {day}\t{users}\t{pct:.2f}%\n")
                
    print(f"Relatório TXT salvo em {report_path}")
    plt.show()

if __name__ == "__main__":
    # Carregando o tsv (ajuste o caminho se necessário)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'myfitnesspal_data', 'data.tsv')
    df_usage = pd.read_csv(data_path, sep='\t')
    gerar_curva_retencao(df_usage)