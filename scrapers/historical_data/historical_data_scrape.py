import nfl_data_py as nfl
import json
import os
import traceback
import pandas as pd
from dotenv import load_dotenv, find_dotenv

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()  
        return super().default(obj)

def save_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, cls=CustomJSONEncoder, indent=4)
    print(f"Saved data to {output_file}")

load_dotenv(find_dotenv())

dataPath = os.getenv('DATA_PATH')
output_folder = os.path.join(dataPath, 'historical_data')
os.makedirs(output_folder, exist_ok=True)

years = [2019, 2020, 2021, 2022, 2023]

try:
    weekly_data = nfl.import_weekly_data(years)
    seasonal_data = nfl.import_seasonal_data(years)
    schedules = nfl.import_schedules(years)
    scoring_lines = nfl.import_sc_lines(years)
    injuries = nfl.import_injuries(years)
    depth_charts = nfl.import_depth_charts(years)
    snap_counts = nfl.import_snap_counts(years)
    passing_data = nfl.import_ngs_data(stat_type='passing', years=years)
    rushing_data = nfl.import_ngs_data(stat_type='rushing', years=years)
    receiving_data = nfl.import_ngs_data(stat_type='receiving', years=years)

    # Save each dataset to a separate JSON file
    save_json(weekly_data.to_dict(orient="records"), os.path.join(output_folder, 'weekly_data.json'))
    save_json(seasonal_data.to_dict(orient="records"), os.path.join(output_folder, 'seasonal_data.json'))
    save_json(schedules.to_dict(orient="records"), os.path.join(output_folder, 'schedules.json'))
    save_json(scoring_lines.to_dict(orient="records"), os.path.join(output_folder, 'scoring_lines.json'))
    save_json(injuries.to_dict(orient="records"), os.path.join(output_folder, 'injuries.json'))
    save_json(depth_charts.to_dict(orient="records"), os.path.join(output_folder, 'depth_charts.json'))
    save_json(snap_counts.to_dict(orient="records"), os.path.join(output_folder, 'snap_counts.json'))
    save_json(passing_data.to_dict(orient="records"), os.path.join(output_folder, 'next_gen_stats_passing.json'))
    save_json(rushing_data.to_dict(orient="records"), os.path.join(output_folder, 'next_gen_stats_rushing.json'))
    save_json(receiving_data.to_dict(orient="records"), os.path.join(output_folder, 'next_gen_stats_receiving.json'))

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
