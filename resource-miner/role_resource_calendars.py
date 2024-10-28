import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from collections import defaultdict
import pandas as pd
import json

def structured_resource_calendar(log):
    resource_calendar = defaultdict(list)

    for case_index, case in enumerate(log):
        for event in case:
            resource = event['org:resource']
            timestamp = event['time:timestamp']
            resource_calendar[resource].append(timestamp)

    structured_resource_calendar = {}
    for resource, timestamps in resource_calendar.items():
        times = pd.Series(pd.to_datetime(timestamps))
        sorted_times = times.sort_values()
        workdays = sorted_times.dt.day_name().unique().tolist()
        weekly_times = sorted_times.groupby(sorted_times.dt.day_name()).agg(['min', 'max'])
        weekly_times_dict = weekly_times.applymap(lambda x: x.time().isoformat()).to_dict('index')
        structured_resource_calendar[resource] = {
            'workdays': workdays,
            'weekly_times': weekly_times_dict,
        }

    return structured_resource_calendar

def get_activity_resources(log):
    activity_resources = defaultdict(set)

    for case_index, case in enumerate(log):
        for event in case:
            activity = event['concept:name']
            resource = event['org:resource']
            activity_resources[activity].add(resource)

    activity_resource_list = []
    for activity, resources in activity_resources.items():
        activity_resource_list.append({
            'Activity': activity,
            'Resources': ', '.join(resources)
        })

    df = pd.DataFrame(activity_resource_list)
    return df.to_dict(orient='records')
