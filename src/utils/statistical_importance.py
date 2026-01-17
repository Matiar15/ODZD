"""
Moduł do testowania istotności statystycznej różnic między próbkami.

Implementuje:
- Porównanie wielu grup (Shapiro-Wilk → ANOVA/Kruskal-Wallis)

Poziom istotności α = 0.05.
"""

import logging

from scipy.stats import shapiro, f_oneway, kruskal

_logger = logging.getLogger(__name__)


def compare_multiple_groups(
    groups: dict[str, list[float]],
    group_names: list[str] = None,  # type: ignore
) -> dict:
    """
    Porównuje wiele grup danych pod kątem istotności statystycznej różnic.

    Używane do porównania wyników dla różnej liczby klientów (1 vs 3 vs 5).

    Procedura:
    1. Test Shapiro-Wilka dla każdej grupy (normalność)
    2. Jeśli wszystkie normalne → ANOVA (test_concurrent.ipynb F)
    3. Jeśli którakolwiek nienormalna → Kruskal-Wallis (nieparametryczny)

    Args:
        groups: Dict gdzie klucz to nazwa grupy (np. "1_client"),
                wartość to lista pomiarów.
        group_names: Opcjonalna lista nazw grup do wyświetlenia.

    Returns:
        Dict z wynikami:
        - test_used: "ANOVA" lub "Kruskal-Wallis"
        - p_value: Wartość p testu
        - is_significant: True jeśli p < 0.05
        - normality: Dict z wynikami Shapiro-Wilka per grupa

    Example:
        >>> results = compare_multiple_groups({
        ...     "1_client": latency_1,
        ...     "3_clients": latency_3,
        ...     "5_clients": latency_5
        ... })
        >>> if results["is_significant"]:
        ...     print("Liczba klientów istotnie wpływa na wydajność!")
    """
    if group_names is None:
        group_names = list(groups.keys())

    group_data = [groups[name] for name in group_names]

    # Test normalności dla każdej grupy
    normality_results = {}
    all_normal = True

    _logger.info("=" * 60)
    _logger.info("PORÓWNANIE WIELU GRUP")
    _logger.info("=" * 60)

    for name in group_names:
        data = groups[name]
        if len(data) < 3:
            _logger.warning(
                f"Grupa '{name}' ma za mało danych ({len(data)}) dla testu Shapiro-Wilka"
            )
            normality_results[name] = {"p_value": None, "is_normal": None}
            all_normal = False
            continue

        stat, p_value = shapiro(data)
        is_normal = p_value > 0.05
        normality_results[name] = {"p_value": p_value, "is_normal": is_normal}  # type: ignore

        _logger.info(
            f"Shapiro-Wilk dla '{name}': p={p_value:.6f} → {'normalny' if is_normal else 'nienormalny'}"
        )

        if not is_normal:
            all_normal = False

    # Wybór testu i wykonanie
    if all_normal:
        _logger.info(
            "\nWszystkie grupy mają rozkład normalny → używam ANOVA (test_concurrent.ipynb F)"
        )
        stat, p_value = f_oneway(*group_data)  # type: ignore
        test_used = "ANOVA"
    else:
        _logger.info(
            "\nCo najmniej jedna grupa ma rozkład nienormalny → używam Kruskal-Wallis"
        )
        stat, p_value = kruskal(*group_data)  # type: ignore
        test_used = "Kruskal-Wallis"

    is_significant = p_value < 0.05

    # Użyj notacji naukowej dla bardzo małego p-value
    p_str = f"{p_value:.2e}" if p_value < 0.0001 else f"{p_value:.6f}"
    _logger.info(f"\n{test_used}: statystyka={stat:.4f}, p-value={p_str}")

    if is_significant:
        _logger.info(
            "✓ WNIOSEK: Różnice między grupami SĄ istotne statystycznie (p < 0.05)"
        )
        _logger.info("  Liczba klientów WPŁYWA na wydajność bazy danych.")
    else:
        _logger.info(
            "✗ WNIOSEK: Brak istotnych statystycznie różnic między grupami (p ≥ 0.05)"
        )
        _logger.info("  Nie wykazano wpływu liczby klientów na wydajność.")

    _logger.info("=" * 60)

    return {
        "test_used": test_used,
        "statistic": stat,
        "p_value": p_value,
        "is_significant": is_significant,
        "normality": normality_results,
    }
