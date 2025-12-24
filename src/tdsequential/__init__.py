"""
tdsequential - Indicador TD Sequential de Tom DeMark
"""
__version__ = "0.1.0"

from .core import calculate_td_sequential, get_last_signal
from .plot import plot_td_sequential

__all__ = ["calculate_td_sequential", "get_last_signal", "plot_td_sequential", "__version__"]
