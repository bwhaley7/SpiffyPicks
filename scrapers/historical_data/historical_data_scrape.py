import nfl_data_py as nfl
import json
import traceback
import pandas as pd
import os
from dotenv import load_dotenv, find_dotenv
from pymongo import MongoClient

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()  # Convert Timestamp to ISO 8601 string
        return super().default(obj)
    
load_dotenv(find_dotenv())

# Access the MongoDB connection string from the environment variable
dataPath = os.getenv('DATA_PATH')
output_file = os.path.join(dataPath, 'historical_data.json')

# Define the years you want to pull data for
years = [2019, 2020, 2021, 2022, 2023]

try:
    # Fetch data using nfl_data_py
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

    # Consolidate all data into a dictionary of lists of records
    data = {
        "weekly_data": weekly_data.to_dict(orient="records"),
        "seasonal_data": seasonal_data.to_dict(orient="records"),
        "schedules": schedules.to_dict(orient="records"),
        "scoring_lines": scoring_lines.to_dict(orient="records"),
        "injuries": injuries.to_dict(orient="records"),
        "depth_charts": depth_charts.to_dict(orient="records"),
        "snap_counts": snap_counts.to_dict(orient="records"),
        "next_gen_stats_passing": passing_data.to_dict(orient="records"),
        "next_gen_stats_rushing": rushing_data.to_dict(orient="records"),
        "next_gen_stats_receiving": receiving_data.to_dict(orient="records")
    }

    with open(output_file, 'w') as json_file:
        json.dump(data, json_file, indent=4, cls=CustomJSONEncoder)

    print(f"Historical data downloaded to: {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")
    traceback.print_exc()
