import json
import os
from datetime import datetime

import pandas as pd
from archive_reader import log, read_lines_zst


def load_existing_json_data(json_path: str) -> dict:
    # Load existing JSON if available, else create an empty dictionary
    if os.path.exists(json_path) and os.path.getsize(json_path) > 0:
        try:
            with open(json_path, "r") as file:
                subreddit_data = json.load(file)
        except json.JSONDecodeError:
            print("Warning: JSON file is corrupted. Initializing with empty data.")
            subreddit_data = {}  # Reset if file is corrupted
    else:
        print("First run detected. Creating a new JSON file.")
        subreddit_data = {}
    return subreddit_data


def update_subreddit_from_submissions_zst(
    input_file: str,
    subreddit_name: str,
    subreddit_data: dict,
    from_date: datetime,
    to_date: datetime,
    min_posts: int,
):
    if subreddit_name not in subreddit_data:
        subreddit_data[subreddit_name] = {}  # Initialize subreddit if not present

    file_size = os.stat(input_file).st_size
    created: datetime = datetime.now()
    matched_lines = 0
    bad_lines = 0
    total_lines = 0
    write_bad_lines = True
    for line, file_bytes_processed in read_lines_zst(input_file):
        total_lines += 1
        if total_lines % 100000 == 0:
            log.info(
                f"{created.strftime('%Y-%m-%d %H:%M:%S')} : {total_lines:,} : {matched_lines:,} : {bad_lines:,} : {file_bytes_processed:,}:{(file_bytes_processed / file_size) * 100:.0f}%"
            )

        try:
            obj = json.loads(line)
            user: str = obj['author']
            created = datetime.fromtimestamp(int(obj["created_utc"]))
            date = created.strftime("%Y-%m-%d")
            if created < from_date:
                continue
            if created > to_date:
                # Assuming that lines are sorted by date
                break

            if user == "[deleted]":
                continue  # Ignore deleted users

            if user not in subreddit_data[subreddit_name]:
                # New user: Add entry
                subreddit_data[subreddit_name][user] = {
                    # "postdates": [date],
                    "postfrequency": 1,
                }
            else:
                # subreddit_data[subreddit_name][user]["postdates"].append(date)
                subreddit_data[subreddit_name][user]["postfrequency"] += 1

        except (KeyError, json.JSONDecodeError) as err:
            bad_lines += 1
            if write_bad_lines:
                if isinstance(err, KeyError):
                    log.warning(f"Key is not in the object: {err}")
                elif isinstance(err, json.JSONDecodeError):
                    log.warning(f"Line decoding failed: {err}")
                log.warning(line)

    subreddit_data[subreddit_name] = {
        user: details
        for user, details in subreddit_data[subreddit_name].items()
        if details["postfrequency"] >= min_posts
    }


def extract_subreddit_submissions(
    subreddit_name: str,
    input_file: str,
    from_date: datetime,
    to_date: datetime,
    json_path: str | None = None,
    csv_output_dir: str = "output/csv/",
    min_posts=1,
):
    if json_path == "":
        json_path = None

    if json_path is not None:
        subreddit_data = load_existing_json_data(json_path)
    else:
        subreddit_data = {}

    update_subreddit_from_submissions_zst(
        input_file, subreddit_name, subreddit_data, from_date, to_date, min_posts
    )

    # Save updated JSON file
    if json_path is not None:
        with open(json_path, "w") as file:
            json.dump(subreddit_data, file, indent=4)

    if not os.path.exists(csv_output_dir):
        os.makedirs(csv_output_dir, exist_ok=True)
    df = pd.DataFrame(
        [
            [user, d["postfrequency"]]
            for user, d in subreddit_data[subreddit_name].items()
        ],
    )
    df.sort_values(by=0, ascending=True, inplace=True)
    df.to_csv(
        os.path.join(csv_output_dir, f"{subreddit_name}.csv"), header=False, index=False
    )

    print(f"Updated data for subreddit: {subreddit_name}")


if __name__ == "__main__":
    subreddits = pd.read_csv("data/sublist.csv", header=None)

    sublists = subreddits[0].tolist()  # Extract only subreddit names as a list
    print(sublists)

    # Better to compile the info of individual subs into a single file
    output_file = "./output/output"
    from_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    to_date = datetime.strptime("2024-12-31", "%Y-%m-%d")

    for subname in sublists:
        input_file = f"./data/archived_submissions/{subname}_submissions.zst"
        extract_subreddit_submissions(
            subname, input_file, from_date, to_date, "output/csv/"
        )
