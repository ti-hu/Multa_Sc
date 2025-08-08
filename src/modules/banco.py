import pandas as pd
from mod_dados import list2string
from mod_db import database
from sqlalchemy import text
from modules.env_loader import BASE_HU, BASE_PRESSLOG


def get_info_veiculos(empresa: str) -> pd.DataFrame:
    db = database(BASE_PRESSLOG) if empresa.upper() == 'PRESSLOG' else database(BASE_HU)

    query = """
    SELECT 
        v.placa as "Placa",
        v.codveiculo as "Cod Veic",
        v.codcidade as"Cod Cidade",
        v.datavendaefetiva IS NOT NULL as "Vendido",
        renavam as "Renavam"
    FROM 
        veiculo v
    WHERE 
        v.codcidade ='733'
        AND v.datavendaefetiva IS NULL
    """

    print(f"[get_info_veiculos] Buscando dados para empresa: {empresa}")
    return db.query(query)


def get_info_veiculos_renavam(placa: str) -> pd.DataFrame:
    # Escolhe o banco com base na placa
    db = database(BASE_PRESSLOG) if placa.upper() == 'PRESSLOG' else database(BASE_HU)

    # Query corrigida para filtrar pela placa específica e retornar só placa e renavam
    query = f"""
    SELECT 
        v.placa AS Placa,
        v.renavam AS Renavam
    FROM 
        veiculo v
    WHERE 
        v.cavalo = 'S' 
        AND v.veiculoproprio = 'S'
        AND v.datavendaefetiva IS NULL
        AND v.placa = '{placa.upper()}'
    """

    print(f"[get_info_veiculos_renavam] Buscando dados para a placa: {placa.upper()}")
    return db.query(query)
