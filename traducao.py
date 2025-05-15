import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Configurações
diretorio_origem = r'C:\Users\Ronaldo\Documents\Repo\ghcertified\content\questions\copilot'
diretorio_destino = r'C:\Users\Ronaldo\Documents\Repo\ghcertified\content\questions\copilot\traduzidas'
total_questoes = 124

# Configuração do ChromeDriver (substitua pelo seu caminho)
service = Service(r'D:\chromedriver-win64\chromedriver.exe')

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=service, options=options)

def traduzir_texto(driver, texto):
    try:
        driver.get("https://translate.google.com/?sl=en&tl=pt&op=translate")
        
        # Aguarda e insere texto
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "textarea[aria-label='Texto de origem']"))
        ).send_keys(texto[:5000])
        
        # Aguarda tradução (múltiplos seletores como fallback)
        try:
            traducao = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[lang='pt']")) or
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-result-index]")) or
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Tradução']"))
            )
            return traducao.text
        except TimeoutException:
            print("Tempo de espera excedido para tradução")
            return texto
            
    except Exception as e:
        print(f"Erro durante tradução: {str(e)}")
        return texto

def processar_questoes():
    driver = setup_driver()
    
    for i in range(1, total_questoes + 1):
        num_questao = f"{i:03d}"
        arquivo_origem = os.path.join(diretorio_origem, f"question-{num_questao}.md")
        arquivo_destino = os.path.join(diretorio_destino, f"questao-{num_questao}.md")
        
        try:
            with open(arquivo_origem, 'r', encoding='utf-8') as f:
                conteudo = f.read()
            
            # Traduz em partes se for muito longo
            if len(conteudo) > 4000:
                partes = [conteudo[i:i+3500] for i in range(0, len(conteudo), 3500)]
                conteudo_traduzido = ""
                for parte in partes:
                    conteudo_traduzido += traduzir_texto(driver, parte)
                    time.sleep(8)  # Intervalo maior para evitar bloqueio
            else:
                conteudo_traduzido = traduzir_texto(driver, conteudo)
                time.sleep(5)
            
            with open(arquivo_destino, 'w', encoding='utf-8') as f:
                f.write(conteudo_traduzido)
            
            print(f"Questão {num_questao} traduzida com sucesso!")
            
        except Exception as e:
            print(f"Erro na questão {num_questao}: {str(e)}")
    
    driver.quit()

if __name__ == "__main__":
    os.makedirs(diretorio_destino, exist_ok=True)
    print("Iniciando tradução...")
    processar_questoes()
    print("Processo concluído!")