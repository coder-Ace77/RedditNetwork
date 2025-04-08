import networkx as nx
import os
import csv

def extract_subreddits_from_graphml(graphml_file, output_file="output/subreddits_from_graph.csv"):
    if not os.path.exists(graphml_file):
        print("GraphML file not found.")
        return

    # Load the GraphML file using networkx
    G = nx.read_graphml(graphml_file)

    # Extract only subreddit nodes (type == 'subreddit')
    subreddit_names = []
    for node, data in G.nodes(data=True):
        if data.get("type") == "subreddit":
            subreddit = data.get("label") or data.get("name") or node
            subreddit_names.append(subreddit)

    # Remove duplicates and sort alphabetically
    subreddit_names = sorted(set(subreddit_names))

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Save to CSV
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Subreddit"])
        for name in subreddit_names:
            writer.writerow([name])

    print(f"Extracted {len(subreddit_names)} subreddits to '{output_file}'.")

# Example usage
extract_subreddits_from_graphml("output/graph.graphml")
