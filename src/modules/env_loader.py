# config/config.py
import os
from datetime import datetime
from pathlib import Path
import logging

# Constantes de diretório
BASE_HU = 'hu'
BASE_PRESSLOG = 'presslog'

ROOT_DIR = Path(__file__).resolve().parents[2]
LOGS_DIR = ROOT_DIR / 'logs'
LOGS_DIR.mkdir(parents=True, exist_ok=True)

DIR_DIAS = ROOT_DIR / 'output' / 'hu' / 'Dias'
DIR_DIAS.mkdir(parents=True, exist_ok=True)

# Constantes de configuração
API_KEY = 'ecc6c18885c04f4875aba19fe4eeba18'
DIAS_DA_SEMANA = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']


# Configuração de logging
def configurar_logging():
    # Pasta do mês (ex: logs/2025-08)
    pasta_mes = LOGS_DIR / datetime.today().strftime('%Y-%m')
    pasta_mes.mkdir(parents=True, exist_ok=True)

    # Nome do arquivo com dia e hora (ex: 2025-08-07_09-30-00.log)
    nome_arquivo_log = pasta_mes / f'Multas_DENT_SC_{datetime.today():%Y-%m-%d_%H-%M-%S}.log'

    # Configuração do logging
    logging.basicConfig(filename=nome_arquivo_log, level=logging.INFO, format='%(asctime)s - %(levelname)s : %(message)s', encoding='utf-8')
