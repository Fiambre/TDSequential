"""
Módulo principal con la lógica de cálculo del indicador TD Sequential y TD Countdown.
Ajustado para que el resultado sea consistente con la lógica del código del gráfico:

- Setup:
  - Se inicia solo por Price Flip (mismas condiciones del gráfico).
  - Se incrementa mientras se cumpla Close < Close[i-4] (buy) o Close > Close[i-4] (sell).
  - Se rompe si no se cumple la condición antes de completar 9.

- Countdown:
  - Se inicia en la MISMA barra donde se completa el Setup (barra 9).
  - Se incrementa (no necesariamente consecutivo) con:
      Buy:  Close[i] <= Low[i-2]
      Sell: Close[i] >= High[i-2]
  - Se cancela SOLO si aparece un Setup contrario completado (un 9 contrario) DESPUÉS.
  - Puede haber "pausas": si no cumple condición, el valor en esa barra es 0.
  - Si llega a 13, se marca 13 en esa barra.

Nota:
- Esta implementación calcula setups y luego aplica countdown por cada setup completado,
  como en tu código del gráfico, en vez de un único countdown global.
"""

import pandas as pd
import numpy as np


def calculate_td_sequential(
    df: pd.DataFrame,
    open_col: str = "Open",
    high_col: str = "High",
    low_col: str = "Low",
    close_col: str = "Close",
    length_setup: int = 9,
    length_countdown: int = 13,
    apply_perfection: bool = True,  # se mantiene por compatibilidad (no altera el conteo)
) -> pd.DataFrame:
    # Copiar DataFrame para no modificar el original
    df_res = df.copy()

    # Validaciones mínimas
    for col in [close_col, high_col, low_col]:
        if col not in df_res.columns:
            raise ValueError(f"Columna '{col}' no encontrada en DataFrame")

    close = df_res[close_col].to_numpy(dtype=float)
    high = df_res[high_col].to_numpy(dtype=float)
    low = df_res[low_col].to_numpy(dtype=float)
    n = len(df_res)

    # ----------------------------
    # 1) SETUP (mismo estilo gráfico)
    # ----------------------------
    buy_setup_count = np.zeros(n, dtype=int)
    sell_setup_count = np.zeros(n, dtype=int)

    completed_buy_setups = []   # índices donde buy_setup_count == 9
    completed_sell_setups = []  # índices donde sell_setup_count == 9

    buy_count = 0
    sell_count = 0

    # El gráfico itera desde i=5 (requiere i-5)
    for i in range(5, n):
        # Bearish Flip -> inicia Buy Setup:
        # (Close[i] < Close[i-4]) and (Close[i-1] > Close[i-5])
        if (close[i] < close[i - 4]) and (close[i - 1] > close[i - 5]):
            # rompe sell en curso
            sell_count = 0

            # inicia buy
            buy_count = 1
            buy_setup_count[i] = buy_count
            continue

        # Bullish Flip -> inicia Sell Setup:
        # (Close[i] > Close[i-4]) and (Close[i-1] < Close[i-5])
        if (close[i] > close[i - 4]) and (close[i - 1] < close[i - 5]):
            # rompe buy en curso
            buy_count = 0

            # inicia sell
            sell_count = 1
            sell_setup_count[i] = sell_count
            continue

        # Continuar Buy Setup
        if buy_count > 0:
            if close[i] < close[i - 4]:
                buy_count += 1
                buy_setup_count[i] = buy_count
                if buy_count == length_setup:
                    completed_buy_setups.append(i)
                    buy_count = 0
            else:
                # se rompe antes de completar
                buy_count = 0

        # Continuar Sell Setup
        if sell_count > 0:
            if close[i] > close[i - 4]:
                sell_count += 1
                sell_setup_count[i] = sell_count
                if sell_count == length_setup:
                    completed_sell_setups.append(i)
                    sell_count = 0
            else:
                sell_count = 0

    # ----------------------------
    # 2) COUNTDOWN (igual que gráfico)
    #    - Por cada setup completado
    #    - Cancela solo por setup contrario completado
    # ----------------------------
    buy_countdown_count = np.zeros(n, dtype=int)
    sell_countdown_count = np.zeros(n, dtype=int)

    contrary_for_buy = set(completed_sell_setups)  # cancela buy countdown
    contrary_for_sell = set(completed_buy_setups)  # cancela sell countdown

    # Buy countdowns: desde cada setup_index (la barra del 9 incluida)
    for setup_index in completed_buy_setups:
        count = 0
        countdown_bar8_close = None

        for i in range(setup_index, n):
            # Cancelación SOLO si aparece un setup contrario completado
            if i in contrary_for_buy:
                break

            if i < 2:
                continue

            # Condición Buy Countdown: Close <= Low[i-2]
            if close[i] <= low[i - 2]:
                count += 1
                buy_countdown_count[i] = count

                if apply_perfection and count == 8:
                    countdown_bar8_close = close[i]

                if count == length_countdown:
                    # Perfection (no altera conteo; placeholder)
                    if apply_perfection and countdown_bar8_close is not None:
                        # Ejemplo regla: Low[13] <= Close[8]
                        _ = (low[i] <= countdown_bar8_close)
                    break

    # Sell countdowns: desde cada setup_index (la barra del 9 incluida)
    for setup_index in completed_sell_setups:
        count = 0
        countdown_bar8_close = None

        for i in range(setup_index, n):
            if i in contrary_for_sell:
                break

            if i < 2:
                continue

            # Condición Sell Countdown: Close >= High[i-2]
            if close[i] >= high[i - 2]:
                count += 1
                sell_countdown_count[i] = count

                if apply_perfection and count == 8:
                    countdown_bar8_close = close[i]

                if count == length_countdown:
                    if apply_perfection and countdown_bar8_close is not None:
                        # Ejemplo regla: High[13] >= Close[8]
                        _ = (high[i] >= countdown_bar8_close)
                    break

    # ----------------------------
    # 3) Escribir columnas y retornar
    # ----------------------------
    df_res["buy_setup_count"] = buy_setup_count
    df_res["sell_setup_count"] = sell_setup_count
    df_res["buy_countdown_count"] = buy_countdown_count
    df_res["sell_countdown_count"] = sell_countdown_count

    return df_res


def get_last_signal(df: pd.DataFrame, length_setup: int = 9, length_countdown: int = 13):
    """
    Busca la última señal completada en el DataFrame con los conteos TD Sequential.

    Retorna:
    - string indicando la última señal completada (Setup 9 o Countdown 13, de compra o venta)
    - None si no hay señales completas
    """
    if "buy_setup_count" not in df.columns:
        raise ValueError("El DataFrame no contiene columnas TD Sequential. Ejecute calculate_td_sequential primero.")

    mask_signal = (
        (df["buy_setup_count"] == length_setup) |
        (df["sell_setup_count"] == length_setup) |
        (df["buy_countdown_count"] == length_countdown) |
        (df["sell_countdown_count"] == length_countdown)
    )
    if not mask_signal.any():
        return None

    last_idx = df[mask_signal].index[-1]
    signal_str = ""
    if df.at[last_idx, "buy_setup_count"] == length_setup:
        signal_str = "Setup de Compra"
    elif df.at[last_idx, "sell_setup_count"] == length_setup:
        signal_str = "Setup de Venta"
    elif df.at[last_idx, "buy_countdown_count"] == length_countdown:
        signal_str = "Countdown de Compra"
    elif df.at[last_idx, "sell_countdown_count"] == length_countdown:
        signal_str = "Countdown de Venta"
    else:
        return None

    return f"Última señal: {signal_str} completado en la barra {last_idx}"
