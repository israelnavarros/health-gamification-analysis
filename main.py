import subprocess
import os
import sys

# Caminhos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# Lista de scripts geradores de gráficos/relatórios na ordem cronológica de análise
SCRIPTS_TO_RUN = [
    "retention_analysis.py",
    "historical_behavioral_churn.py",
    "historical_review_analysis.py",
    "gamification_nlp_analysis.py",
    "review_complaints_analysis.py",
    "veteran_users_analysis.py"
]

def main():
    print("="*60)
    print("🚀 INICIANDO GERAÇÃO DE RELATÓRIOS E GRÁFICOS")
    print("="*60)
    
    for script in SCRIPTS_TO_RUN:
        script_path = os.path.join(SCRIPTS_DIR, script)
        if not os.path.exists(script_path):
            print(f"\n❌ Script não encontrado: {script}")
            continue
            
        print(f"\n▶️ Executando: {script} ...")
        try:
            subprocess.run([sys.executable, script_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ O script {script} falhou com o erro: {e}")
            
    print("\n" + "="*60)
    print("✅ PIPELINE FINALIZADA! TODOS OS RELATÓRIOS FORAM ATUALIZADOS.")
    print(f"📁 Verifique as subpastas em '{os.path.join(BASE_DIR, 'visuals')}' para ver os resultados.")
    print("="*60)

if __name__ == "__main__":
    main()