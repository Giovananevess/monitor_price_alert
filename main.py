import cloudscraper
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import os
import time

# --- CONFIGURAÇÕES ---
TOKEN = "8748353509:AAHTf1OtzXeZKMjqSLta-44E2a00JXOXouE"
CHAT_ID = "7061790855"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        import requests
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

# --- EXTRAÇÃO (VERSÃO BLINDADA) ---
def capturar_dados(url):
    # Criamos o scraper que simula um navegador real
    # Tente substituir a linha do scraper por esta configuração mais pesada:
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        },
        interpreter='nodejs' # Isso tenta simular o carregamento de scripts reais
    )

    # Tentamos até 3 vezes com um pequeno intervalo se falhar
    for i in range(3):
        try:
            print(f"Tentativa {i+1}: Acessando o site...")
            response = scraper.get(url, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Seletor 1: Tenta o título padrão
                titulo_elem = soup.find('h1') or soup.select_one('.ui-pdp-title')
                
                if titulo_elem:
                    titulo = titulo_elem.text.strip()
                    
                    # Busca o preço pela meta tag (mais confiável em servidores)
                    preco_meta = soup.find('meta', {'property': 'twitter:data2'})
                    if preco_meta:
                        valor_texto = preco_meta.get('content').replace('R$', '').replace('.', '').replace(',', '.').strip()
                        preco_final = float(valor_texto)
                    else:
                        # Fallback para o seletor de classe
                        preco_elem = soup.select_one('.andes-money-amount__fraction')
                        if not preco_elem:
                            continue # Tenta a próxima iteração
                        
                        preco_inteiro = preco_elem.text.replace('.', '')
                        centavos_elem = soup.select_one('.andes-money-amount__cents')
                        centavos = centavos_elem.text if centavos_elem else "00"
                        preco_final = float(f"{preco_inteiro}.{centavos}")

                    return {
                        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "produto": titulo,
                        "preco": preco_final
                    }
            
            print(f"Aviso: Status {response.status_code} na tentativa {i+1}. Aguardando...")
            time.sleep(5) # Espera 5 segundos antes de tentar de novo
            
        except Exception as e:
            print(f"Erro na tentativa {i+1}: {e}")
            time.sleep(5)

    # Se sair do loop sem retornar, deu erro total
    raise Exception("O Mercado Livre bloqueou todas as tentativas de acesso do servidor.")

# --- PERSISTÊNCIA PARTICIONADA ---
def salvar_historico_particionado(novo_dado):
    hoje = datetime.datetime.now()
    caminho = f"data/year={hoje.year}/month={hoje.month:02d}/day={hoje.day:02d}/"
    
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        
    arquivo = os.path.join(caminho, 'precos.csv')
    df_novo = pd.DataFrame([novo_dado])
    
    if os.path.exists(arquivo):
        df_novo.to_csv(arquivo, mode='a', header=False, index=False)
    else:
        df_novo.to_csv(arquivo, index=False)

# --- LÓGICA DE ALERTA ---
def verificar_alerta(preco_atual, preco_desejado, nome_produto):
    if preco_atual <= preco_desejado:
        msg = f"🚨 BAIXOU O PREÇO!\n\nPRODUTO: {nome_produto}\nPREÇO AGORA: R$ {preco_atual}\nALVO: R$ {preco_desejado}"
        enviar_telegram(msg)
        print(f"✅ Sucesso! Alerta enviado para o Telegram.")
    else:
        print(f"ℹ️ Preço de R$ {preco_atual} ainda acima do alvo (R$ {preco_desejado}).")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    # Link de um produto na Amazon para teste
    url_alvo = "https://www.amazon.com.br/dp/B088GHNCST" 
    meu_preco_alvo = 5000.00
    
    meu_preco_alvo = 8000.00 

    print("--- INICIANDO PIPELINE DE MONITORAMENTO ---")
    try:
        dados_coletados = capturar_dados(url_alvo)
        salvar_historico_particionado(dados_coletados)
        verificar_alerta(dados_coletados['preco'], meu_preco_alvo, dados_coletados['produto'])
        print("--- PIPELINE FINALIZADO COM SUCESSO ---")
    except Exception as e:
        print(f"❌ Falha crítica: {e}")