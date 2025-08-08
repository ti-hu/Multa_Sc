import os
import time
import logging
import threading
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Imports dos módulos do projeto
from sec import acessos
from modules.env_loader import DIAS_DA_SEMANA, DIR_DIAS, configurar_logging
from modules.banco import get_info_veiculos
from modules.portal_detran_sc import (
    click_certificado,
    login_detran_sc,
    verificar_debitos_multas,
)


def dividir_dataframe(df: pd.DataFrame, partes: int = 7) -> List[pd.DataFrame]:
    """Divide o DataFrame em `partes` sub-DataFrames intercalados."""
    return [df.iloc[i::partes].reset_index(drop=True) for i in range(partes)]


def gerar_planilhas_iniciais():
    """Gera planilhas Excel iniciais para cada dia da semana dentro da pasta 'Dias'."""
    os.makedirs("Dias", exist_ok=True)
    df_all = get_info_veiculos("hu")
    for idx, parte in enumerate(dividir_dataframe(df_all)):
        nome = Path(DIR_DIAS) / f"{DIAS_DA_SEMANA[idx]}.xlsx"
        parte.to_excel(nome, index=False)
        logging.info(f"Planilha gerada: {nome} ({len(parte)} registros)")


def obter_parte_do_dia() -> Tuple[Path, pd.DataFrame]:
    """Retorna o caminho e DataFrame da planilha correspondente ao dia atual."""
    dia_idx = datetime.today().weekday()
    if dia_idx > 4:
        raise SystemExit("Fim de semana: não há o que processar.")

    arquivo = Path(DIR_DIAS) / f"{DIAS_DA_SEMANA[dia_idx]}.xlsx"
    if not arquivo.exists():
        raise FileNotFoundError(f"Planilha do dia não encontrada: {arquivo}")

    df = pd.read_excel(arquivo)
    logging.info(f"Planilha carregada: {arquivo} ({len(df)} registros)")
    return arquivo, df


def atualizar_planilha(caminho: Path, novos: pd.DataFrame) -> None:
    """Anexa novos registros à planilha existente ou cria nova se não existir."""
    if caminho.exists():
        df_existente = pd.read_excel(caminho)
        df_final = pd.concat([df_existente, novos], ignore_index=True)
    else:
        df_final = novos
    df_final.to_excel(caminho, index=False)
    logging.info(f"Planilha atualizada: {caminho} ({len(df_final)} registros)")


def executar_fluxo_por_parte(df_parte: pd.DataFrame, api_key: str) -> pd.DataFrame:
    """Realiza o fluxo de consulta no portal e retorna DataFrame de resultados."""
    # Inicia thread de clique em certificado (daemon)
    cert_thread = threading.Thread(target=click_certificado, daemon=True)
    cert_thread.start()

    driver = login_detran_sc(api_key)
    resultados = []

    for _, row in df_parte.iterrows():
        placa, renavam = row.get('Placa'), row.get('Renavam')
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
            time.sleep(2)
            status, info = verificar_debitos_multas(driver, placa, renavam)
            # Agrupa débitos
            for deb in info.get('debitos', []):
                resultados.append({**deb, 'Placa': placa, 'Renavam': renavam, 'Tipo': 'Débito', 'Status Geral': status})
            # Agrupa multas
            for multa in info.get('multas', []):
                resultados.append({**multa, 'Placa': placa, 'Renavam': renavam, 'Tipo': 'Multa', 'Status Geral': status})
            # Caso sem registros
            if not info.get('debitos') and not info.get('multas'):
                resultados.append({'Placa': placa, 'Renavam': renavam, 'Tipo': 'Nenhum', 'Status Geral': status})

        except Exception as e:
            resultados.append({'Placa': placa, 'Renavam': renavam, 'Tipo': 'Erro', 'Descrição': str(e), 'Status Geral': 'Erro'})
        finally:
            driver.get("https://servicos.detran.sc.gov.br/consulta-dossie-veiculo")
            time.sleep(2)

    driver.quit()
    return pd.DataFrame(resultados)


def main():
    configurar_logging()
    try:
        # Gera planilhas se não existirem
        if not all((Path("Dias") / f"{d}.xlsx").exists() for d in DIAS_DA_SEMANA):
            gerar_planilhas_iniciais()

        arquivo, df_dia = obter_parte_do_dia()
        df_resultados = executar_fluxo_por_parte(df_dia, acessos['captcha_API_key'])
        atualizar_planilha(arquivo, df_resultados)

    except Exception as e:
        logging.exception(f"FATAL: {e}")
        raise


if __name__ == '__main__':
    main()
