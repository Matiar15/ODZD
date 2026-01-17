"""
Moduł do filtrowania wartości odstających (outliers) z danych pomiarowych.

Wykorzystuje metodę IQR (Interquartile Range) - standardową technikę
statystyczną do identyfikacji i usuwania wartości ekstremalnych.
"""

import numpy as np


def filter_outliers(data: list[float]) -> list[float]:
    """
    Filtruje wartości odstające z listy danych metodą IQR.

    Metoda IQR (Interquartile Range):
    - Q1: pierwszy kwartyl (25. percentyl)
    - Q3: trzeci kwartyl (75. percentyl)
    - IQR = Q3 - Q1
    - Dolna granica: Q1 - 1.5 * IQR
    - Górna granica: Q3 + 1.5 * IQR

    Wartości poza tymi granicami są uznawane za outliers i usuwane.

    Args:
        data: Lista wartości numerycznych do przefiltrowania.

    Returns:
        Lista wartości bez outlierów.

    Example:
        >>> data = [1, 2, 3, 4, 5, 100]  # 100 to outlier
        >>> filter_outliers(data)
        [1, 2, 3, 4, 5]
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    # Wyznaczenie granic akceptowalnych wartości
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    filtered_outliers = [x for x in data if lower_bound <= x <= upper_bound]
    return filtered_outliers
