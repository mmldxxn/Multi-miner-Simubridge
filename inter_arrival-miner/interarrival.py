# computation.py

import numpy as np
import scipy.stats as stats
import warnings
from pm4py.objects.log.importer.xes import importer as xes_importer
from typing import Dict, Any, List

possible_distributions = [
    'fixed',
    'normal',
    'exponential',
    'uniform',
    'triangular',
    'lognormal',
    'gamma'
]

def find_best_fit_distribution(observed_values, N=None, remove_outliers=False) -> Dict[str, Any]:
    if remove_outliers:
        q1 = np.percentile(observed_values, 25)
        q3 = np.percentile(observed_values, 75)
        iqr = q3 - q1
        lower_limit = q1 - 1.5 * iqr
        upper_limit = q3 + 1.5 * iqr
        observed_values = observed_values[(observed_values >= lower_limit) & (observed_values <= upper_limit)]
    
    if not N:
        N = len(observed_values)

    generated_values = dict()
    distr_params = {d: dict() for d in possible_distributions}

    if np.min(observed_values) == np.max(observed_values):
        return {
            "arrival_time_distribution": {
                "distribution_name": 'fixed',
                "distribution_params": [{"value": np.mean(observed_values)}]
            }
        }

    for distr_name in possible_distributions:
        try:
            if distr_name == 'fixed':
                distr_params[distr_name] = {'value': np.mean(observed_values)}
                generated_values[distr_name] = np.array([distr_params[distr_name]['value']] * N)
            elif distr_name == 'normal':
                dist = stats.norm
                loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'loc': loc, 'scale': scale}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            elif distr_name == 'exponential':
                dist = stats.expon
                loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'loc': loc, 'scale': scale}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            elif distr_name == 'uniform':
                dist = stats.uniform
                loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'loc': loc, 'scale': scale}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            elif distr_name == 'triangular':
                dist = stats.triang
                c, loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'c': c, 'loc': loc, 'scale': scale}
                generated_values[distr_name] = dist.rvs(c=c, loc=loc, scale=scale, size=N)
            elif distr_name == 'lognormal':
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    dist = stats.lognorm
                    s, loc, scale = dist.fit(observed_values)
                    distr_params[distr_name] = {'s': s, 'loc': loc, 'scale': scale}
                    generated_values[distr_name] = dist.rvs(s=s, loc=loc, scale=scale, size=N)
            elif distr_name == 'gamma':
                dist = stats.gamma
                a, loc, scale = dist.fit(observed_values)
                distr_params[distr_name] = {'a': a, 'loc': loc, 'scale': scale}
                generated_values[distr_name] = dist.rvs(a=a, loc=loc, scale=scale, size=N)
        except Exception as e:
            print(f"An error occurred while fitting distribution {distr_name}: {e}")
            continue

    wass_distances = {d_name: stats.wasserstein_distance(observed_values, generated_values[d_name]) for d_name in possible_distributions if d_name in generated_values}
    best_distr = min(wass_distances, key=wass_distances.get)

    distr_params_list = [{"value": value} for value in distr_params[best_distr].values()]

    return {
        "arrival_time_distribution": {
            "distribution_name": best_distr,
            "distribution_params": distr_params_list
        }
    }

def compute_inter_arrival_times(log) -> list:
    inter_arrival_times = []
    start_times = []
    
    for trace in log:
        for event in trace:
            if event['lifecycle:transition'] == 'start':
                start_times.append(event['time:timestamp'])
                break

    start_times.sort()

    for i in range(1, len(start_times)):
        time_1 = start_times[i]
        time_0 = start_times[i - 1]
        inter_arrival_times.append((time_1 - time_0).total_seconds())
    
    return inter_arrival_times

def find_inter_arrival_distribution(log) -> Dict[str, Any]:
    inter_arrival_times = compute_inter_arrival_times(log)
    return find_best_fit_distribution(inter_arrival_times)
