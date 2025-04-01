import json
import os
from datetime import datetime

import networkx as nx
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
    subreddit_name: str,
    subreddit_data: dict,
    from_date: datetime,
    to_date: datetime,
    min_posts: int,
):
    if subreddit_name not in subreddit_data:
        subreddit_data[subreddit_name] = {}  # Initialize subreddit if not present

    input_file = f"./data/archived_submissions/{subreddit_name}_submissions.zst"
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
            user = f"u/{obj['author']}"
            created = datetime.fromtimestamp(int(obj["created_utc"]))
            date = created.strftime("%Y-%m-%d")
            if created < from_date:
                continue
            if created > to_date:
                # Assuming that lines are sorted by date
                break

            if user == "u/[deleted]":
                continue  # Ignore deleted users

            if user not in subreddit_data[subreddit_name]:
                # New user: Add entry
                subreddit_data[subreddit_name][user] = {
                    "postdates": [date],
                    "postfrequency": 1,
                }
            else:
                # Existing user: Append date if it's not a duplicate
                # TODO: Why not increment postfrequency if date is duplicate?
                # TODO: Do we even need exact postdates
                # @RVNayan
                if date not in subreddit_data[subreddit_name][user]["postdates"]:
                    subreddit_data[subreddit_name][user]["postdates"].append(date)
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
        user: {
            "postdates": list(details["postdates"]),
            **{k: v for k, v in details.items() if k != "postdates"},
        }
        for user, details in subreddit_data[subreddit_name].items()
        if details["postfrequency"] >= min_posts
    }


def extract_subreddit_submissions(
    subreddit_name,
    from_date,
    to_date,
    json_path="./output/posts.json",
    graph_path="./output/graph.graphml",
    min_posts=1,
):
    subreddit_data = load_existing_json_data(json_path)

    update_subreddit_from_submissions_zst(
        subreddit_name, subreddit_data, from_date, to_date, min_posts
    )

    # Save updated JSON file
    with open(json_path, "w") as file:
        json.dump(subreddit_data, file, indent=4)

    print(f"Updated data for subreddit: {subreddit_name}")

    # Load existing graph if available, otherwise create a new graph
    if os.path.exists(graph_path) and os.path.getsize(graph_path) > 0:
        try:
            G = nx.read_graphml(graph_path)
            print("Existing graph loaded.")
        except Exception as e:
            print(
                f"Warning: Unable to load existing graph. Creating a new one. Error: {e}"
            )
            G = nx.Graph()
    else:
        print("No existing graph found. Creating a new one.")
        G = nx.Graph()

    # Add subreddit node if not already present
    if subreddit_name not in G:
        G.add_node(subreddit_name, bipartite=0, type="subreddit")

    # Add user nodes and edges (with minimum post threshold)
    for user, details in subreddit_data[subreddit_name].items():
        if details["postfrequency"] < min_posts:
            continue  # Ignore users with post count below threshold

        if user not in G:
            G.add_node(user, bipartite=1, type="user")

        if not G.has_edge(user, subreddit_name):  # Ensure user is the source
            G.add_edge(user, subreddit_name, weight=details["postfrequency"])
        else:
            G[user][subreddit_name]["weight"] += details["postfrequency"]

    # Export the updated graph
    nx.write_graphml(G, graph_path)
    print(f"Graph updated and exported to {graph_path}")


if __name__ == "__main__":
    subreddits = pd.read_csv("data/sublist.csv", header=None)

    sublists = subreddits[0].tolist()  # Extract only subreddit names as a list
    print(sublists)

    # Better to compile the info of individual subs into a single file
    output_file = "./output/output"
    from_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    to_date = datetime.strptime("2024-12-31", "%Y-%m-%d")

    for subname in sublists:
        # Replace it with a text file filled with subreddit names
        input_file = f"./data/archived_submissions/{subname}_submissions.zst"
        extract_subreddit_submissions(subname, from_date, to_date)
