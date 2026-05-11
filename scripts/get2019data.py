from google_play_scraper import reviews, Sort
import pandas as pd
import time
from datetime import datetime
import os
import random

app_id = 'com.myfitnesspal.android'
all_reviews = []
token = None
count_per_request = 1000 # Máximo permitido para ir mais rápido

# Intervalo desejado
start_year = 2015
end_year = 2014
MAX_REVIEWS = 10000

# Configuração do diretório de saída
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'app_reviews_data')
os.makedirs(DATA_DIR, exist_ok=True)

next_backup = 5000

print(f"--- Iniciando busca por avaliações de {end_year} a {start_year} ---")
print("Aguarde, o scraper precisa passar pelas avaliações recentes primeiro...\n")

skipped_count = 0
reached_past = False

try:
    while not reached_past:
        # Busca o lote de reviews
        result, token = reviews(
            app_id,
            lang='en',      # 'en' para mais dados, 'pt' para ser mais rápido
            country='us',   # 'us' para mais dados, 'br' para ser mais rápido
            sort=Sort.NEWEST,
            count=count_per_request,
            continuation_token=token
        )

        if not result:
            print("Não há mais avaliações disponíveis.")
            break

        # Verifica a data da primeira e da última review do lote para o log
        current_batch_year = result[0]['at'].year
        last_batch_year = result[-1]['at'].year
        
        for r in result:
            review_year = r['at'].year
            
            if end_year <= review_year <= start_year:
                # Salva apenas o essencial para o arquivo não ficar gigante
                all_reviews.append({
                    'date': r['at'],
                    'score': r['score'],
                    'text': r['content'],
                    'thumbsUp': r['thumbsUpCount']
                })
                
                if len(all_reviews) >= MAX_REVIEWS:
                    print(f"\nLimite máximo de {MAX_REVIEWS} avaliações atingido. Parando a coleta!")
                    reached_past = True
                    break
            elif review_year > start_year:
                skipped_count += 1
            elif review_year < end_year:
                reached_past = True
                break

        print(f"[LOG] Processando ano: {current_batch_year} | " 
              f"Pulei {skipped_count} recentes | "
              f"Coletei {len(all_reviews)} do intervalo desejado")

        # Se já coletamos muito, salvamos um backup para não perder o progresso
        if len(all_reviews) >= next_backup:
            backup_path = os.path.join(DATA_DIR, 'backup_mfp_reviews.csv')
            pd.DataFrame(all_reviews).to_csv(backup_path, index=False)
            print(f"💾 Backup salvo na pasta data! ({len(all_reviews)} itens)")
            next_backup += 5000

        # Pausa obrigatória para não ser bloqueado pelo Google (Error 429)
        time.sleep(random.uniform(1.5, 3.5)) # Sleep aleatório entre 1.5 e 3.5 segundos

except Exception as e:
    print(f"\nOcorreu um erro ou interrupção: {e}")

# Finalização
if all_reviews:
    df = pd.DataFrame(all_reviews)
    filename = os.path.join(DATA_DIR, f'myfitnesspal_{end_year}_{start_year}.csv')
    df.to_csv(filename, index=False)
    print(f"\n--- SUCESSO! ---")
    print(f"Total de avaliações salvas: {len(df)}")
    print(f"Arquivo gerado: {filename}")
else:
    print("\nNenhuma avaliação encontrada no período especificado.")
