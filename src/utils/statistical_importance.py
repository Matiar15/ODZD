import typing
import logging

from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu

_logger = logging.getLogger(__name__)

def is_statistically_significant(first_data: list[typing.Any], second_data: list[typing.Any],):
    shapiro_1 = shapiro(first_data)
    shapiro_2 = shapiro(second_data)

    _logger.info(f"Shapiro-Wilk Test for first dataset: p-value = {shapiro_1.pvalue}")
    _logger.info(f"Shapiro-Wilk Test for second dataset: p-value = {shapiro_2.pvalue}")

    if shapiro_1.pvalue > 0.05 and shapiro_2.pvalue > 0.05:
        _logger.info("There is no basis to reject H0 that both lists are normally distributed.")

        levene_test = levene(first_data, second_data)
        _logger.info(f"Levene's Test: p-value = {levene_test.pvalue}")

        if levene_test.pvalue > 0.05:
            _logger.info("There is no basis to reject H0 that the variances are equal, I perform a Student's t-test.")
            t_test = ttest_ind(first_data, second_data, equal_var=True)
        else:
            _logger.info("Variances are not equal, I am doing t-Welch test.")
            t_test = ttest_ind(first_data, second_data, equal_var=False)

        _logger.info(f"T-test: p-value = {t_test.pvalue}")
        if t_test.pvalue > 0.05:
            _logger.info("There is no basis to reject H0 that the difference in distributions is not statistically significant.")
        else:
            _logger.info(f"Because the p-value is less than the assumed significance level (α=0.05), the difference between the distributions is statistically significant. We can therefore reject the null hypothesis and accept the alternative that the distributions of the two samples differ statistically significantly.")
    else:
        _logger.info("At least one list is not normally distributed, I perform the Mann-Whitney test.")
        mann_whitney = mannwhitneyu(first_data, second_data, alternative='two-sided')
        _logger.info(f"Mann-Whitney U Test: p-value = {mann_whitney.pvalue}, so...")
        if mann_whitney.pvalue > 0.05:
            _logger.info("There is no basis to reject H0 that the difference in distributions is not statistically significant.")
        else:
            _logger.info(f"Because the p-value is less than the assumed significance level (α=0.05), the difference between the distributions is statistically significant. We can therefore reject the null hypothesis and accept the alternative that the distributions of the two samples differ statistically significantly.")
