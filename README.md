# 🚀 Monitor de Preços Automatizado: Pipeline de Dados Ponta a Ponta

Este projeto é um **Pipeline de Dados** completo que monitora preços de produtos e notifica o usuário via Telegram. Ele foi desenhado para simular um ambiente real de Engenharia de Dados, focando em **escalabilidade, segurança de credenciais e automação em nuvem**.

## 🎯 Objetivo
Criar um fluxo automatizado que coleta, processa e armazena dados históricos de preços, utilizando uma arquitetura de pastas que facilita a análise de Big Data.

---

## 🛠️ Stack Tecnológica

* **Python**: Linguagem principal para o motor do pipeline.
* **Pandas**: Estruturação e manipulação de dados.
* **GitHub Actions**: Orquestrador de CI/CD para rodar o script automaticamente.
* **Telegram Bot API**: Sistema de notificação e alertas em tempo real.
* **Dotenv**: Gerenciamento de variáveis de ambiente para segurança local.

---

## 🏗️ Arquitetura e Boas Práticas

O projeto foi construído seguindo padrões profissionais de engenharia:

### 1. Segurança de Credenciais
Utilizei **Variáveis de Ambiente** para proteger o Token do Bot e o Chat ID. No ambiente local, as chaves são gerenciadas via arquivo `.env` (protegido pelo `.gitignore`), enquanto na nuvem são gerenciadas pelo **GitHub Secrets**.

### 2. Armazenamento Particionado (Data Lake)
Os dados não são jogados em um arquivo único. Eles seguem uma estrutura de particionamento por data:
`data/year=YYYY/month=MM/day=DD/precos.csv`  
> *Essa prática é essencial em ambientes profissionais (como AWS S3 ou Azure Data Lake) para otimizar a velocidade de leitura e reduzir custos de processamento.*

### 3. Automação Inteligente
O pipeline está configurado no **GitHub Actions** para rodar em intervalos programados (Cron Job), garantindo monitoramento contínuo sem intervenção humana.

---

## 📂 Estrutura do Repositório

```text
├── .github/workflows/
│   └── main.yml        # Configuração da automação no GitHub
├── data/               # Armazenamento particionado dos CSVs
├── .gitignore          # Proteção contra upload de arquivos sensíveis
├── main.py             # Script principal do pipeline
├── requirements.txt    # Dependências do projeto
└── README.md           # Documentação




🚀 Como Executar
Clonagem e Dependências:

Bash
git clone [https://github.com/Giovananevess/monitor_price_alert.git](https://github.com/Giovananevess/monitor_price_alert.git)
pip install -r requirements.txt
Configuração Local:
Crie um arquivo .env na raiz com:

Plaintext
TELEGRAM_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_id_aqui
Execução:

Bash
python main.py
