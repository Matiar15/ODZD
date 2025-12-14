import numpy as np

def filter_outliers(data):
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1

    # Find out the bounds
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    filtered_outliers = [x for x in data if lower_bound <= x <= upper_bound]
    return filtered_outliers