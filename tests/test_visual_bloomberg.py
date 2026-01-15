"""
Test de visualización estilo Bloomberg con niveles TDST
Genera PNG de alta resolución similar a los gráficos de Bloomberg Finance
"""

import pytest
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from tdsequential.core import calculate_td_sequential, get_last_signal
from tdsequential.levels import calculate_tdst_levels

# Configurar matplotlib para modo no interactivo
plt.switch_backend('Agg')


@pytest.fixture
def bkx_data():
    """Cargar datos reales del BKX Index"""
    df = pd.read_csv('tests/bkx_data.csv', index_col=0, parse_dates=True)
    return df


class TestBloombergStyleVisualization:
    """Tests de visualización estilo Bloomberg con alta resolución"""

    def test_generate_bloomberg_style_chart_full_period(self, bkx_data):
        """Genera gráfico estilo Bloomberg con período completo (2 años)"""
        # Calcular TD Sequential
        df_sequential = calculate_td_sequential(bkx_data)

        # Resetear índice para TDST
        df_reset = df_sequential.reset_index(drop=False)
        df_reset = df_reset.rename(columns={'index': 'Date'})
        df_reset_calc = df_reset.drop(columns=['Date']).reset_index(drop=True)

        # Calcular niveles TDST
        df_with_levels = calculate_tdst_levels(df_reset_calc)

        # Restaurar índice datetime
        df_with_levels['Date'] = df_reset['Date'].values
        df_with_levels = df_with_levels.set_index('Date')

        # Crear figura de alta resolución
        fig, ax = plt.subplots(figsize=(20, 12), dpi=150)

        # Configurar fondo negro estilo Bloomberg
        ax.set_facecolor('#0a0a0a')
        fig.patch.set_facecolor('#0a0a0a')

        # Graficar precio de cierre
        ax.plot(df_with_levels.index, df_with_levels['Close'],
                color='white', linewidth=1.5, label='BKX Index - Close', zorder=5)

        # Graficar niveles TDST como líneas horizontales
        self._plot_tdst_levels(ax, df_with_levels)

        # Marcar números de Setup y Countdown
        self._plot_td_numbers(ax, df_with_levels)

        # Personalización estilo Bloomberg
        self._apply_bloomberg_style(ax, df_with_levels,
                                     title='BKX Index (KBW Bank Index) - TD Sequential Analysis')

        # Guardar PNG de alta resolución
        plt.tight_layout()
        output_path = 'tests/output_bloomberg_full_period.png'
        plt.savefig(output_path, dpi=150, facecolor='#0a0a0a', edgecolor='none')
        plt.close('all')

        print("\n[OK] Grafico generado: " + output_path)
        print("   Resolucion: 3000x1800 pixeles")
        print(f"   Periodo: {df_with_levels.index[0].date()} a {df_with_levels.index[-1].date()}")

    def test_generate_bloomberg_style_chart_last_6_months(self, bkx_data):
        """Genera gráfico estilo Bloomberg con últimos 6 meses"""
        # Calcular TD Sequential
        df_sequential = calculate_td_sequential(bkx_data)

        # Tomar últimos 6 meses (~120 barras diarias)
        df_6m = df_sequential.tail(120)

        # Resetear índice para TDST
        df_reset = df_6m.reset_index(drop=False)
        df_reset = df_reset.rename(columns={'index': 'Date'})
        df_reset_calc = df_reset.drop(columns=['Date']).reset_index(drop=True)

        # Calcular niveles TDST
        df_with_levels = calculate_tdst_levels(df_reset_calc)

        # Restaurar índice datetime
        df_with_levels['Date'] = df_reset['Date'].values
        df_with_levels = df_with_levels.set_index('Date')

        # Crear figura de alta resolución
        fig, ax = plt.subplots(figsize=(20, 12), dpi=150)

        # Configurar fondo negro estilo Bloomberg
        ax.set_facecolor('#0a0a0a')
        fig.patch.set_facecolor('#0a0a0a')

        # Graficar precio de cierre
        ax.plot(df_with_levels.index, df_with_levels['Close'],
                color='white', linewidth=2, label='BKX Index', zorder=5)

        # Graficar niveles TDST
        self._plot_tdst_levels(ax, df_with_levels)

        # Marcar números de Setup y Countdown
        self._plot_td_numbers(ax, df_with_levels)

        # Personalización estilo Bloomberg
        self._apply_bloomberg_style(ax, df_with_levels,
                                     title='BKX Index - TD Sequential (Últimos 6 Meses)')

        # Guardar PNG de alta resolución
        plt.tight_layout()
        output_path = 'tests/output_bloomberg_6months.png'
        plt.savefig(output_path, dpi=150, facecolor='#0a0a0a', edgecolor='none')
        plt.close('all')

        print("\n[OK] Grafico generado: " + output_path)
        print("   Resolucion: 3000x1800 pixeles")
        print(f"   Periodo: {df_with_levels.index[0].date()} a {df_with_levels.index[-1].date()}")

    def test_generate_bloomberg_style_chart_with_candlesticks(self, bkx_data):
        """Genera gráfico estilo Bloomberg con velas japonesas (OHLC)"""
        # Calcular TD Sequential
        df_sequential = calculate_td_sequential(bkx_data)

        # Tomar últimos 3 meses para mejor visualización de velas
        df_3m = df_sequential.tail(60)

        # Resetear índice para TDST
        df_reset = df_3m.reset_index(drop=False)
        df_reset = df_reset.rename(columns={'index': 'Date'})
        df_reset_calc = df_reset.drop(columns=['Date']).reset_index(drop=True)

        # Calcular niveles TDST
        df_with_levels = calculate_tdst_levels(df_reset_calc)

        # Restaurar índice datetime
        df_with_levels['Date'] = df_reset['Date'].values
        df_with_levels = df_with_levels.set_index('Date')

        # Crear figura de alta resolución
        fig, ax = plt.subplots(figsize=(22, 12), dpi=150)

        # Configurar fondo negro estilo Bloomberg
        ax.set_facecolor('#0a0a0a')
        fig.patch.set_facecolor('#0a0a0a')

        # Graficar velas japonesas
        self._plot_candlesticks(ax, df_with_levels)

        # Graficar niveles TDST
        self._plot_tdst_levels(ax, df_with_levels)

        # Marcar números de Setup y Countdown
        self._plot_td_numbers(ax, df_with_levels)

        # Personalización estilo Bloomberg
        self._apply_bloomberg_style(ax, df_with_levels,
                                     title='BKX Index - TD Sequential with Candlesticks (3 Months)')

        # Guardar PNG de alta resolución
        plt.tight_layout()
        output_path = 'tests/output_bloomberg_candlesticks.png'
        plt.savefig(output_path, dpi=150, facecolor='#0a0a0a', edgecolor='none')
        plt.close('all')

        print("\n[OK] Grafico generado: " + output_path)
        print("   Resolucion: 3300x1800 pixeles")
        print(f"   Periodo: {df_with_levels.index[0].date()} a {df_with_levels.index[-1].date()}")

    def test_generate_bloomberg_style_chart_with_summary(self, bkx_data):
        """Genera gráfico estilo Bloomberg con panel de resumen de señales"""
        # Calcular TD Sequential
        df_sequential = calculate_td_sequential(bkx_data)

        # Resetear índice para TDST
        df_reset = df_sequential.reset_index(drop=False)
        df_reset = df_reset.rename(columns={'index': 'Date'})
        df_reset_calc = df_reset.drop(columns=['Date']).reset_index(drop=True)

        # Calcular niveles TDST
        df_with_levels = calculate_tdst_levels(df_reset_calc)

        # Restaurar índice datetime
        df_with_levels['Date'] = df_reset['Date'].values
        df_with_levels = df_with_levels.set_index('Date')

        # Crear figura con subplots (gráfico principal + panel de info)
        fig = plt.figure(figsize=(22, 14), dpi=150)
        gs = fig.add_gridspec(4, 1, height_ratios=[3, 0.3, 0.3, 0.3], hspace=0.3)

        ax_main = fig.add_subplot(gs[0])
        ax_info1 = fig.add_subplot(gs[1])
        ax_info2 = fig.add_subplot(gs[2])
        ax_info3 = fig.add_subplot(gs[3])

        # Configurar fondo negro
        fig.patch.set_facecolor('#0a0a0a')
        for ax in [ax_main, ax_info1, ax_info2, ax_info3]:
            ax.set_facecolor('#0a0a0a')

        # Gráfico principal
        ax_main.plot(df_with_levels.index, df_with_levels['Close'],
                     color='white', linewidth=1.8, label='BKX Index', zorder=5)

        self._plot_tdst_levels(ax_main, df_with_levels)
        self._plot_td_numbers(ax_main, df_with_levels)
        self._apply_bloomberg_style(ax_main, df_with_levels,
                                     title='BKX Index - Complete TD Sequential Analysis')

        # Panel de resumen
        self._create_summary_panel(ax_info1, ax_info2, ax_info3, df_with_levels)

        # Guardar PNG de alta resolución
        plt.tight_layout()
        output_path = 'tests/output_bloomberg_with_summary.png'
        plt.savefig(output_path, dpi=150, facecolor='#0a0a0a', edgecolor='none')
        plt.close('all')

        print("\n[OK] Grafico generado: " + output_path)
        print("   Resolucion: 3300x2100 pixeles")
        print("   Incluye: Panel de resumen de senales")

    # ============== Métodos auxiliares ==============

    def _plot_tdst_levels(self, ax, df):
        """Grafica niveles TDST como líneas horizontales persistentes"""
        # TDST Buy (soporte - verde)
        tdst_buy_active = None
        for i, idx in enumerate(df.index):
            current_tdst = df.loc[idx, 'tdst_buy']

            if pd.notna(current_tdst):
                if tdst_buy_active is None or tdst_buy_active != current_tdst:
                    # Nuevo nivel TDST Buy
                    tdst_buy_active = current_tdst
                    start_idx = i

                # Dibujar línea hasta el siguiente índice o final
                if i < len(df) - 1:
                    ax.hlines(current_tdst, df.index[start_idx], df.index[i+1],
                             colors='#00ff00', linestyles='solid', linewidth=1.5,
                             alpha=0.7, zorder=3, label='TDST Buy' if i == start_idx else '')
            else:
                tdst_buy_active = None

        # TDST Sell (resistencia - rojo)
        tdst_sell_active = None
        for i, idx in enumerate(df.index):
            current_tdst = df.loc[idx, 'tdst_sell']

            if pd.notna(current_tdst):
                if tdst_sell_active is None or tdst_sell_active != current_tdst:
                    # Nuevo nivel TDST Sell
                    tdst_sell_active = current_tdst
                    start_idx = i

                # Dibujar línea hasta el siguiente índice o final
                if i < len(df) - 1:
                    ax.hlines(current_tdst, df.index[start_idx], df.index[i+1],
                             colors='#ff0000', linestyles='solid', linewidth=1.5,
                             alpha=0.7, zorder=3, label='TDST Sell' if i == start_idx else '')
            else:
                tdst_sell_active = None

    def _plot_td_numbers(self, ax, df):
        """Marca los números de TD Sequential en el gráfico"""
        price_range = df['High'].max() - df['Low'].min()
        offset = 0.015 * price_range

        for i, idx in enumerate(df.index):
            # Buy Setup (números verdes abajo)
            buy_setup = df.loc[idx, 'buy_setup_count']
            if buy_setup > 0:
                price = df.loc[idx, 'Low']
                ax.text(idx, price - offset, str(int(buy_setup)),
                       color='#00ff00', fontsize=10, ha='center', va='top',
                       fontweight='bold', zorder=10)

            # Sell Setup (números rojos arriba)
            sell_setup = df.loc[idx, 'sell_setup_count']
            if sell_setup > 0:
                price = df.loc[idx, 'High']
                ax.text(idx, price + offset, str(int(sell_setup)),
                       color='#ff0000', fontsize=10, ha='center', va='bottom',
                       fontweight='bold', zorder=10)

            # Buy Countdown (números cyan abajo)
            buy_cd = df.loc[idx, 'buy_countdown_count']
            if buy_cd > 0 and buy_cd <= 13:
                price = df.loc[idx, 'Low']
                ax.text(idx, price - offset * 2.5, str(int(buy_cd)),
                       color='#00ffff', fontsize=9, ha='center', va='top',
                       fontweight='normal', zorder=10)

            # Sell Countdown (números magenta arriba)
            sell_cd = df.loc[idx, 'sell_countdown_count']
            if sell_cd > 0 and sell_cd <= 13:
                price = df.loc[idx, 'High']
                ax.text(idx, price + offset * 2.5, str(int(sell_cd)),
                       color='#ff00ff', fontsize=9, ha='center', va='bottom',
                       fontweight='normal', zorder=10)

    def _plot_candlesticks(self, ax, df):
        """Grafica velas japonesas (candlesticks)"""
        # Velas alcistas (verde) y bajistas (rojo)
        for idx in df.index:
            open_price = df.loc[idx, 'Open']
            close_price = df.loc[idx, 'Close']
            high_price = df.loc[idx, 'High']
            low_price = df.loc[idx, 'Low']

            # Color según dirección
            color = '#00ff00' if close_price >= open_price else '#ff0000'

            # Dibujar mecha (high-low)
            ax.plot([idx, idx], [low_price, high_price],
                   color=color, linewidth=0.8, alpha=0.8, zorder=2)

            # Dibujar cuerpo
            body_height = abs(close_price - open_price)
            body_bottom = min(open_price, close_price)

            # Ancho de la vela (aproximado)
            if len(df) > 1:
                # Calcular ancho basado en el intervalo entre barras
                time_diff = (df.index[1] - df.index[0]).total_seconds() / 86400  # en días
                width = time_diff * 0.6
            else:
                width = 0.6

            rect = Rectangle((mdates.date2num(idx) - width/2, body_bottom),
                           width, body_height,
                           facecolor=color, edgecolor=color,
                           alpha=0.8, zorder=3)
            ax.add_patch(rect)

    def _apply_bloomberg_style(self, ax, df, title=''):
        """Aplica estilo visual similar a Bloomberg Terminal"""
        # Título
        ax.set_title(title, color='white', fontsize=18, fontweight='bold', pad=20)

        # Ejes
        ax.set_xlabel('Date', color='white', fontsize=14, fontweight='bold')
        ax.set_ylabel('Price', color='white', fontsize=14, fontweight='bold')

        # Ticks
        ax.tick_params(colors='white', labelsize=11)

        # Spines
        for spine in ['bottom', 'left']:
            ax.spines[spine].set_color('white')
            ax.spines[spine].set_linewidth(1.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        # Grid estilo Bloomberg
        ax.grid(True, alpha=0.15, color='#404040', linestyle='-', linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)

        # Formato de fechas
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Leyenda estilo Bloomberg
        legend = ax.legend(loc='upper left', fontsize=10, framealpha=0.9,
                          facecolor='#1a1a1a', edgecolor='white')
        plt.setp(legend.get_texts(), color='white')

    def _create_summary_panel(self, ax1, ax2, ax3, df):
        """Crea panel de resumen con estadísticas de señales"""
        # Ocultar ejes
        for ax in [ax1, ax2, ax3]:
            ax.axis('off')

        # Calcular estadísticas
        buy_setups = (df['buy_setup_count'] == 9).sum()
        sell_setups = (df['sell_setup_count'] == 9).sum()
        buy_countdowns = (df['buy_countdown_count'] == 13).sum()
        sell_countdowns = (df['sell_countdown_count'] == 13).sum()

        last_signal = get_last_signal(df)
        last_price = df['Close'].iloc[-1]
        first_price = df['Close'].iloc[0]
        price_change_pct = ((last_price - first_price) / first_price) * 100

        # Panel 1: Señales completadas
        text1 = ("SENALES COMPLETADAS:\n" +
                f"   Buy Setups: {buy_setups} | Sell Setups: {sell_setups} | " +
                f"Buy Countdowns: {buy_countdowns} | Sell Countdowns: {sell_countdowns}")
        ax1.text(0.05, 0.5, text1, fontsize=12, color='white',
                verticalalignment='center', fontfamily='monospace')

        # Panel 2: Última señal
        text2 = f"ULTIMA SENAL: {last_signal if last_signal else 'Ninguna'}"
        ax2.text(0.05, 0.5, text2, fontsize=12, color='#00ff00' if last_signal else 'white',
                verticalalignment='center', fontfamily='monospace', fontweight='bold')

        # Panel 3: Precio actual
        price_color = '#00ff00' if price_change_pct >= 0 else '#ff0000'
        text3 = (f"PRECIO ACTUAL: ${last_price:.2f} | " +
                f"Cambio: {price_change_pct:+.2f}% | " +
                f"Periodo: {df.index[0].date()} - {df.index[-1].date()}")
        ax3.text(0.05, 0.5, text3, fontsize=12, color=price_color,
                verticalalignment='center', fontfamily='monospace', fontweight='bold')


if __name__ == '__main__':
    # Ejecutar tests para generar gráficos
    pytest.main([__file__, '-v', '-s'])
