import re
import time
import logging
import pyautogui
import pandas as pd

from pathlib import Path
from typing import List, Optional
from twocaptcha import TwoCaptcha

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC

# Configuração de API key local
from modules.env_loader import API_KEY


# ------------------- DRIVER & CERTIFICADO -------------------
def get_chrome_driver() -> webdriver.Chrome:
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option("prefs", {"profile.default_content_setting_values.geolocation": 2})
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.maximize_window()
    return driver


# ------------------- CAPTCHA -------------------
def resolver_hcaptcha(driver, sitekey, url, api_key):
    """
    Resolve um desafio hCaptcha usando 2Captcha, com prints detalhados.

    Args:
        driver (webdriver): Instância do navegador Selenium.
        sitekey (str): Chave do site do hCaptcha.
        url (str): URL da página com o captcha.
        api_key (str): Chave da API do 2Captcha.

    Returns:
        bool: True se captcha for resolvido, False caso contrário.
    """
    logging.info('>> Iniciando resolução de hCaptcha via 2Captcha')
    print("🔐 Iniciando resolução de hCaptcha com 2Captcha")

    solver = TwoCaptcha(api_key)

    try:
        print("📡 Enviando desafio para o 2Captcha...")
        result = solver.hcaptcha(sitekey=sitekey, url=url)
        print("✅ Token recebido do 2Captcha:")
        print(f"🔑 {result['code'][:10]}...")

        token = result['code']

        print("🧩 Inserindo token no campo '[name=h-captcha-response]'...")
        driver.execute_script(
            """
            const field = document.querySelector('[name="h-captcha-response"]');
            if (field) {
                field.style.display = 'block';
                field.value = arguments[0];
                console.log('🟩 Token inserido no campo h-captcha-response.');
            } else {
                console.log('🟥 Campo h-captcha-response não encontrado.');
            }
        """,
            token,
        )

        print("🚀 Executando callback do hCaptcha (onHcaptchaCallback)...")

        print("🔄 esperando para verificar certificado")

        driver.execute_script(
            """
            if(window.onHcaptchaCallback) {
                console.log('🟦 Callback onHcaptchaCallback encontrado, executando...');
                window.onHcaptchaCallback(arguments[0]);
            } else if(window.hcaptcha && window.hcaptcha.getResponse) {
                console.log('🟨 Callback padrão do hCaptcha, executando getResponse...');
                window.hcaptcha.getResponse(window.hcaptchaWidgetId);
            } else {
                console.log('🟥 Nenhum callback do hCaptcha encontrado.');
            }
        """,
            token,
        )

        print("✅ Callback executado com sucesso.")
        logging.info('>> hCaptcha resolvido e formulário submetido com sucesso.')
        print("✅ Processo finalizado com sucesso.")
        return True

    except Exception as e:
        print("❌ Erro durante resolução do hCaptcha.")
        print(f"💥 Detalhes: {e}")
        logging.error(f"Erro ao resolver hCaptcha: {e}")
        return False


def click_certificado():
    print("[Início] Vou esperar 1:24 (95 segundos) antes de clicar no certificado...")
    time.sleep(95)
    print("[Atenção] Faltam 10 segundos para o clique...")
    time.sleep(5)
    print("[Preparar] Faltam 5 segundos...")
    time.sleep(5)

    print("[Clique 1] Movendo até o botão do certificado (x=691, y=339)...")
    pyautogui.moveTo(x=739, y=215, duration=0.2)
    print("[Clique 1] Clicando no botão do certificado!")
    pyautogui.click()

    print("[Clique 2] Movendo até o botão 'OK' (x=976, y=401)...")
    pyautogui.moveTo(x=976, y=362, duration=0.2)
    print("[Clique 2] Clicando no 'OK' (duplo clique)...")
    pyautogui.click()
    pyautogui.click()

    print("[Finalizado] Todos os cliques foram realizados com sucesso.")
    logging.info("✔️ Certificado clicado via PyAutoGUI.")


def detectar_e_resolver_hcaptcha(driver, api_key):
    """
    Detecta a presença de um hCaptcha e tenta resolvê-lo automaticamente.

    Args:
        driver (webdriver): Instância ativa do Chrome.
        api_key (str): Chave da API do 2Captcha.

    Returns:
        bool: True se captcha foi resolvido, False caso contrário.
    """
    try:
        print("🔎 Aguardando presença do iframe do hCaptcha...")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'hcaptcha')]")))
        print("✅ Iframe do hCaptcha encontrado.")

        iframe = driver.find_element(By.XPATH, "//iframe[contains(@src, 'hcaptcha')]")
        src = iframe.get_attribute("src")
        print(f"📦 SRC do iframe: {src}")

        from urllib.parse import urlparse, parse_qs

        print("🔍 Extraindo sitekey da URL do iframe (fragmento após #)...")
        fragment = urlparse(src).fragment
        print(f"🧩 Fragmento da URL: {fragment}")
        params = parse_qs(fragment)
        print(f"🧾 Parâmetros extraídos do fragmento: {params}")

        sitekey = params.get("sitekey", [None])[0]
        sitekey = "93b08d40-d46c-400a-ba07-6f91cda815b9"
        print(f"🔑 Sitekey encontrada: {sitekey}")

        if not sitekey:
            logging.warning("⚠️ Sitekey não encontrada na URL do iframe.")
            return False

        current_url = driver.current_url
        print(f"🌐 URL atual da página: {current_url}")

        print("🚀 Chamando função para resolver o hCaptcha...")
        resultado = resolver_hcaptcha(driver, sitekey, current_url, api_key)

        if resultado:
            print("🎉 hCaptcha resolvido com sucesso!")
        else:
            print("❌ Falha ao resolver o hCaptcha.")

        return resultado

    except Exception as e:
        print("⚠️ Exceção capturada durante a detecção do hCaptcha.")
        print(f"🧨 Detalhes do erro: {e}")
        logging.info(">> Nenhum hCaptcha detectado ou erro na detecção.")
        return False


# ------------------- DETRAN-SC -------------------
def login_detran_sc(api_key: str) -> webdriver.Chrome:

    driver = get_chrome_driver()
    wait = WebDriverWait(driver, 15)

    try:

        print("[1] Carregando Pagina.")
        driver.get("https://servicos.detran.sc.gov.br/login")
        time.sleep(2)

        # --- 1) clicar no botão Gov.Br que abre nova janela ---
        print("[2] Localizando botão Gov.Br...")
        btn_govbr = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/section/div[2]/div[2]/form/div[1]/button")))
        btn_govbr.click()

        # --- 2) espera até que o número de janelas seja 2 ---
        print("[3] Clicou no Gov.Br, esperando nova janela...")
        wait.until(EC.number_of_windows_to_be(2))
        janelas = driver.window_handles
        janela_original = janelas[0]
        nova_janela = janelas[1]

        # --- 3) muda o foco para a nova janela ---
        print(f"[4] Janelas abertas: {janelas}")
        driver.switch_to.window(nova_janela)
        print(f"[5] Foco na nova janela: {nova_janela}")
        time.sleep(2)

        # --- após driver.switch_to.window(nova_janela) e time.sleep(2) ---
        print("[6] Aguardando botão de certificado digital Gov.Br...")
        btn_cert = wait.until(EC.element_to_be_clickable((By.ID, "login-certificate")))
        print("[7] Clicou em 'Seu certificado digital'.")
        btn_cert.click()

        print("[8] Resolvendo Captcha...")
        time.sleep(2)
        detectar_e_resolver_hcaptcha(driver, api_key)

        # --- volta o foco para a janela original ---
        driver.switch_to.window(janela_original)
        print(f"[9] Foco de volta para a janela original: {janela_original}")
        time.sleep(2)

        try:
            # 2) Aguarda e fecha o modal de privacidade
            print("[pesquisar_placa] Aguardando modal de privacidade...")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.modal")))
            print("[pesquisar_placa] Modal detectado.")

            print("[pesquisar_placa] Aguardando botão de fechar (btn-close) clicável...")
            btn_fecha = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.modal button.btn-close")))
            print("[pesquisar_placa] Botão de fechar encontrado, clicando...")
            btn_fecha.click()
            print("[pesquisar_placa] Modal fechado com sucesso.")
        except Exception as e:
            print("sem modal")
            pass

        # 3) Clica em "Consultar Veículos"
        print("[pesquisar_placa] Buscando botão 'Consultar Veículos'...")
        elemento = driver.find_element(By.XPATH, "//a[contains(., 'Consultar') and contains(., 'Veículos')]")
        elemento.click()
        print("[pesquisar_placa] Botão 'Consultar Veículos' clicado.")

        return driver

    except Exception as err:
        logging.error(f"[Login] Erro: {err}")
        driver.quit()
        raise


def verificar_debitos_multas(driver: webdriver.Chrome, placa: str, renavam: str) -> tuple[str, dict]:
    dados = {'debitos': [], 'multas': []}
    status = "Sem Débitos ou Multas"

    try:
        # Primeiro clique no botão de consulta
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(2)

        # Espera os campos de entrada serem visíveis
        campos = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "form.consulta-dossie__form label.form-label")))

        id_placa = campos[0].get_attribute("for")
        id_renavam = campos[1].get_attribute("for")

        # Preenche Placa
        campo_placa = driver.find_element(By.CSS_SELECTOR, f"input#{id_placa}")
        campo_placa.clear()
        campo_placa.send_keys(placa)

        # Preenche Renavam
        campo_renavam = driver.find_element(By.CSS_SELECTOR, f"input#{id_renavam}")
        campo_renavam.clear()
        campo_renavam.send_keys(renavam)

        time.sleep(4)

        # Submete novamente o formulário
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(4)

    except Exception as e:
        print(f"[ERRO AO PREENCHER FORMULÁRIO] {e}")
        return "Erro ao preencher dados", {'debitos': 'erro', 'multas': 'erro'}

    # Tenta extrair débitos
    try:
        blocos = driver.find_elements(By.CLASS_NAME, 'lista-debitos__item')[1:]
        for bloco in blocos:
            divs = bloco.find_elements(By.TAG_NAME, 'div')
            if len(divs) >= 3:
                dados['debitos'].append({'descricao': divs[0].text, 'vencimento': divs[1].text, 'valor': divs[2].text})
        if dados['debitos']:
            status = "Com Débitos"
    except Exception as e:
        print(f"[ERRO AO LER DÉBITOS] {e}")

    # Tenta extrair multas
    try:
        acc = driver.find_element(By.XPATH, "//*[contains(text(),'INFRAÇÕES')]/..")
        driver.execute_script("arguments[0].scrollIntoView();", acc)
        acc.click()
        time.sleep(2)

        itens = acc.find_elements(By.CLASS_NAME, 'lista-dados__item')
        multa = {}
        for it in itens:
            try:
                key = it.find_element(By.CLASS_NAME, 'lista-dados__item--title').text.strip()
                val = it.find_element(By.TAG_NAME, 'p').text.strip()
                multa[key] = val
            except:
                continue

        if multa:
            dados['multas'].append(multa)
            status = status.replace("Sem", "Com") if status == "Sem Débitos ou Multas" else status + " e Multas"
    except Exception as e:
        print(f"[ERRO AO LER MULTAS] {e}")

    return status, dados
