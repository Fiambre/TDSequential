import numpy as np
import pandas as pd

def calculate_tdst_levels(df, high_col='High', low_col='Low') -> pd.DataFrame:
    """
    Calcula niveles TDST (Tom DeMark Support/Resistance) tras completar un Setup.

    Reglas:
    - Tras un Buy Setup (9), se traza un nivel de resistencia (TDST) = máximo entre las velas 1 a 9.
    - Tras un Sell Setup (9), se traza un nivel de soporte (TDST) = mínimo entre las velas 1 a 9.
    - El nivel se mantiene activo hasta que el precio lo rompe (por debajo en Buy, por encima en Sell).

    Requiere que el DataFrame tenga las columnas:
      - 'buy_setup_count' con valores de 1 a 9 para los buy setups
      - 'sell_setup_count' con valores de 1 a 9 para los sell setups

    Parámetros:
    - df: DataFrame con las columnas de conteo de setups.
    - high_col: nombre de la columna de máximos (default: 'High').
    - low_col: nombre de la columna de mínimos (default: 'Low').

    Retorna:
    - DataFrame con dos nuevas columnas:
        - 'tdst_buy': nivel TDST tras cada buy setup
        - 'tdst_sell': nivel TDST tras cada sell setup
    """
    df = df.copy()
    df['tdst_buy'] = np.nan
    df['tdst_sell'] = np.nan

    active_buy_tdst = None
    active_sell_tdst = None

    for i in range(len(df)):
        # Detectar fin de Buy Setup (vela 9)
        if i >= 8 and df.loc[i, 'buy_setup_count'] == 9:
            active_buy_tdst = df.loc[i - 8:i, high_col].max()

        # Detectar fin de Sell Setup (vela 9)
        if i >= 8 and df.loc[i, 'sell_setup_count'] == 9:
            active_sell_tdst = df.loc[i - 8:i, low_col].min()

        # Asignar niveles actuales (persisten)
        df.at[i, 'tdst_buy'] = active_buy_tdst
        df.at[i, 'tdst_sell'] = active_sell_tdst

        # Invalidar TDST si el precio lo rompe
        if active_buy_tdst is not None and df.loc[i, low_col] < active_buy_tdst:
            active_buy_tdst = None

        if active_sell_tdst is not None and df.loc[i, high_col] > active_sell_tdst:
            active_sell_tdst = None

    return df[['tdst_buy', 'tdst_sell']]
