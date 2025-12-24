"""
Módulo de visualización opcional para TD Sequential.
Incluye función para graficar el precio con las señales del indicador marcadas.
"""

import matplotlib.pyplot as plt

def plot_td_sequential(df, open_col='Open', high_col='High', low_col='Low', close_col='Close', ax=None):
    """
    Genera un gráfico con el precio de cierre y marca las señales del TD Sequential (Setups y Countdowns completados).
    
    Parámetros:
    - df: DataFrame que contiene las columnas de conteo generadas por `calculate_td_sequential`.
    - open_col, high_col, low_col, close_col: nombres de columnas OHLC (deben coincidir con los usados en `calculate_td_sequential`).
    - ax: objeto matplotlib Axes existente donde dibujar (opcional). Si no se proporciona, se creará uno nuevo.
    
    Retorna:
    - El objeto Axes con el gráfico dibujado. (Use `plt.show()` para mostrarlo en pantalla si está en un script o terminal).
    """
    # Verificar que el DataFrame tiene las columnas necesarias de conteo
    required_cols = ['buy_setup_count', 'sell_setup_count', 'buy_countdown_count', 'sell_countdown_count']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError("El DataFrame no contiene las columnas de conteo TD Sequential. Asegúrese de ejecutar calculate_td_sequential primero.")
    
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    # Graficar la línea de precio de cierre
    ax.plot(df.index, df[close_col], label='Precio de Cierre', color='black')
    # Calcular un desplazamiento vertical pequeño para las flechas (2% del rango de precios)
    price_range = df[high_col].max() - df[low_col].min()
    offset = 0.02 * price_range
    
    # Identificar índices de señales completadas
    buy_setup_idx = df.index[df['buy_setup_count'] == 9]
    sell_setup_idx = df.index[df['sell_setup_count'] == 9]
    buy_countdown_idx = df.index[df['buy_countdown_count'] == 13]
    sell_countdown_idx = df.index[df['sell_countdown_count'] == 13]
    
    # Marcar Setup de Compra (triángulo verde hacia arriba debajo del precio)
    if len(buy_setup_idx) > 0:
        ax.scatter(buy_setup_idx, df.loc[buy_setup_idx, low_col] - offset, marker='^', color='green', label='Buy Setup (9)')
    # Marcar Setup de Venta (triángulo rojo hacia abajo encima del precio)
    if len(sell_setup_idx) > 0:
        ax.scatter(sell_setup_idx, df.loc[sell_setup_idx, high_col] + offset, marker='v', color='red', label='Sell Setup (9)')
    # Marcar Countdown de Compra (triángulo azul hacia arriba debajo del precio)
    if len(buy_countdown_idx) > 0:
        ax.scatter(buy_countdown_idx, df.loc[buy_countdown_idx, low_col] - offset, marker='^', color='blue', label='Buy Countdown (13)')
    # Marcar Countdown de Venta (triángulo azul hacia abajo encima del precio)
    if len(sell_countdown_idx) > 0:
        ax.scatter(sell_countdown_idx, df.loc[sell_countdown_idx, high_col] + offset, marker='v', color='blue', label='Sell Countdown (13)')
    
    ax.set_title('Señales TD Sequential')
    ax.legend()
    return ax
