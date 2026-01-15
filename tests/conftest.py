"""
Fixtures compartidos para los tests de tdsequential
"""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture
def sample_ohlc_data():
    """
    DataFrame básico con datos OHLC para testing
    """
    n = 20
    return pd.DataFrame({
        'Open': range(100, 100 + n),
        'High': range(102, 102 + n),
        'Low': range(98, 98 + n),
        'Close': range(101, 101 + n)
    })


@pytest.fixture
def sample_ohlc_with_setup():
    """
    DataFrame con datos OHLC y columnas de setup para testing de levels
    """
    n = 20
    return pd.DataFrame({
        'Open': range(100, 100 + n),
        'High': [110] * n,
        'Low': [100] * n,
        'Close': range(101, 101 + n),
        'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 10,
        'sell_setup_count': [0] * n
    })


@pytest.fixture
def sample_ohlc_with_signals():
    """
    DataFrame completo con datos OHLC y todas las columnas de TD Sequential
    Incluye algunas señales completadas para testing de plots
    """
    n = 25
    return pd.DataFrame({
        'Open': range(100, 100 + n),
        'High': range(102, 102 + n),
        'Low': range(98, 98 + n),
        'Close': range(101, 101 + n),
        'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 15,
        'sell_setup_count': [0] * 10 + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 5,
        'buy_countdown_count': [0] * 11 + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0],
        'sell_countdown_count': [0] * n
    })


@pytest.fixture
def complete_buy_setup_data():
    """
    DataFrame diseñado para completar un Buy Setup de forma garantizada
    Bearish flip requiere: Close[i] < Close[i-4] AND Close[i-1] > Close[i-5]
    """
    closes = [120, 119, 118, 117, 116, 115, 120, 114, 113, 112, 111, 110, 109, 108, 107, 106, 105]

    return pd.DataFrame({
        'Open': closes,
        'High': [c + 1 for c in closes],
        'Low': [c - 1 for c in closes],
        'Close': closes
    })


@pytest.fixture
def complete_sell_setup_data():
    """
    DataFrame diseñado para completar un Sell Setup de forma garantizada
    Bullish flip requiere: Close[i] > Close[i-4] AND Close[i-1] < Close[i-5]
    """
    closes = [100, 101, 102, 103, 104, 105, 100, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115]

    return pd.DataFrame({
        'Open': closes,
        'High': [c + 1 for c in closes],
        'Low': [c - 1 for c in closes],
        'Close': closes
    })


@pytest.fixture
def alternating_price_data():
    """
    DataFrame con precios que alternan (no debería generar setups largos)
    """
    closes = []
    base = 100
    for i in range(30):
        if i % 2 == 0:
            closes.append(base)
        else:
            closes.append(base + 5)

    return pd.DataFrame({
        'Open': closes,
        'High': [c + 1 for c in closes],
        'Low': [c - 1 for c in closes],
        'Close': closes
    })


@pytest.fixture
def real_world_like_data():
    """
    DataFrame con datos más realistas (precios con algo de volatilidad)
    """
    np.random.seed(42)  # Para reproducibilidad

    n = 100
    closes = [100]

    for i in range(1, n):
        # Movimiento aleatorio con tendencia ligera
        change = np.random.normal(0, 1)
        closes.append(closes[-1] + change)

    closes = np.array(closes)

    return pd.DataFrame({
        'Open': closes + np.random.normal(0, 0.5, n),
        'High': closes + np.abs(np.random.normal(1, 0.5, n)),
        'Low': closes - np.abs(np.random.normal(1, 0.5, n)),
        'Close': closes
    })


@pytest.fixture
def tdst_break_scenario():
    """
    DataFrame diseñado para probar la ruptura de niveles TDST
    """
    return pd.DataFrame({
        'Open': range(100, 120),
        'High': [110] * 20,
        'Low': [105, 105, 105, 105, 105, 105, 105, 105, 105, 108,  # setup completo en i=9
                107, 107, 107, 100,  # i=13: Low rompe el TDST Buy (110)
                107, 107, 107, 107, 107, 107],
        'Close': range(101, 121),
        'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 10,
        'sell_setup_count': [0] * 20
    })


@pytest.fixture
def multiple_signals_data():
    """
    DataFrame con múltiples tipos de señales para testing completo
    """
    n = 40
    return pd.DataFrame({
        'Open': range(100, 100 + n),
        'High': range(102, 102 + n),
        'Low': range(98, 98 + n),
        'Close': range(101, 101 + n),
        'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 15 + [1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 6,
        'sell_setup_count': [0] * 10 + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 20,
        'buy_countdown_count': [0] * 11 + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] + [0] * 16,
        'sell_countdown_count': [0] * 22 + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] + [0] * 5
    })


@pytest.fixture
def empty_signals_data():
    """
    DataFrame con columnas de señales pero sin ninguna señal completada
    """
    n = 15
    return pd.DataFrame({
        'Open': range(100, 100 + n),
        'High': range(102, 102 + n),
        'Low': range(98, 98 + n),
        'Close': range(101, 101 + n),
        'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 0, 0, 0, 0, 0, 0, 0],  # No llega a 9
        'sell_setup_count': [0] * n,
        'buy_countdown_count': [0] * n,
        'sell_countdown_count': [0] * n
    })


@pytest.fixture
def datetime_index_data():
    """
    DataFrame con índice de tipo datetime para testing realista
    """
    dates = pd.date_range(start='2023-01-01', periods=30, freq='D')

    n = 30
    return pd.DataFrame({
        'Open': range(100, 100 + n),
        'High': range(102, 102 + n),
        'Low': range(98, 98 + n),
        'Close': range(101, 101 + n),
        'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 20,
        'sell_setup_count': [0] * n,
        'buy_countdown_count': [0] * n,
        'sell_countdown_count': [0] * n
    }, index=dates)


@pytest.fixture
def custom_column_names_data():
    """
    DataFrame con nombres de columnas personalizados
    """
    n = 20
    return pd.DataFrame({
        'precio_apertura': range(100, 100 + n),
        'precio_maximo': range(102, 102 + n),
        'precio_minimo': range(98, 98 + n),
        'precio_cierre': range(101, 101 + n)
    })
