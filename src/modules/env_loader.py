# config/config.py
import os
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
def configurar_logging(nome_log='app.log'):
    logging.basicConfig(filename=LOGS_DIR / nome_log, level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
