# 🚀 Monitor de Preços Automatizado com Alerta no Telegram

Este projeto é um Pipeline de Dados ponta a ponta que monitora preços de produtos e notifica o usuário via Telegram quando o valor atinge o alvo desejado. Ele foi desenvolvido com foco em boas práticas de **Engenharia de Dados** e **Automação**.

## 🎯 Objetivo
Automatizar a coleta de preços e o armazenamento histórico, eliminando a necessidade de verificação manual e permitindo a análise de tendências de preços ao longo do tempo.

---

## 🛠️ Tecnologias Utilizadas

* **Python 3.10+**: Linguagem base do projeto.
* **Pandas**: Processamento de dados e estruturação de dataframes.
* **Cloudscraper & BeautifulSoup4**: Extração de dados (Web Scraping) contornando proteções anti-bot.
* **GitHub Actions**: Orquestração e automação do pipeline na nuvem.
* **Telegram Bot API**: Sistema de mensageria e alertas em tempo real.

---

## 🏗️ Arquitetura do Projeto

O projeto segue padrões de organização de **Data Lakes**, utilizando o conceito de particionamento para otimizar a escalabilidade:

### 1. Ingestão e Processamento
O script `main.py` realiza a captura do dado, trata strings de preços e converte para tipos numéricos (`float`), garantindo a integridade da informação.

### 2. Armazenamento Particionado
Em vez de um arquivo único e pesado, os dados são salvos em uma estrutura de pastas baseada em datas:
`data/year=YYYY/month=MM/day=DD/precos.csv`
> *Este formato é amplamente utilizado em ambientes de Big Data (como AWS S3 e Hadoop) para agilizar consultas e reduzir custos de processamento.*

### 3. Automação (CI/CD)
Através do GitHub Actions, o monitoramento é executado de forma agendada (Cron Job), garantindo que o pipeline rode sem a necessidade de um computador local ligado.

---

## 🚀 Como Rodar o Projeto

1. **Clonar o repositório:**
   ```bash
   git clone [https://github.com/Giovananevess/monitor_price_alert.git](https://github.com/Giovananevess/monitor_price_alert.git)
   cd monitor_price_alert
