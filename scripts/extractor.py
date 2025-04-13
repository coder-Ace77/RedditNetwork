import json
import os
from datetime import datetime
from typing import Dict

import pandas as pd
from archive_reader import log, read_lines_zst


def load_existing_json_data(json_path: str) -> Dict:
    if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
        try:
            with open(json_path, "r") as file:
                return json.load(file)
        except json.JSONDecodeError:
            log.warning("JSON file is corrupted. Initializing with empty data.")
    return {}


def update_subreddit_data(
    input_file: str,
    subreddit_name: str,
    subreddit_data: Dict,
    from_date: datetime,
    to_date: datetime,
    min_posts: int,
):
    if subreddit_name not in subreddit_data:
        subreddit_data[subreddit_name] = {}

    file_size = os.stat(input_file).st_size
    created = datetime.now()
    matched_lines = bad_lines = total_lines = 0

    for line, file_bytes_processed in read_lines_zst(input_file):
        total_lines += 1
        if total_lines % 100000 == 0:
            log.info(
                f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {total_lines:,} : {matched_lines:,} : "
                f"{bad_lines:,} : {file_bytes_processed:,}:{(file_bytes_processed / file_size) * 100:.0f}%"
            )

        try:
            obj = json.loads(line)
            user = obj['author']
            created = datetime.fromtimestamp(int(obj["created_utc"]))
            
            if created < from_date or created > to_date or user == "[deleted]":
                continue

            year = created.year
            year_key = f"posts_{year}"

            if user not in subreddit_data[subreddit_name]:
                subreddit_data[subreddit_name][user] = {
                    year_key: 1,
                    "total_posts": 1
                }
            else:
                subreddit_data[subreddit_name][user][year_key] = subreddit_data[subreddit_name][user].get(year_key, 0) + 1
                subreddit_data[subreddit_name][user]["total_posts"] += 1

            matched_lines += 1

        except (KeyError, json.JSONDecodeError) as err:
            bad_lines += 1
            log.warning(f"Error processing line: {err}")

    subreddit_data[subreddit_name]={
        user: details 
        for user, details in subreddit_data[subreddit_name].items()
        if details["total_posts"] >= min_posts
    }


def extract_subreddit_submissions(
    subreddit_name: str,
    input_file: str,
    from_date: datetime,
    to_date: datetime,
    json_path: str = None,
    csv_output_dir: str = "output/csv/",
    min_posts: int = 1,
):
    subreddit_data = load_existing_json_data(json_path) if json_path else {}

    update_subreddit_data(
        input_file, subreddit_name, subreddit_data, from_date, to_date, min_posts
    )

    if json_path:
        with open(json_path, "w") as file:
            json.dump(subreddit_data, file, indent=4)

    os.makedirs(csv_output_dir, exist_ok=True)
    save_year_wise_data(subreddit_data, subreddit_name, csv_output_dir)


def save_year_wise_data(subreddit_data: Dict, subreddit_name: str, output_dir: str):
    if subreddit_name not in subreddit_data:
        return

    year_columns = [f"posts_{year}" for year in range(2019,2025)]
    all_columns = ["username"] + year_columns + ["total_posts"]

    rows = []
    for user, data in subreddit_data[subreddit_name].items():
        row = {"username": user}
        for year_col in year_columns:
            row[year_col] = data.get(year_col, 0)
        row["total_posts"] = data["total_posts"]
        rows.append(row)
    

    df = pd.DataFrame(rows, columns=all_columns)
    df.sort_values(by="username", inplace=True)
    df.to_csv(os.path.join(output_dir, f"{subreddit_name}.csv"), index=False)
    log.info(f"Saved data for subreddit: {subreddit_name}")


if __name__ == "__main__":
    subreddits = pd.read_csv("data/sublist.csv", header=None)
    sublists = subreddits[0].tolist()

    from_date = datetime.strptime("2019-01-01", "%Y-%m-%d")
    to_date = datetime.strptime("2023-12-31", "%Y-%m-%d")

    for subname in sublists:
        input_file = f"/content/data/archived_submissions/{subname}_submissions.zst"
        extract_subreddit_submissions(
            subname, input_file, from_date, to_date
        )