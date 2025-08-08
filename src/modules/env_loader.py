from pathlib import Path
from datetime import date

BASE_HU = 'hu'
BASE_PRESSLOG = 'presslog'

PATH = Path(__file__).resolve().parents[2]
PATH_LOGS = PATH / 'logs'
PATH_MULTAS = PATH / 'output'
API_KEY = 'ecc6c18885c04f4875aba19fe4eeba18'

DIAS_DA_SEMANA = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'Sabado']

PATH_LOGS.mkdir(exist_ok=True)
PATH_MULTAS.mkdir(exist_ok=True)
