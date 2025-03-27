import pandas as pd
import json
import os
import networkx as nx

def update_json(subreddit_name, csv_path="./output/output.csv", json_path="./output/posts.json", graph_path="./output/graph.graphml", min_posts=1):
    
    # Check if CSV file exists and is non-empty
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        print("CSV file is empty or missing. Skipping processing.")
        return  # Stop execution if there's no data

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

    # Read CSV
    data = pd.read_csv(csv_path)

    # Extract required columns
    user_ids = data.iloc[:, 3]  # Usernames
    post_dates = data.iloc[:, 1]  # Post Dates

    # Convert post_dates to a list per user
    if subreddit_name not in subreddit_data:
        subreddit_data[subreddit_name] = {}  # Initialize subreddit if not present

    for user, date in zip(user_ids, post_dates):
        if user == "u/[deleted]":  
            continue  # Ignore deleted users

        if user not in subreddit_data[subreddit_name]:  
            # New user: Add entry
            subreddit_data[subreddit_name][user] = {"postdates": [date], "postfrequency": 1}
        else:
            # Existing user: Append date if it's not a duplicate
            if date not in subreddit_data[subreddit_name][user]["postdates"]:
                subreddit_data[subreddit_name][user]["postdates"].append(date)
                subreddit_data[subreddit_name][user]["postfrequency"] += 1

    subreddit_data[subreddit_name] = {
        user: details for user, details in subreddit_data[subreddit_name].items() 
        if details["postfrequency"] >= min_posts
    }

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
            print(f"Warning: Unable to load existing graph. Creating a new one. Error: {e}")
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

