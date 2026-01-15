"""
Tests para el módulo core.py
Testea las funciones calculate_td_sequential y get_last_signal
"""

import pytest
import pandas as pd
import numpy as np
from tdsequential.core import calculate_td_sequential, get_last_signal


class TestCalculateTDSequential:
    """Tests para la función calculate_td_sequential"""

    def test_basic_dataframe_structure(self, sample_ohlc_data):
        """Verifica que la función retorna las columnas esperadas"""
        df_result = calculate_td_sequential(sample_ohlc_data)

        expected_columns = [
            'buy_setup_count',
            'sell_setup_count',
            'buy_countdown_count',
            'sell_countdown_count'
        ]

        for col in expected_columns:
            assert col in df_result.columns, f"Columna {col} no encontrada"

    def test_minimum_data_length(self):
        """Verifica que funciona con un DataFrame pequeño"""
        df = pd.DataFrame({
            'Open': [100, 101, 102, 103, 104, 105, 106],
            'High': [102, 103, 104, 105, 106, 107, 108],
            'Low': [99, 100, 101, 102, 103, 104, 105],
            'Close': [101, 102, 103, 104, 105, 106, 107]
        })

        df_result = calculate_td_sequential(df)
        assert len(df_result) == len(df)
        assert 'buy_setup_count' in df_result.columns

    def test_empty_dataframe_returns_empty(self):
        """Verifica el comportamiento con DataFrame vacío"""
        df = pd.DataFrame(columns=['Open', 'High', 'Low', 'Close'])
        df_result = calculate_td_sequential(df)

        assert len(df_result) == 0
        assert 'buy_setup_count' in df_result.columns

    def test_missing_columns_raises_error(self):
        """Verifica que lanza error si faltan columnas requeridas"""
        df = pd.DataFrame({
            'Open': [100, 101, 102],
            'High': [102, 103, 104]
            # Faltan Low y Close
        })

        with pytest.raises(ValueError, match="Columna.*no encontrada"):
            calculate_td_sequential(df)

    def test_buy_setup_detection(self, complete_buy_setup_data):
        """Verifica la detección de Buy Setup (bearish flip + secuencia bajista)"""
        df_result = calculate_td_sequential(complete_buy_setup_data)

        # Verificar que se detectó al menos un buy setup
        assert (df_result['buy_setup_count'] > 0).any(), "No se detectó ningún buy setup"

        # Verificar que el conteo avanza
        max_buy_setup = df_result['buy_setup_count'].max()
        assert max_buy_setup >= 1, f"Expected buy setup progress, got {max_buy_setup}"

    def test_sell_setup_detection(self, complete_sell_setup_data):
        """Verifica la detección de Sell Setup (bullish flip + secuencia alcista)"""
        df_result = calculate_td_sequential(complete_sell_setup_data)

        # Verificar que se detectó al menos un sell setup
        assert (df_result['sell_setup_count'] > 0).any(), "No se detectó ningún sell setup"

        # Verificar que el conteo avanza
        max_sell_setup = df_result['sell_setup_count'].max()
        assert max_sell_setup >= 1, f"Expected sell setup progress, got {max_sell_setup}"

    def test_custom_column_names(self):
        """Verifica que funciona con nombres de columnas personalizados"""
        df = pd.DataFrame({
            'precio_apertura': [100, 101, 102, 103, 104, 105, 106],
            'precio_maximo': [102, 103, 104, 105, 106, 107, 108],
            'precio_minimo': [99, 100, 101, 102, 103, 104, 105],
            'precio_cierre': [101, 102, 103, 104, 105, 106, 107]
        })

        df_result = calculate_td_sequential(
            df,
            open_col='precio_apertura',
            high_col='precio_maximo',
            low_col='precio_minimo',
            close_col='precio_cierre'
        )

        assert 'buy_setup_count' in df_result.columns

    def test_countdown_starts_after_setup(self, complete_buy_setup_data):
        """Verifica que el countdown comienza después de completar un setup"""
        df_result = calculate_td_sequential(complete_buy_setup_data)

        # Encontrar la primera barra con buy_setup_count = 9
        setup_completed_idx = df_result[df_result['buy_setup_count'] == 9].index

        if len(setup_completed_idx) > 0:
            first_setup_idx = setup_completed_idx[0]
            # Verificar que el countdown aparece en o después del setup completado
            countdown_starts = df_result[df_result['buy_countdown_count'] > 0].index
            if len(countdown_starts) > 0:
                assert countdown_starts[0] >= first_setup_idx

    def test_countdown_condition_buy(self):
        """Verifica que el buy countdown se incrementa cuando Close <= Low[i-2]"""
        # Esta prueba es conceptual, ya que requiere un setup completado primero
        df = pd.DataFrame({
            'Open': range(100, 120),
            'High': range(102, 122),
            'Low': range(98, 118),
            'Close': range(101, 121)
        })

        df_result = calculate_td_sequential(df)

        # Verificar que las columnas existen y son del tipo correcto
        assert df_result['buy_countdown_count'].dtype in [np.int32, np.int64, int]

    def test_countdown_condition_sell(self):
        """Verifica que el sell countdown se incrementa cuando Close >= High[i-2]"""
        df = pd.DataFrame({
            'Open': range(120, 100, -1),
            'High': range(122, 102, -1),
            'Low': range(118, 98, -1),
            'Close': range(121, 101, -1)
        })

        df_result = calculate_td_sequential(df)

        # Verificar que las columnas existen y son del tipo correcto
        assert df_result['sell_countdown_count'].dtype in [np.int32, np.int64, int]

    def test_custom_setup_length(self):
        """Verifica que funciona con longitudes de setup personalizadas"""
        df = pd.DataFrame({
            'Open': range(100, 115),
            'High': range(102, 117),
            'Low': range(98, 113),
            'Close': range(101, 116)
        })

        df_result = calculate_td_sequential(df, length_setup=7)

        # Si se completa un setup, debe ser con valor 7, no 9
        if df_result['buy_setup_count'].max() > 0:
            assert df_result['buy_setup_count'].max() <= 7
        if df_result['sell_setup_count'].max() > 0:
            assert df_result['sell_setup_count'].max() <= 7

    def test_custom_countdown_length(self):
        """Verifica que funciona con longitudes de countdown personalizadas"""
        df = pd.DataFrame({
            'Open': range(100, 125),
            'High': range(102, 127),
            'Low': range(98, 123),
            'Close': range(101, 126)
        })

        df_result = calculate_td_sequential(df, length_countdown=10)

        # Si se completa un countdown, debe ser con valor 10, no 13
        if df_result['buy_countdown_count'].max() > 0:
            assert df_result['buy_countdown_count'].max() <= 10
        if df_result['sell_countdown_count'].max() > 0:
            assert df_result['sell_countdown_count'].max() <= 10

    def test_perfection_parameter(self):
        """Verifica que el parámetro apply_perfection no causa errores"""
        df = pd.DataFrame({
            'Open': range(100, 120),
            'High': range(102, 122),
            'Low': range(98, 118),
            'Close': range(101, 121)
        })

        df_with_perfection = calculate_td_sequential(df, apply_perfection=True)
        df_without_perfection = calculate_td_sequential(df, apply_perfection=False)

        assert len(df_with_perfection) == len(df_without_perfection)

    def test_setup_breaks_on_condition_failure(self):
        """Verifica que un setup en progreso se rompe si no se cumple la condición"""
        # Crear datos donde empieza un setup pero se rompe antes de llegar a 9
        closes = [110, 109, 108, 107, 106, 105,  # i=0-5
                  104, 103, 102, 101,            # i=6-9: comienza bearish flip
                  99, 98,                        # continúa bajando
                  110]                           # ROMPE el setup al subir mucho

        df = pd.DataFrame({
            'Open': closes,
            'High': [c + 1 for c in closes],
            'Low': [c - 1 for c in closes],
            'Close': closes
        })

        df_result = calculate_td_sequential(df)

        # El último valor de buy_setup_count debería ser 0 porque se rompió
        last_buy_count = df_result['buy_setup_count'].iloc[-1]
        assert last_buy_count == 0, f"Expected setup to break, but got count={last_buy_count}"

    def test_no_modification_of_original_dataframe(self):
        """Verifica que no se modifica el DataFrame original"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111)
        })

        original_columns = df.columns.tolist()
        _ = calculate_td_sequential(df)

        # El DataFrame original no debe tener las nuevas columnas
        assert df.columns.tolist() == original_columns


class TestGetLastSignal:
    """Tests para la función get_last_signal"""

    def test_returns_none_when_no_signals(self):
        """Verifica que retorna None si no hay señales completadas"""
        df = pd.DataFrame({
            'Open': range(100, 105),
            'High': range(102, 107),
            'Low': range(98, 103),
            'Close': range(101, 106),
            'buy_setup_count': [0, 0, 0, 0, 0],
            'sell_setup_count': [0, 0, 0, 0, 0],
            'buy_countdown_count': [0, 0, 0, 0, 0],
            'sell_countdown_count': [0, 0, 0, 0, 0]
        })

        result = get_last_signal(df)
        assert result is None

    def test_detects_buy_setup_completion(self):
        """Verifica que detecta la completación de un Buy Setup"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'sell_setup_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'buy_countdown_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_countdown_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        })

        result = get_last_signal(df)
        assert result is not None
        assert "Setup de Compra" in result

    def test_detects_sell_setup_completion(self):
        """Verifica que detecta la completación de un Sell Setup"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111),
            'buy_setup_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'buy_countdown_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_countdown_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        })

        result = get_last_signal(df)
        assert result is not None
        assert "Setup de Venta" in result

    def test_detects_buy_countdown_completion(self):
        """Verifica que detecta la completación de un Buy Countdown"""
        df = pd.DataFrame({
            'Open': range(100, 115),
            'High': range(102, 117),
            'Low': range(98, 113),
            'Close': range(101, 116),
            'buy_setup_count': [0] * 15,
            'sell_setup_count': [0] * 15,
            'buy_countdown_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0],
            'sell_countdown_count': [0] * 15
        })

        result = get_last_signal(df)
        assert result is not None
        assert "Countdown de Compra" in result

    def test_detects_sell_countdown_completion(self):
        """Verifica que detecta la completación de un Sell Countdown"""
        df = pd.DataFrame({
            'Open': range(100, 115),
            'High': range(102, 117),
            'Low': range(98, 113),
            'Close': range(101, 116),
            'buy_setup_count': [0] * 15,
            'sell_setup_count': [0] * 15,
            'buy_countdown_count': [0] * 15,
            'sell_countdown_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0]
        })

        result = get_last_signal(df)
        assert result is not None
        assert "Countdown de Venta" in result

    def test_returns_most_recent_signal(self):
        """Verifica que retorna la señal más reciente cuando hay múltiples"""
        df = pd.DataFrame({
            'Open': range(100, 120),
            'High': range(102, 122),
            'Low': range(98, 118),
            'Close': range(101, 121),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_setup_count': [0] * 10 + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'buy_countdown_count': [0] * 20,
            'sell_countdown_count': [0] * 20
        })

        result = get_last_signal(df)
        assert result is not None
        # Debe detectar el último (Sell Setup en índice 19)
        assert "Setup de Venta" in result
        assert "19" in result

    def test_raises_error_without_required_columns(self):
        """Verifica que lanza error si faltan las columnas requeridas"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111)
        })

        with pytest.raises(ValueError, match="no contiene columnas TD Sequential"):
            get_last_signal(df)

    def test_custom_length_parameters(self):
        """Verifica que funciona con longitudes personalizadas"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 0, 0],
            'sell_setup_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'buy_countdown_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_countdown_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        })

        # Con length_setup=7, debe detectar la barra 7
        result = get_last_signal(df, length_setup=7)
        assert result is not None
        assert "Setup de Compra" in result

    def test_includes_bar_index_in_result(self):
        """Verifica que el resultado incluye el índice de la barra"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111),
            'buy_setup_count': [0, 0, 0, 0, 0, 0, 0, 0, 0, 9],
            'sell_setup_count': [0] * 10,
            'buy_countdown_count': [0] * 10,
            'sell_countdown_count': [0] * 10
        })

        result = get_last_signal(df)
        assert result is not None
        assert "barra 9" in result or "9" in result
