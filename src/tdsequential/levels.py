import numpy as np
import pandas as pd

def calculate_tdst_levels(df, high_col='High', low_col='Low') -> pd.DataFrame:
    """
    Calcula niveles TDST (Tom DeMark Support/Resistance) tras completar un Setup.

    Reglas:
    - Tras un Buy Setup (9), se traza un nivel (TDST Buy) = LOW más bajo de las velas 1 a 9 del setup.
    - Tras un Sell Setup (9), se traza un nivel (TDST Sell) = HIGH más alto de las velas 1 a 9 del setup.
    - El nivel se mantiene activo hasta que el precio lo rompe:
        - Buy TDST se invalida si Low < TDST Buy
        - Sell TDST se invalida si High > TDST Sell

    Requiere columnas:
      - 'buy_setup_count' (1..9)
      - 'sell_setup_count' (1..9)

    Retorna:
    - El DataFrame original con dos nuevas columnas:
        - 'tdst_buy'
        - 'tdst_sell'
    """
    df = df.copy()

    # Crear columnas si no existen
    if 'tdst_buy' not in df.columns:
        df['tdst_buy'] = np.nan
    else:
        df['tdst_buy'] = np.nan

    if 'tdst_sell' not in df.columns:
        df['tdst_sell'] = np.nan
    else:
        df['tdst_sell'] = np.nan

    active_buy_tdst = None
    active_sell_tdst = None

    n = len(df)
    for i in range(n):
        # Invalidar TDST ANTES de asignar (verificar ruptura en barra anterior)
        if active_buy_tdst is not None and df.loc[i, low_col] < active_buy_tdst:
            active_buy_tdst = None

        if active_sell_tdst is not None and df.loc[i, high_col] > active_sell_tdst:
            active_sell_tdst = None

        # Detectar fin de Buy Setup (vela 9) - usar Low del rango
        if i >= 8 and df.loc[i, 'buy_setup_count'] == 9:
            # TDST Buy = Low más bajo de las barras 1-9 del setup (SOPORTE)
            active_buy_tdst = df.loc[i - 8:i, low_col].min()

        # Detectar fin de Sell Setup (vela 9) - usar High del rango
        if i >= 8 and df.loc[i, 'sell_setup_count'] == 9:
            # TDST Sell = High más alto de las barras 1-9 del setup (RESISTENCIA)
            active_sell_tdst = df.loc[i - 8:i, high_col].max()

        # Asignar niveles actuales (persisten hasta que se rompan)
        df.at[i, 'tdst_buy'] = active_buy_tdst
        df.at[i, 'tdst_sell'] = active_sell_tdst

    return df
