import pandas as pd
from google_play_scraper import Sort, reviews
import os

def scrape_mfp_reviews():
    print("Coletando reviews do MyFitnessPal na Google Play Store...")
    print("Isso pode levar alguns instantes (estamos baixando 10000 reviews)...")
    
    # Coletar as reviews usando a biblioteca google-play-scraper
    result, continuation_token = reviews(
        'com.myfitnesspal.android',
        lang='en', # Pegando em inglês para maximizar o encontro das palavras da sua lista
        country='us',
        sort=Sort.NEWEST, # Pega as avaliações mais recentes
        count=10000 # Quantidade de reviews a serem extraídas
    )
    
    if not result:
        print("Nenhuma review encontrada.")
        return

    # Converter o resultado (lista de dicionários) para um DataFrame do Pandas
    df = pd.DataFrame(result)
    
    # Criar a coluna appId para manter a compatibilidade com o seu código de NLP
    df['appId'] = 'com.myfitnesspal.android'
    
    # Salvar na pasta correta
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_file = os.path.join(base_dir, 'data', 'app_reviews_data', 'mfp_reviews.csv')
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Sucesso! {len(df)} reviews coletadas e salvas em:\n{output_file}")

if __name__ == "__main__":
    scrape_mfp_reviews()