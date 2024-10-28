
import numpy as np
import pandas as pd
from scipy import stats
import warnings
import pm4py
from tqdm import tqdm
import json
from pm4py.objects.log.importer.xes import importer as xes_importer


possible_distributions = [
    'fixed',
    'normal',
    'exponential',
    'uniform',
    'triangular',
    'lognormal',
    'gamma'
]

def n_to_weekday(i):
    weekday_labels = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    return dict(zip(range(7), weekday_labels))[i]

def find_best_fit_distribution(observed_values, N=None, remove_outliers=False):
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
        return 'fixed', {'value': np.mean(observed_values)}

    for distr_name in possible_distributions:
        try:
            if distr_name == 'fixed':
                distr_params[distr_name] = {'value': np.mean(observed_values)}
                generated_values[distr_name] = np.array([distr_params[distr_name]['value']] * N)
            elif distr_name == 'normal':
                dist = stats.norm
                loc, scale = dist.fit(observed_values)
                q75, q25 = np.percentile(observed_values, [75, 25])
                iqr = q75 - q25
                distr_params[distr_name] = {'loc': loc, 'scale': scale, 'max': q75 + iqr * 1.5, 'mean': np.mean(observed_values)}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            elif distr_name == 'exponential':
                dist = stats.expon
                loc, scale = dist.fit(observed_values)
                q75, q25 = np.percentile(observed_values, [75, 25])
                iqr = q75 - q25
                distr_params[distr_name] = {'loc': loc, 'scale': scale, 'max': q75 + iqr * 1.5, 'mean': np.mean(observed_values)}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            elif distr_name == 'uniform':
                dist = stats.uniform
                loc, scale = dist.fit(observed_values)
                q75, q25 = np.percentile(observed_values, [75, 25])
                iqr = q75 - q25
                distr_params[distr_name] = {'loc': loc, 'scale': scale, 'max': q75 + iqr * 1.5, 'mean': np.mean(observed_values)}
                generated_values[distr_name] = dist.rvs(loc=loc, scale=scale, size=N)
            elif distr_name == 'triangular':
                dist = stats.triang
                c, loc, scale = dist.fit(observed_values)
                q75, q25 = np.percentile(observed_values, [75, 25])
                iqr = q75 - q25
                distr_params[distr_name] = {'c': c, 'loc': loc, 'scale': scale, 'max': q75 + iqr * 1.5, 'mean': np.mean(observed_values)}
                generated_values[distr_name] = dist.rvs(c=c, loc=loc, scale=scale, size=N)
            elif distr_name == 'lognormal':
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", RuntimeWarning)
                    dist = stats.lognorm
                    s, loc, scale = dist.fit(observed_values)
                    q75, q25 = np.percentile(observed_values, [75, 25])
                    iqr = q75 - q25
                    distr_params[distr_name] = {'s': s, 'loc': loc, 'scale': scale, 'max': q75 + iqr * 1.5, 'mean': np.mean(observed_values)}
                    generated_values[distr_name] = dist.rvs(s=s, loc=loc, scale=scale, size=N)
            elif distr_name == 'gamma':
                dist = stats.gamma
                a, loc, scale = dist.fit(observed_values)
                q75, q25 = np.percentile(observed_values, [75, 25])
                iqr = q75 - q25
                distr_params[distr_name] = {'a': a, 'loc': loc, 'scale': scale, 'max': q75 + iqr * 1.5, 'mean': np.mean(observed_values)}
                generated_values[distr_name] = dist.rvs(a=a, loc=loc, scale=scale, size=N)
        except Exception as e:
            print(f"An error occurred while fitting distribution {distr_name}: {e}")
            continue

    wass_distances = {d_name: stats.wasserstein_distance(observed_values, generated_values[d_name]) for d_name in possible_distributions if d_name in generated_values}
    best_distr = min(wass_distances, key=wass_distances.get)

    return best_distr, distr_params[best_distr], wass_distances


def compute_execution_times(log, filter_by_res=None):
    activities = list(pm4py.get_event_attribute_values(log, 'concept:name').keys())
    print(f"Total activities identified: {len(activities)}")
    activities_extimes = {a: [] for a in activities}
    

    for trace in log:
        # print(f"Trace: {trace}")
        event_dict = {}
        prev_event = None
        for event in trace:
            print(f"Event: {event}")
            act = event['concept:name']
            trans = event['lifecycle:transition']
            timestamp = event['time:timestamp']
            res = event.get('org:resource', None)

            if trans == 'start':
                event_dict[act] = timestamp
            elif trans == 'complete' and act in event_dict:
                start_time = event_dict.pop(act)
                exec_time = (timestamp - start_time).total_seconds()
                if filter_by_res:
                    if res in filter_by_res:
                        activities_extimes[act].append(exec_time)
                else:
                    activities_extimes[act].append(exec_time)
            elif prev_event:
                exec_time = (timestamp - prev_event['time:timestamp']).total_seconds()
                if filter_by_res:
                    if res in filter_by_res:
                        activities_extimes[prev_event['concept:name']].append(exec_time)
                else:
                    activities_extimes[prev_event['concept:name']].append(exec_time)
            
            prev_event = event
    
    for a in list(activities_extimes.keys()):
        if not activities_extimes[a]:
            del activities_extimes[a]

    return activities_extimes


def find_execution_distributions(log, mode='activity'):
    """
    output: {ACTIVITY_NAME: (DISTRNAME, {PARAMS: VALUE})}
    """
    if mode == 'activity':
        activities_extimes = compute_execution_times(log)
        print(f"Activities with computed execution times: {len(activities_extimes)}")
        activities = list(activities_extimes.keys())
        exec_distr = {a: find_best_fit_distribution(activities_extimes[a])[:2] for a in activities}
    if mode == 'resource':
        resources = pm4py.get_event_attribute_values(log, "org:resource")
        exec_distr = dict()
        print('Finding best fit execution time distribution for each resource...')
        for res in tqdm(resources):
            activities_extimes = compute_execution_times(log, filter_by_res=[res])
            activities = list(activities_extimes.keys())
            exec_distr[res] = {a: find_best_fit_distribution(activities_extimes[a])[:2] for a in activities}
            
    return exec_distr

# log = xes_importer.apply('PurchasingExample.xes')
# print(type(log))
# acd = compute_execution_times(log)
# print(f"Number of activities with execution distributions: {len(acd)}")
# print(acd)
# # Convert the output to json and write it to a file
# with open('execution_distributions.json', 'w') as json_file:
#     json.dump(acd, json_file)