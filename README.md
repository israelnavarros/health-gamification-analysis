# Health Gamification Analysis 🎮🍎

Este repositório contém o trabalho desenvolvido para a disciplina de **Game Analytics**. O objetivo é analisar como mecânicas de jogos influenciam a consistência de hábitos saudáveis em usuários de aplicativos de Fitness.

## 📋 Sobre o Projeto
O projeto utiliza dados públicos do **MyFitnessPal** (logs de usuários e reviews da Play Store) para correlacionar o uso de mecânicas como *streaks* (ofensivas) com a retenção de longo prazo.

## 📊 Questão Central
As mecânicas de gamificação realmente impactam o comportamento dos usuários de forma sustentável?

## 🛠️ Tecnologias Utilizadas
* **Python 3.x**
* **Pandas** (Tratamento de dados)
* **Matplotlib/Seaborn** (Visualização)
* **Google Play Scraper** (Análise de Sentimento)

## 📂 Estrutura do Repositório
* `/data`: Datasets utilizados (Links para o Kaggle).
* `/notebooks`: Análise exploratória e cálculo de métricas (Churn, DAU/MAU, Retention).
* `/visuals`: Gráficos gerados para as entregas acadêmicas.
* `/scripts`: Scripts Python de coleta, processamento de NLP e análise comportamental.

## 📜 Descrição dos Scripts

O código fonte está estruturado em pequenos scripts focados, divididos por contexto histórico:

### 📥 1. Scripts de Coleta de Dados (Os "Buscadores")
* **`scrape_reviews.py`**: Baixa as 10.000 avaliações mais recentes da Play Store (cenário atual / 2026).
* **`get2019data.py`**: Um scraper com paginação e backups para minerar avaliações históricas antigas (2014 a 2015) burlando bloqueios da Play Store.

### ⏳ 2. Scripts da "Era de Ouro" (Dados de 2014 e 2015)
* **`retention_analysis.py`**: Desenha a curva de retenção do app com base nos logs de acesso (`data.tsv`).
* **`historical_behavioral_churn.py`**: Analisa o comportamento inicial dos usuários e prova que a falta de consistência (quebra de *streak* nos primeiros 15 dias) era o principal fator de abandono.
* **`historical_review_analysis.py`**: Analisa as reviews antigas e gera o gráfico de reclamações da época (focadas em pequenos bugs de sincronização, não em monetização).

### 📱 3. Scripts da "Era Moderna" (Dados Recentes / 2026)
* **`gamification_nlp_analysis.py`**: *(Validador Positivo)* Mapeia palavras-chave em reviews de notas altas (4 e 5 estrelas) mostrando a força contínua de retenção dos *streaks* e metas.
* **`review_complaints_analysis.py`**: *(Diagnóstico do Abandono)* Mapeia as reclamações nas reviews negativas (1 e 2 estrelas) provando o impacto negativo do excesso de anúncios e *paywall*.
* **`veteran_users_analysis.py`**: *(Ponte entre Eras)* Isola textos de usuários antigos ("uso há 10 anos") que estão saindo agora, provando a mudança de satisfação e quebra de usabilidade com o tempo.

### 🛠️ 4. Scripts Utilitários
* **`load_data.py`**: Teste de sanidade para checar o carregamento dos datasets locais e colunas lidas.

## 🚀 Como Executar
1. Clone o repositório: `git clone https://github.com/SEU-USUARIO/health-gamification-analysis`
2. Instale as dependências: `pip install -r requirements.txt`