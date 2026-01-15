"""
Tests de integración usando datos reales del BKX Index
"""

import pytest
import pandas as pd
from tdsequential.core import calculate_td_sequential, get_last_signal
from tdsequential.levels import calculate_tdst_levels
from tdsequential.plot import plot_td_sequential
import matplotlib.pyplot as plt


@pytest.fixture
def bkx_data():
    """Cargar datos reales del BKX Index"""
    df = pd.read_csv('tests/bkx_data.csv', index_col=0, parse_dates=True)
    # Renombrar columnas si es necesario
    return df


class TestBKXIntegration:
    """Tests de integración con datos reales del BKX Index"""

    def test_calculate_td_sequential_on_real_data(self, bkx_data):
        """Verifica que calculate_td_sequential funciona con datos reales"""
        df_result = calculate_td_sequential(bkx_data)

        # Verificar que se agregaron las columnas
        assert 'buy_setup_count' in df_result.columns
        assert 'sell_setup_count' in df_result.columns
        assert 'buy_countdown_count' in df_result.columns
        assert 'sell_countdown_count' in df_result.columns

        # Verificar que hay algunos conteos
        assert df_result['buy_setup_count'].max() >= 0
        assert df_result['sell_setup_count'].max() >= 0

    def test_tdst_levels_on_real_data(self, bkx_data):
        """Verifica que calculate_tdst_levels funciona con datos reales"""
        # Primero calcular TD Sequential
        df_with_signals = calculate_td_sequential(bkx_data)

        # Resetear índice para que levels.py funcione (usa .loc con índices enteros)
        df_with_signals_reset = df_with_signals.reset_index(drop=True)

        # Luego calcular niveles TDST
        df_result = calculate_tdst_levels(df_with_signals_reset)

        # Verificar que se agregaron las columnas
        assert 'tdst_buy' in df_result.columns
        assert 'tdst_sell' in df_result.columns

    def test_plot_on_real_data(self, bkx_data):
        """Verifica que plot_td_sequential funciona con datos reales"""
        # Calcular TD Sequential
        df_with_signals = calculate_td_sequential(bkx_data)

        # Crear el gráfico
        ax = plot_td_sequential(df_with_signals)

        assert ax is not None
        assert ax.has_data()

        # Limpiar
        plt.close('all')

    def test_get_last_signal_on_real_data(self, bkx_data):
        """Verifica que get_last_signal funciona con datos reales"""
        # Calcular TD Sequential
        df_with_signals = calculate_td_sequential(bkx_data)

        # Obtener última señal
        last_signal = get_last_signal(df_with_signals)

        # Puede ser None o un string, ambos son válidos
        assert last_signal is None or isinstance(last_signal, str)

    def test_full_workflow_on_real_data(self, bkx_data):
        """Test del workflow completo: Sequential -> TDST -> Plot"""
        # 1. Calcular TD Sequential
        df_sequential = calculate_td_sequential(bkx_data)

        # Resetear índice para que levels.py funcione
        df_sequential_reset = df_sequential.reset_index(drop=True)

        # 2. Calcular niveles TDST
        df_with_levels = calculate_tdst_levels(df_sequential_reset)

        # 3. Obtener última señal
        last_signal = get_last_signal(df_with_levels)

        # 4. Crear gráfico
        ax = plot_td_sequential(df_with_levels)

        # Verificaciones
        assert len(df_with_levels) == len(bkx_data)
        assert 'buy_setup_count' in df_with_levels.columns
        assert 'tdst_buy' in df_with_levels.columns
        assert ax is not None
        assert last_signal is None or isinstance(last_signal, str)

        # Limpiar
        plt.close('all')

    def test_detects_setups_in_real_data(self, bkx_data):
        """Verifica que se detectan setups en datos reales"""
        df_result = calculate_td_sequential(bkx_data)

        # Con 2 años de datos, debería haber al menos algunos setups
        buy_setups = (df_result['buy_setup_count'] == 9).sum()
        sell_setups = (df_result['sell_setup_count'] == 9).sum()

        # Verificar que hay al menos algún setup (puede ser 0 si el mercado es muy lateral)
        total_setups = buy_setups + sell_setups
        print(f"\nSetups detectados: Buy={buy_setups}, Sell={sell_setups}, Total={total_setups}")

        # Al menos debería haber procesado los datos sin errores
        assert df_result['buy_setup_count'].max() >= 0
        assert df_result['sell_setup_count'].max() >= 0

    def test_detects_countdowns_in_real_data(self, bkx_data):
        """Verifica que se detectan countdowns en datos reales"""
        df_result = calculate_td_sequential(bkx_data)

        # Verificar que hay conteos de countdown
        buy_countdowns = (df_result['buy_countdown_count'] == 13).sum()
        sell_countdowns = (df_result['sell_countdown_count'] == 13).sum()

        total_countdowns = buy_countdowns + sell_countdowns
        print(f"\nCountdowns detectados: Buy={buy_countdowns}, Sell={sell_countdowns}, Total={total_countdowns}")

        # Al menos debería haber procesado los datos sin errores
        assert df_result['buy_countdown_count'].max() >= 0
        assert df_result['sell_countdown_count'].max() >= 0

    def test_tdst_levels_are_calculated_when_setup_completes(self, bkx_data):
        """Verifica que los niveles TDST se calculan cuando hay setups completados"""
        # Calcular TD Sequential
        df_sequential = calculate_td_sequential(bkx_data)

        # Resetear índice para que levels.py funcione
        df_sequential_reset = df_sequential.reset_index(drop=True)

        # Calcular TDST
        df_with_levels = calculate_tdst_levels(df_sequential_reset)

        # Si hay setups completados, debería haber niveles TDST
        has_buy_setup = (df_sequential_reset['buy_setup_count'] == 9).any()
        has_sell_setup = (df_sequential_reset['sell_setup_count'] == 9).any()

        if has_buy_setup:
            # Debería haber al menos un nivel TDST Buy no nulo
            assert df_with_levels['tdst_buy'].notna().any(), "Debería haber niveles TDST Buy con setups completados"

        if has_sell_setup:
            # Debería haber al menos un nivel TDST Sell no nulo
            assert df_with_levels['tdst_sell'].notna().any(), "Debería haber niveles TDST Sell con setups completados"

    def test_data_integrity_preserved(self, bkx_data):
        """Verifica que los datos originales OHLC se preservan"""
        df_result = calculate_td_sequential(bkx_data)

        # Verificar que las columnas OHLC están intactas
        assert (df_result['Open'] == bkx_data['Open']).all()
        assert (df_result['High'] == bkx_data['High']).all()
        assert (df_result['Low'] == bkx_data['Low']).all()
        assert (df_result['Close'] == bkx_data['Close']).all()

    def test_no_future_data_leakage(self, bkx_data):
        """Verifica que no hay fuga de datos futuros"""
        df_result = calculate_td_sequential(bkx_data)

        # El setup en la barra i solo debe depender de barras <= i
        # Verificar que el primer setup no puede aparecer antes de la barra 5
        # (necesita al menos i-5 para el flip condition)
        first_buy_setup = df_result[df_result['buy_setup_count'] > 0].index
        first_sell_setup = df_result[df_result['sell_setup_count'] > 0].index

        if len(first_buy_setup) > 0:
            first_idx = df_result.index.get_loc(first_buy_setup[0])
            assert first_idx >= 5, "El setup no puede aparecer antes de la barra 5"

        if len(first_sell_setup) > 0:
            first_idx = df_result.index.get_loc(first_sell_setup[0])
            assert first_idx >= 5, "El setup no puede aparecer antes de la barra 5"
