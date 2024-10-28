import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer
from collections import defaultdict
import pandas as pd
import json

def structured_resource_calendar(log):
    resource_calendar = defaultdict(list)

    # Step 1: Extract timestamps for each resource
    for case in log:
        for event in case:
            resource = event['org:resource']
            timestamp = event['time:timestamp']
            resource_calendar[resource].append(timestamp)

    structured_resource_calendar = []

    for resource, timestamps in resource_calendar.items():
        # Convert timestamps to pandas datetime, ensuring they are timezone naive
        times = pd.Series(pd.to_datetime(timestamps)).dt.tz_localize(None)
        
        # Step 2: Classify times by day of the week and date
        times_df = pd.DataFrame({
            'timestamp': times,
            'day_of_week': times.dt.day_name(),
            'date': times.dt.date
        })
        
        # Get the unique workdays
        workdays = times.dt.day_name().unique().tolist()
        
        # Step 3: Find min and max times for each day of the week ensuring they are from the same date
        min_max_times_per_day = times_df.groupby(['day_of_week', 'date'])['timestamp'].agg(['min', 'max'])
        
        # Aggregate min and max times by day of the week
        min_max_times = min_max_times_per_day.groupby(level=0).agg({'min': 'min', 'max': 'max'})

        # Ensure min and max times are correctly formatted
        min_max_times_dict = min_max_times.apply(
            lambda row: {
                'min': row['min'].time().isoformat() if pd.notna(row['min']) else None,
                'max': row['max'].time().isoformat() if pd.notna(row['max']) else None
            }, axis=1).to_dict()

        structured_resource_calendar.append({
            'name': resource,
            'workdays': workdays,
            'weekly_times': min_max_times_dict,
        })

    return structured_resource_calendar

# Example usage:
# log = xes_importer.apply('path_to_log.xes')
# print(json.dumps(structured_resource_calendar(log), indent=4))








# def structured_resource_calendar(log):
#     resource_calendar = defaultdict(list)

#     for case_index, case in enumerate(log):
#         for event in case:
#             resource = event['org:resource']
#             timestamp = event['time:timestamp']
#             resource_calendar[resource].append(timestamp)

#     structured_resource_calendar = []
#     for resource, timestamps in resource_calendar.items():
#         times = pd.Series(pd.to_datetime(timestamps))
#         sorted_times = times.sort_values()
#         workdays = sorted_times.dt.day_name().unique().tolist()
#         weekly_times = sorted_times.groupby(sorted_times.dt.day_name()).agg(['min', 'max'])
#         weekly_times_dict = weekly_times.applymap(lambda x: x.time().isoformat()).to_dict('index')
#         structured_resource_calendar.append({
#             'name': resource,
#             'workdays': workdays,
#             'weekly_times': weekly_times_dict,
#         })

#     return structured_resource_calendar

# # Example usage
# # log = pm4py.read_xes('PurchasingExample.xes')
# # acd = structured_resource_calendar(log)
# # print(json.dumps(acd, indent=4))
