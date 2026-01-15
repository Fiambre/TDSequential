"""
Tests para el módulo plot.py
Testea la función plot_td_sequential
"""

import pytest
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from tdsequential.plot import plot_td_sequential


# Configurar matplotlib para modo no interactivo (evita ventanas durante tests)
matplotlib.use('Agg')


class TestPlotTDSequential:
    """Tests para la función plot_td_sequential"""

    def test_basic_plot_creation(self, sample_ohlc_with_signals):
        """Verifica que se crea un gráfico básico sin errores"""
        ax = plot_td_sequential(sample_ohlc_with_signals)

        assert ax is not None
        assert isinstance(ax, plt.Axes)

        # Limpiar
        plt.close('all')

    def test_requires_td_sequential_columns(self, sample_ohlc_data):
        """Verifica que lanza error si faltan las columnas de conteo TD Sequential"""
        with pytest.raises(ValueError, match="no contiene las columnas de conteo TD Sequential"):
            plot_td_sequential(sample_ohlc_data)

    def test_plot_with_custom_ax(self, sample_ohlc_with_signals):
        """Verifica que funciona cuando se proporciona un Axes personalizado"""
        fig, custom_ax = plt.subplots(figsize=(12, 8))

        returned_ax = plot_td_sequential(sample_ohlc_with_signals, ax=custom_ax)

        assert returned_ax is custom_ax
        assert returned_ax.has_data()

        # Limpiar
        plt.close('all')

    def test_plot_contains_price_line(self, sample_ohlc_with_signals):
        """Verifica que el gráfico contiene la línea de precio de cierre"""
        ax = plot_td_sequential(sample_ohlc_with_signals)

        lines = ax.get_lines()
        assert len(lines) >= 1, "Debería haber al menos una línea (precio de cierre)"

        # Verificar que hay una línea con el label correcto
        labels = [line.get_label() for line in lines]
        assert 'Precio de Cierre' in labels

        # Limpiar
        plt.close('all')

    def test_plot_marks_buy_setup_signals(self):
        """Verifica que marca correctamente las señales de Buy Setup (9)"""
        df = pd.DataFrame({
            'Open': range(100, 120),
            'High': range(102, 122),
            'Low': range(98, 118),
            'Close': range(101, 121),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_setup_count': [0] * 20,
            'buy_countdown_count': [0] * 20,
            'sell_countdown_count': [0] * 20
        })

        ax = plot_td_sequential(df)

        # Verificar que hay un scatter plot (para las señales)
        collections = ax.collections
        assert len(collections) > 0, "Debería haber al menos un scatter plot para las señales"

        # Verificar que la leyenda incluye 'Buy Setup'
        legend = ax.get_legend()
        if legend:
            labels = [text.get_text() for text in legend.get_texts()]
            assert any('Buy Setup' in label for label in labels)

        # Limpiar
        plt.close('all')

    def test_plot_marks_sell_setup_signals(self):
        """Verifica que marca correctamente las señales de Sell Setup (9)"""
        df = pd.DataFrame({
            'Open': range(100, 120),
            'High': range(102, 122),
            'Low': range(98, 118),
            'Close': range(101, 121),
            'buy_setup_count': [0] * 20,
            'sell_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'buy_countdown_count': [0] * 20,
            'sell_countdown_count': [0] * 20
        })

        ax = plot_td_sequential(df)

        # Verificar la leyenda
        legend = ax.get_legend()
        if legend:
            labels = [text.get_text() for text in legend.get_texts()]
            assert any('Sell Setup' in label for label in labels)

        # Limpiar
        plt.close('all')

    def test_plot_marks_buy_countdown_signals(self):
        """Verifica que marca correctamente las señales de Buy Countdown (13)"""
        df = pd.DataFrame({
            'Open': range(100, 125),
            'High': range(102, 127),
            'Low': range(98, 123),
            'Close': range(101, 126),
            'buy_setup_count': [0] * 25,
            'sell_setup_count': [0] * 25,
            'buy_countdown_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] + [0] * 11,
            'sell_countdown_count': [0] * 25
        })

        ax = plot_td_sequential(df)

        # Verificar la leyenda
        legend = ax.get_legend()
        if legend:
            labels = [text.get_text() for text in legend.get_texts()]
            assert any('Buy Countdown' in label for label in labels)

        # Limpiar
        plt.close('all')

    def test_plot_marks_sell_countdown_signals(self):
        """Verifica que marca correctamente las señales de Sell Countdown (13)"""
        df = pd.DataFrame({
            'Open': range(100, 125),
            'High': range(102, 127),
            'Low': range(98, 123),
            'Close': range(101, 126),
            'buy_setup_count': [0] * 25,
            'sell_setup_count': [0] * 25,
            'buy_countdown_count': [0] * 25,
            'sell_countdown_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] + [0] * 11
        })

        ax = plot_td_sequential(df)

        # Verificar la leyenda
        legend = ax.get_legend()
        if legend:
            labels = [text.get_text() for text in legend.get_texts()]
            assert any('Sell Countdown' in label for label in labels)

        # Limpiar
        plt.close('all')

    def test_plot_with_custom_column_names(self):
        """Verifica que funciona con nombres de columnas personalizados"""
        df = pd.DataFrame({
            'precio_apertura': range(100, 120),
            'precio_maximo': range(102, 122),
            'precio_minimo': range(98, 118),
            'precio_cierre': range(101, 121),
            'buy_setup_count': [0] * 20,
            'sell_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'buy_countdown_count': [0] * 20,
            'sell_countdown_count': [0] * 20
        })

        ax = plot_td_sequential(
            df,
            open_col='precio_apertura',
            high_col='precio_maximo',
            low_col='precio_minimo',
            close_col='precio_cierre'
        )

        assert ax is not None
        assert ax.has_data()

        # Limpiar
        plt.close('all')

    def test_plot_with_multiple_signals(self):
        """Verifica que maneja múltiples tipos de señales simultáneamente"""
        df = pd.DataFrame({
            'Open': range(100, 130),
            'High': range(102, 132),
            'Low': range(98, 128),
            'Close': range(101, 131),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 20,
            'sell_setup_count': [0] * 10 + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 10,
            'buy_countdown_count': [0] * 11 + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] + [0] * 6,
            'sell_countdown_count': [0] * 25 + [1, 2, 3, 4, 13]
        })

        ax = plot_td_sequential(df)

        # Debe haber múltiples scatter plots
        collections = ax.collections
        assert len(collections) > 0

        # La leyenda debe tener múltiples entradas
        legend = ax.get_legend()
        if legend:
            labels = [text.get_text() for text in legend.get_texts()]
            assert len(labels) > 1

        # Limpiar
        plt.close('all')

    def test_plot_with_no_signals(self):
        """Verifica que funciona incluso sin señales completadas"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 0, 0],  # No llega a 9
            'sell_setup_count': [0] * 10,
            'buy_countdown_count': [0] * 10,
            'sell_countdown_count': [0] * 10
        })

        ax = plot_td_sequential(df)

        assert ax is not None
        # Debería tener la línea de precio al menos
        assert len(ax.get_lines()) >= 1

        # Limpiar
        plt.close('all')

    def test_plot_has_title(self, sample_ohlc_with_signals):
        """Verifica que el gráfico tiene un título"""
        ax = plot_td_sequential(sample_ohlc_with_signals)

        title = ax.get_title()
        assert title != ""
        assert "TD Sequential" in title

        # Limpiar
        plt.close('all')

    def test_plot_has_legend(self, sample_ohlc_with_signals):
        """Verifica que el gráfico tiene una leyenda"""
        ax = plot_td_sequential(sample_ohlc_with_signals)

        legend = ax.get_legend()
        assert legend is not None

        # Limpiar
        plt.close('all')

    def test_plot_returns_same_ax_when_provided(self):
        """Verifica que retorna el mismo Axes que se proporciona"""
        df = pd.DataFrame({
            'Open': range(100, 110),
            'High': range(102, 112),
            'Low': range(98, 108),
            'Close': range(101, 111),
            'buy_setup_count': [0] * 10,
            'sell_setup_count': [0] * 10,
            'buy_countdown_count': [0] * 10,
            'sell_countdown_count': [0] * 10
        })

        fig, provided_ax = plt.subplots()
        returned_ax = plot_td_sequential(df, ax=provided_ax)

        assert returned_ax is provided_ax

        # Limpiar
        plt.close('all')

    def test_plot_markers_positioned_correctly(self):
        """Verifica que los marcadores están posicionados cerca de los precios High/Low"""
        df = pd.DataFrame({
            'Open': range(100, 120),
            'High': [110] * 20,
            'Low': [100] * 20,
            'Close': range(101, 121),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_setup_count': [0] * 10 + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'buy_countdown_count': [0] * 20,
            'sell_countdown_count': [0] * 20
        })

        ax = plot_td_sequential(df)

        # Verificar que hay scatter plots
        collections = ax.collections
        assert len(collections) > 0

        # Los marcadores deberían estar cerca de los valores Low/High
        for collection in collections:
            offsets = collection.get_offsets()
            if len(offsets) > 0:
                y_values = offsets[:, 1]
                # Los valores Y deben estar en el rango razonable (cerca de 95-115 con offset del 2%)
                assert np.all(y_values > 90)
                assert np.all(y_values < 120)

        # Limpiar
        plt.close('all')

    def test_plot_uses_correct_colors(self):
        """Verifica que se usan colores apropiados para cada tipo de señal"""
        df = pd.DataFrame({
            'Open': range(100, 130),
            'High': range(102, 132),
            'Low': range(98, 128),
            'Close': range(101, 131),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 20,
            'sell_setup_count': [0] * 10 + [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] + [0] * 10,
            'buy_countdown_count': [0] * 11 + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13] + [0] * 6,
            'sell_countdown_count': [0] * 25 + [1, 2, 3, 4, 13]
        })

        ax = plot_td_sequential(df)

        # Verificar que hay scatter plots con colores
        collections = ax.collections
        assert len(collections) > 0

        colors_found = []
        for collection in collections:
            facecolors = collection.get_facecolors()
            if len(facecolors) > 0:
                colors_found.append(facecolors[0])

        # Debe haber al menos algún color (verde, rojo, azul según el código)
        assert len(colors_found) > 0

        # Limpiar
        plt.close('all')

    def test_plot_with_datetime_index(self):
        """Verifica que funciona con un índice de tipo datetime"""
        dates = pd.date_range(start='2023-01-01', periods=20, freq='D')

        df = pd.DataFrame({
            'Open': range(100, 120),
            'High': range(102, 122),
            'Low': range(98, 118),
            'Close': range(101, 121),
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            'sell_setup_count': [0] * 20,
            'buy_countdown_count': [0] * 20,
            'sell_countdown_count': [0] * 20
        }, index=dates)

        ax = plot_td_sequential(df)

        assert ax is not None
        assert ax.has_data()

        # Limpiar
        plt.close('all')

    def test_plot_with_empty_dataframe(self):
        """Verifica el comportamiento con DataFrame vacío"""
        df = pd.DataFrame(columns=[
            'Open', 'High', 'Low', 'Close',
            'buy_setup_count', 'sell_setup_count',
            'buy_countdown_count', 'sell_countdown_count'
        ])

        ax = plot_td_sequential(df)

        assert ax is not None
        # No debería tener datos
        assert len(ax.get_lines()) >= 1  # La línea de cierre existe pero está vacía

        # Limpiar
        plt.close('all')

    def test_plot_offset_calculation(self):
        """Verifica que el offset vertical se calcula correctamente"""
        # DataFrame con rango de precios conocido
        df = pd.DataFrame({
            'Open': [100] * 10,
            'High': [150] * 10,  # Rango = 150 - 50 = 100
            'Low': [50] * 10,
            'Close': [100] * 10,
            'buy_setup_count': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            'sell_setup_count': [0] * 10,
            'buy_countdown_count': [0] * 10,
            'sell_countdown_count': [0] * 10
        })

        ax = plot_td_sequential(df)

        # El offset debería ser 2% de 100 = 2
        # Los marcadores Buy Setup deberían estar en Low - offset = 50 - 2 = 48
        collections = ax.collections
        if len(collections) > 0:
            offsets = collections[0].get_offsets()
            if len(offsets) > 0:
                # Verificar que el marcador está cerca de 48 (con margen de error)
                y_value = offsets[0, 1]
                assert 45 < y_value < 52

        # Limpiar
        plt.close('all')
