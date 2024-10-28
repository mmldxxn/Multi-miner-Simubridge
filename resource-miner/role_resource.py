from pm4py.objects.log.importer.xes import importer as xes_importer
from collections import defaultdict
import pandas as pd

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
