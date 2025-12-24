"""
Módulo principal con la lógica de cálculo del indicador TD Sequential y TD Countdown.
Incluye funciones para calcular los conteos y detectar la última señal completada.
"""

import pandas as pd
import numpy as np

def calculate_td_sequential(df, open_col='Open', high_col='High', low_col='Low', close_col='Close',
                             length_setup=9, length_countdown=13, apply_perfection=True):
    """
    Calcula los conteos del indicador TD Sequential (Setup y Countdown) para un DataFrame de precios OHLC.
    
    Parámetros:
    - df: pandas DataFrame con columnas de precios (por lo menos Close, High, Low; Open es opcional para esta lógica).
    - open_col, high_col, low_col, close_col: nombres de las columnas de apertura, máximo, mínimo y cierre (por defecto 'Open', 'High', 'Low', 'Close').
    - length_setup: número de barras consecutivas para completar un Setup (por defecto 9, según reglas originales).
    - length_countdown: número de barras (no necesariamente consecutivas) para completar un Countdown (por defecto 13).
    - apply_perfection: bool (por defecto True). Si es True, aplica las reglas de "perfeccionamiento" (perfection) para setups y countdowns 
      según Tom DeMark, verificando condiciones adicionales en la barra final. Estas condiciones no alteran el conteo numérico, 
      pero pueden usarse para identificar señales más fuertes.
    
    Retorna:
    - DataFrame nuevo con las columnas adicionales:
      'buy_setup_count', 'sell_setup_count', 'buy_countdown_count', 'sell_countdown_count'.
      Cada columna contiene el conteo actual para el patrón correspondiente o 0 si no está activo en esa barra.
    """
    # Copiar DataFrame para no modificar el original
    df_res = df.copy()
    # Asegurarse de que existen las columnas necesarias
    for col in [close_col, high_col, low_col]:
        if col not in df_res.columns:
            raise ValueError(f"Columna '{col}' no encontrada en DataFrame")
    
    close = df_res[close_col].values
    high = df_res[high_col].values
    low = df_res[low_col].values
    n = len(df_res)
    # Inicializar listas de conteo con ceros
    buy_setup_count = [0] * n
    sell_setup_count = [0] * n
    buy_countdown_count = [0] * n
    sell_countdown_count = [0] * n
    
    # Variables de estado
    active_setup = None       # 'buy' o 'sell' si estamos en medio de un Setup activo
    setup_count = 0           # conteo actual dentro del Setup activo
    active_countdown = None   # 'buy' o 'sell' si estamos en un Countdown activo
    countdown_count = 0       # conteo actual dentro del Countdown activo
    countdown_bar8_close = None  # guarda el valor de cierre de la barra 8 del Countdown para chequeo de perfeccionamiento
    initial_started = False   # indica si ya se inició algún setup (para manejar la condición inicial)
    last_env = None           # último entorno de tendencia reconocido: 'bullish' (alcista) o 'bearish' (bajista)
    
    # Recorrer las barras del DataFrame secuencialmente
    for i in range(n):
        # No se puede evaluar un Setup hasta que haya al menos 4 barras anteriores (para comparar cierres)
        if i < 4:
            continue
        
        # 1. Detección de Price Flip (cambio de tendencia) si hay suficientes datos históricos (requiere i-5)
        if i >= 5:
            # Flip alcista (bullish flip): la barra previa era bajista y la actual es alcista en términos de 4 barras atrás
            if close[i-1] < close[i-5] and close[i] > close[i-4]:
                # Si hay un Countdown de compra activo, cancelarlo (nuevo Setup opuesto comienza)
                if active_countdown == 'buy':
                    active_countdown = None
                    countdown_count = 0
                    countdown_bar8_close = None
                # Si hay un Setup de compra activo (incompleto) se descarta
                if active_setup == 'buy':
                    active_setup = None
                    setup_count = 0
                # Iniciar un nuevo Setup de venta
                active_setup = 'sell'
                setup_count = 1
                sell_setup_count[i] = setup_count
                initial_started = True
                last_env = 'bullish'  # entorno actual alcista
                continue
            # Flip bajista (bearish flip): la barra previa era alcista y la actual es bajista
            if close[i-1] > close[i-5] and close[i] < close[i-4]:
                if active_countdown == 'sell':
                    active_countdown = None
                    countdown_count = 0
                    countdown_bar8_close = None
                if active_setup == 'sell':
                    active_setup = None
                    setup_count = 0
                active_setup = 'buy'
                setup_count = 1
                buy_setup_count[i] = setup_count
                initial_started = True
                last_env = 'bearish'  # entorno actual bajista
                continue
        
        # 2. Lógica de Countdown activo (si ya se completó un Setup previo y estamos contando hacia 13)
        if active_countdown is not None:
            if active_countdown == 'buy':
                # Countdown de compra: se incrementa si el cierre actual <= el mínimo de hace 2 barras
                if i >= 2 and close[i] <= low[i-2]:
                    countdown_count += 1
                    buy_countdown_count[i] = countdown_count
                    if countdown_count == 8:
                        # Guardar el cierre de la barra 8 para verificar perfeccionamiento al completar
                        countdown_bar8_close = close[i]
                    if countdown_count == length_countdown:
                        # Countdown de compra completado (13)
                        if apply_perfection and countdown_bar8_close is not None:
                            # Regla de perfeccionamiento para Countdown de compra:
                            # Verificar si el mínimo de la barra 13 <= cierre de la barra 8 del countdown
                            if low[i] <= countdown_bar8_close:
                                # Señal perfeccionada (por ejemplo, podría marcarse con un indicador adicional)
                                pass
                        # Resetear el estado tras completar el Countdown
                        active_countdown = None
                        countdown_count = 0
                        countdown_bar8_close = None
                        # *No* iniciamos automáticamente un nuevo Setup aquí; esperaremos un nuevo price flip
                else:
                    # Si la condición no se cumple, no se incrementa el countdown en esta barra (puede haber días "en pausa")
                    buy_countdown_count[i] = 0
            elif active_countdown == 'sell':
                # Countdown de venta: se incrementa si el cierre actual >= el máximo de hace 2 barras
                if i >= 2 and close[i] >= high[i-2]:
                    countdown_count += 1
                    sell_countdown_count[i] = countdown_count
                    if countdown_count == 8:
                        countdown_bar8_close = close[i]
                    if countdown_count == length_countdown:
                        if apply_perfection and countdown_bar8_close is not None:
                            # Regla de perfeccionamiento para Countdown de venta:
                            # Verificar si el máximo de la barra 13 >= cierre de la barra 8 del countdown
                            if high[i] >= countdown_bar8_close:
                                # Señal perfeccionada
                                pass
                        active_countdown = None
                        countdown_count = 0
                        countdown_bar8_close = None
                else:
                    sell_countdown_count[i] = 0
            # Continuar a la siguiente barra
            continue
        
        # 3. Lógica de Setup activo o inicio de uno nuevo
        if active_setup is None:
            # No hay un Setup en progreso
            if not initial_started:
                # Si aún no se inició ningún Setup en todo el historial, permitimos iniciar uno sin flip previo
                if close[i] < close[i-4]:
                    active_setup = 'buy'
                    setup_count = 1
                    buy_setup_count[i] = setup_count
                    initial_started = True
                    last_env = 'bearish'
                    continue
                elif close[i] > close[i-4]:
                    active_setup = 'sell'
                    setup_count = 1
                    sell_setup_count[i] = setup_count
                    initial_started = True
                    last_env = 'bullish'
                    continue
            else:
                # Ya hubo algún Setup antes; utilizamos el entorno previo (last_env) para detectar flips sin doble condición
                if last_env == 'bearish' and close[i] > close[i-4]:
                    # El entorno anterior era bajista y ahora la condición es alcista -> nuevo Setup de venta
                    active_setup = 'sell'
                    setup_count = 1
                    sell_setup_count[i] = setup_count
                    last_env = 'bullish'
                    continue
                elif last_env == 'bullish' and close[i] < close[i-4]:
                    # El entorno anterior era alcista y ahora la condición es bajista -> nuevo Setup de compra
                    active_setup = 'buy'
                    setup_count = 1
                    buy_setup_count[i] = setup_count
                    last_env = 'bearish'
                    continue
            # Si no se cumplen condiciones para iniciar un Setup en esta barra, continuar a la siguiente
            continue
        
        # 4. Continuación de un Setup activo
        if active_setup == 'buy':
            # Setup de compra en progreso: requerimos cierre < cierre de hace 4 barras
            if close[i] < close[i-4]:
                setup_count += 1
                buy_setup_count[i] = setup_count
                if setup_count == length_setup:
                    # Se completó un Buy Setup (9)
                    if apply_perfection:
                        # Regla de perfeccionamiento para Setup de compra:
                        # El mínimo de la barra 8 o 9 debe ser menor que los mínimos de las barras 6 y 7
                        cond1 = (i >= 3 and low[i] < low[i-2] and low[i] < low[i-3])
                        cond2 = (i >= 3 and low[i-1] < low[i-2] and low[i-1] < low[i-3])
                        if cond1 or cond2:
                            # Señal de Setup de compra perfeccionada
                            pass
                    # Termina el Setup de compra
                    active_setup = None
                    setup_count = 0
                    # Iniciar fase de Countdown de compra
                    active_countdown = 'buy'
                    countdown_count = 0
                    countdown_bar8_close = None
                    # El entorno de tendencia permanece bajista hasta que ocurra un flip alcista real
            else:
                # La secuencia de Setup se rompe (no se cumplen 9 consecutivas)
                active_setup = None
                setup_count = 0
                # Marcar con 0 en esta barra para indicar que no continuó el conteo
                buy_setup_count[i] = 0
                # El entorno permanece bajista (last_env sigue siendo 'bearish', ya que no hubo flip opuesto)
        
        elif active_setup == 'sell':
            # Setup de venta en progreso: requerimos cierre > cierre de hace 4 barras
            if close[i] > close[i-4]:
                setup_count += 1
                sell_setup_count[i] = setup_count
                if setup_count == length_setup:
                    # Se completó un Sell Setup (9)
                    if apply_perfection:
                        # Regla de perfeccionamiento para Setup de venta:
                        # El máximo de la barra 8 o 9 debe ser mayor que los máximos de las barras 6 y 7
                        cond1 = (i >= 3 and high[i] > high[i-2] and high[i] > high[i-3])
                        cond2 = (i >= 3 and high[i-1] > high[i-2] and high[i-1] > high[i-3])
                        if cond1 or cond2:
                            # Señal de Setup de venta perfeccionada
                            pass
                    active_setup = None
                    setup_count = 0
                    # Iniciar fase de Countdown de venta
                    active_countdown = 'sell'
                    countdown_count = 0
                    countdown_bar8_close = None
                    # El entorno permanece alcista (last_env = 'bullish')
            else:
                # Secuencia de Setup rota
                active_setup = None
                setup_count = 0
                sell_setup_count[i] = 0
                # El entorno permanece alcista (no hubo flip contrario aún)
    
    # Añadir las columnas de conteo al DataFrame resultado
    df_res['buy_setup_count'] = buy_setup_count
    df_res['sell_setup_count'] = sell_setup_count
    df_res['buy_countdown_count'] = buy_countdown_count
    df_res['sell_countdown_count'] = sell_countdown_count
    return df_res

def get_last_signal(df, length_setup=9, length_countdown=13):
    """
    Busca la última señal completada en el DataFrame con los conteos TD Sequential.
    
    Parámetros:
    - df: pandas DataFrame que contiene las columnas de conteo generadas por `calculate_td_sequential`.
    - length_setup: longitud del Setup usada (por defecto 9).
    - length_countdown: longitud del Countdown usada (por defecto 13).
    
    Retorna:
    - Un string en español indicando la última señal completada (Setup 9 o Countdown 13, de compra o venta),
      por ejemplo: "Última señal: Setup de Compra completado en la barra X".
    - Si no hay ninguna señal completa (no hubo ningún 9 ni 13 en los datos), retorna None.
    """
    if 'buy_setup_count' not in df.columns:
        raise ValueError("El DataFrame no contiene columnas TD Sequential. Ejecute calculate_td_sequential primero.")
    # Identificar filas donde se completó un Setup (9) o Countdown (13)
    mask_signal = (
        (df['buy_setup_count'] == length_setup) | 
        (df['sell_setup_count'] == length_setup) | 
        (df['buy_countdown_count'] == length_countdown) | 
        (df['sell_countdown_count'] == length_countdown)
    )
    if not mask_signal.any():
        return None
    last_idx = df[mask_signal].index[-1]  # última posición donde hay una señal
    # Determinar el tipo de señal en esa posición
    signal_str = ""
    if df.at[last_idx, 'buy_setup_count'] == length_setup:
        signal_str = "Setup de Compra"
    elif df.at[last_idx, 'sell_setup_count'] == length_setup:
        signal_str = "Setup de Venta"
    elif df.at[last_idx, 'buy_countdown_count'] == length_countdown:
        signal_str = "Countdown de Compra"
    elif df.at[last_idx, 'sell_countdown_count'] == length_countdown:
        signal_str = "Countdown de Venta"
    else:
        return None
    return f"Última señal: {signal_str} completado en la barra {last_idx}"
