# Tests de Visualización Estilo Bloomberg

## Descripción

Suite de tests que genera gráficos de **alta resolución** (150 DPI) con estilo visual similar a **Bloomberg Terminal**, incluyendo:

- ✅ Números TD Sequential (Setup 1-9 y Countdown 1-13)
- ✅ Niveles TDST (Support/Resistance) como líneas horizontales persistentes
- ✅ Fondo negro profesional estilo Bloomberg
- ✅ Grid sutil y leyendas profesionales
- ✅ Múltiples formatos: línea de precio, velas japonesas, paneles de resumen

---

## Tests Disponibles

### 1. `test_generate_bloomberg_style_chart_full_period`

Genera gráfico con **período completo** (2 años de datos del BKX Index).

**Archivo generado**: `tests/output_bloomberg_full_period.png`

**Características**:
- Resolución: **3000x1800 píxeles** (150 DPI)
- Período: 2024-01-16 a 2026-01-14 (502 barras)
- Incluye: Todos los niveles TDST históricos
- Formato: Línea de precio

**Elementos visuales**:
- Números verdes (Buy Setup) debajo del precio
- Números rojos (Sell Setup) arriba del precio
- Números cyan (Buy Countdown) debajo del precio
- Números magenta (Sell Countdown) arriba del precio
- Líneas verdes horizontales (TDST Buy - soporte)
- Líneas rojas horizontales (TDST Sell - resistencia)

---

### 2. `test_generate_bloomberg_style_chart_last_6_months`

Genera gráfico con **últimos 6 meses** (~120 barras).

**Archivo generado**: `tests/output_bloomberg_6months.png`

**Características**:
- Resolución: **3000x1800 píxeles** (150 DPI)
- Período: Últimos 6 meses
- Incluye: Niveles TDST activos en el período
- Formato: Línea de precio más gruesa (linewidth=2)

**Ideal para**:
- Análisis de corto plazo
- Visualización clara de señales recientes
- Comparación con gráficos de Bloomberg

---

### 3. `test_generate_bloomberg_style_chart_with_candlesticks`

Genera gráfico con **velas japonesas** (OHLC) en lugar de línea de precio.

**Archivo generado**: `tests/output_bloomberg_candlesticks.png`

**Características**:
- Resolución: **3300x1800 píxeles** (150 DPI)
- Período: Últimos 3 meses (60 barras)
- Incluye: Velas japonesas + TDST + números TD
- Formato: Candlesticks (verde=alcista, rojo=bajista)

**Elementos visuales**:
- Velas japonesas con cuerpo y mechas
- Colores: Verde (#00ff00) para velas alcistas, Rojo (#ff0000) para bajistas
- Mejor visualización de patrones OHLC
- Números TD Sequential sobre las velas

---

### 4. `test_generate_bloomberg_style_chart_with_summary`

Genera gráfico con **panel de resumen** de estadísticas.

**Archivo generado**: `tests/output_bloomberg_with_summary.png`

**Características**:
- Resolución: **3300x2100 píxeles** (150 DPI)
- Período: 2 años completos
- Incluye: Gráfico principal + 3 paneles de información
- Formato: Multi-panel con estadísticas

**Paneles de información**:
1. **Panel 1 - Señales Completadas**:
   - Buy Setups: X
   - Sell Setups: X
   - Buy Countdowns: X
   - Sell Countdowns: X

2. **Panel 2 - Última Señal**:
   - Muestra la última señal completada (Setup 9 o Countdown 13)
   - Incluye número de barra

3. **Panel 3 - Precio Actual**:
   - Precio actual del índice
   - Cambio porcentual en el período
   - Rango de fechas analizado

---

## Cómo Ejecutar los Tests

### Ejecutar todos los tests de visualización

```bash
pytest tests/test_visual_bloomberg.py -v -s
```

### Ejecutar un test específico

```bash
# Gráfico período completo
pytest tests/test_visual_bloomberg.py::TestBloombergStyleVisualization::test_generate_bloomberg_style_chart_full_period -v -s

# Gráfico 6 meses
pytest tests/test_visual_bloomberg.py::TestBloombergStyleVisualization::test_generate_bloomberg_style_chart_last_6_months -v -s

# Gráfico con velas
pytest tests/test_visual_bloomberg.py::TestBloombergStyleVisualization::test_generate_bloomberg_style_chart_with_candlesticks -v -s

# Gráfico con resumen
pytest tests/test_visual_bloomberg.py::TestBloombergStyleVisualization::test_generate_bloomberg_style_chart_with_summary -v -s
```

---

## Archivos Generados

Todos los gráficos se guardan en la carpeta `tests/`:

| Archivo | Resolución | Período | Descripción |
|---------|------------|---------|-------------|
| `output_bloomberg_full_period.png` | 3000x1800 | 2 años | Período completo con TDST |
| `output_bloomberg_6months.png` | 3000x1800 | 6 meses | Últimos 6 meses |
| `output_bloomberg_candlesticks.png` | 3300x1800 | 3 meses | Con velas japonesas |
| `output_bloomberg_with_summary.png` | 3300x2100 | 2 años | Con panel de estadísticas |

---

## Características de los Gráficos

### Estilo Visual Bloomberg

✅ **Fondo negro** (#0a0a0a) - Idéntico a Bloomberg Terminal
✅ **Grid sutil** - Alpha 0.15, color #404040
✅ **Texto blanco** - Títulos, ejes, labels
✅ **Spines minimalistas** - Solo bottom y left visibles
✅ **Leyenda profesional** - Fondo oscuro semitransparente

### Código de Colores TD Sequential

| Elemento | Color | Posición | Significado |
|----------|-------|----------|-------------|
| Buy Setup | Verde (#00ff00) | Debajo | Secuencia bajista 1-9 |
| Sell Setup | Rojo (#ff0000) | Arriba | Secuencia alcista 1-9 |
| Buy Countdown | Cyan (#00ffff) | Debajo | Cuenta regresiva 1-13 |
| Sell Countdown | Magenta (#ff00ff) | Arriba | Cuenta regresiva 1-13 |
| TDST Buy | Verde (#00ff00) | Línea horizontal | Soporte |
| TDST Sell | Rojo (#ff0000) | Línea horizontal | Resistencia |

### Niveles TDST

Los niveles TDST se dibujan como **líneas horizontales persistentes** que:

1. ✅ Se activan cuando se completa un Setup (9)
2. ✅ Permanecen activos hasta que el precio los rompe
3. ✅ Se invalidan si:
   - TDST Buy: `Low < tdst_buy`
   - TDST Sell: `High > tdst_sell`
4. ✅ Múltiples niveles pueden estar activos simultáneamente

---

## Implementación Técnica

### Métodos Auxiliares

La clase `TestBloombergStyleVisualization` incluye métodos helper:

1. **`_plot_tdst_levels(ax, df)`**
   - Dibuja niveles TDST como líneas horizontales
   - Detecta cambios de nivel y dibuja segmentos
   - Maneja invalidación de niveles

2. **`_plot_td_numbers(ax, df)`**
   - Marca números TD Sequential en el gráfico
   - Usa offsets verticales para separar Setup y Countdown
   - Colores y tamaños diferenciados

3. **`_plot_candlesticks(ax, df)`**
   - Dibuja velas japonesas OHLC
   - Colores verde/rojo según dirección
   - Ancho de vela proporcional al timeframe

4. **`_apply_bloomberg_style(ax, df, title)`**
   - Aplica estilo visual Bloomberg
   - Configura ejes, grid, leyenda
   - Formato de fechas profesional

5. **`_create_summary_panel(ax1, ax2, ax3, df)`**
   - Crea panel de resumen con estadísticas
   - Texto monospace estilo terminal
   - Colores dinámicos según datos

---

## Resoluciones y DPI

Todos los gráficos se generan con **150 DPI** (dots per inch):

| Tamaño (px) | Tamaño Impreso (pulgadas) | Uso Recomendado |
|-------------|---------------------------|-----------------|
| 3000x1800 | 20x12 | Pantallas 4K, presentaciones |
| 3300x1800 | 22x12 | Pantallas ultra-wide |
| 3300x2100 | 22x14 | Informes, dashboards |

**Para cambiar DPI**:
```python
plt.savefig(output_path, dpi=300, ...)  # Alta calidad para impresión
plt.savefig(output_path, dpi=72, ...)   # Web/pantalla estándar
```

---

## Comparación con Bloomberg

### Similitudes con Bloomberg Terminal

✅ **Colores idénticos**: Setup verde/rojo, Countdown cyan/magenta
✅ **Posicionamiento**: Números arriba (Sell) y abajo (Buy)
✅ **Niveles TDST**: Líneas horizontales persistentes
✅ **Fondo negro**: Estilo terminal profesional
✅ **Grid sutil**: No distrae del precio

### Diferencias menores

⚠️ **Fuentes**: Bloomberg usa fuentes propietarias
⚠️ **Grosor de líneas**: Puede variar ligeramente
⚠️ **Emojis en paneles**: Bloomberg no los usa (removidos en Windows)

---

## Ejemplos de Uso

### Generar todos los gráficos

```bash
pytest tests/test_visual_bloomberg.py -v -s
```

**Output esperado**:
```
[OK] Grafico generado: tests/output_bloomberg_full_period.png
   Resolucion: 3000x1800 pixeles
   Periodo: 2024-01-16 a 2026-01-14

[OK] Grafico generado: tests/output_bloomberg_6months.png
   Resolucion: 3000x1800 pixeles
   Periodo: 2025-07-25 a 2026-01-14

[OK] Grafico generado: tests/output_bloomberg_candlesticks.png
   Resolucion: 3300x1800 pixeles
   Periodo: 2025-10-20 a 2026-01-14

[OK] Grafico generado: tests/output_bloomberg_with_summary.png
   Resolucion: 3300x2100 pixeles
   Incluye: Panel de resumen de senales

======================== 4 passed in 5.49s =========================
```

### Personalizar resolución

Editar el test y cambiar el parámetro `dpi`:

```python
plt.savefig(output_path, dpi=300, facecolor='#0a0a0a', edgecolor='none')
```

### Cambiar período

Modificar el número de barras:

```python
# En lugar de tail(120) para 6 meses
df_custom = df_sequential.tail(250)  # ~1 año
```

---

## Notas Técnicas

### Fixture `bkx_data`

Los tests usan el fixture `bkx_data` que carga datos reales del BKX Index:

```python
@pytest.fixture
def bkx_data():
    """Cargar datos reales del BKX Index"""
    df = pd.read_csv('tests/bkx_data.csv', index_col=0, parse_dates=True)
    return df
```

### Manejo de Índices Datetime

Los niveles TDST requieren resetear el índice:

```python
# Resetear índice para TDST (usa .loc con enteros)
df_reset = df_sequential.reset_index(drop=False)
df_reset = df_reset.rename(columns={'index': 'Date'})
df_reset_calc = df_reset.drop(columns=['Date']).reset_index(drop=True)

# Calcular TDST
df_with_levels = calculate_tdst_levels(df_reset_calc)

# Restaurar índice datetime
df_with_levels['Date'] = df_reset['Date'].values
df_with_levels = df_with_levels.set_index('Date')
```

### Colores Hexadecimales

```python
BACKGROUND = '#0a0a0a'    # Negro casi absoluto
GRID = '#404040'          # Gris oscuro
BUY_SETUP = '#00ff00'     # Verde brillante
SELL_SETUP = '#ff0000'    # Rojo brillante
BUY_CD = '#00ffff'        # Cyan
SELL_CD = '#ff00ff'       # Magenta
WHITE = 'white'           # Texto y ejes
```

---

## Troubleshooting

### Error: "UnicodeEncodeError"

Si aparece error con emojis en Windows, asegúrate de que los `print()` no usen emojis:

```python
# ❌ Incorrecto
print("✅ Gráfico generado")

# ✅ Correcto
print("[OK] Grafico generado")
```

### Warning: "tight_layout not compatible"

Es esperado en el test con summary panel. Se puede ignorar o usar:

```python
plt.subplots_adjust(hspace=0.3)  # En lugar de tight_layout()
```

### Niveles TDST no aparecen

Verifica que hay Setups completados (9):

```python
print((df['buy_setup_count'] == 9).sum())   # Debe ser > 0
print((df['sell_setup_count'] == 9).sum())  # Debe ser > 0
```

---

## Próximas Mejoras

### v1.1 (Planeado)
- [ ] Exportar a PDF vectorial
- [ ] Animaciones GIF de señales
- [ ] Múltiples instrumentos en un solo gráfico
- [ ] Zoom interactivo con Plotly

### v1.2 (Futuro)
- [ ] Anotaciones automáticas de señales
- [ ] Integración con TradingView
- [ ] Dashboard web interactivo
- [ ] Alertas visuales cuando se completa señal

---

## Licencia

Estos tests están incluidos en la librería `tdsequential` bajo licencia MIT.

---

**¡Gráficos de calidad Bloomberg generados localmente! 🚀**
