import os
import csv
import itertools
import concurrent.futures
from collections import defaultdict

# Read all subreddit files into memory
def load_sublist_data(folder_path):
    sublists = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            subreddit = filename.replace(".csv", "")
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                users = [row[0] for row in reader if row]
                users.sort()  # ensure it's sorted
                sublists.append((subreddit, users))
    return sublists

# Compute connection strength between two subreddits
def compute_pair(pair):
    (sub1, users1), (sub2, users2) = pair

    # Two-pointer approach
    i = j = common = 0
    while i < len(users1) and j < len(users2):
        if users1[i] == users2[j]:
            # print(sub1, sub2, users1[i]) # printing the common users for verification
            common += 1
            i += 1
            j += 1
        elif users1[i] < users2[j]:
            i += 1
        else:
            j += 1

    if common > 0:
        weight = common # Common users
        return (sub1, sub2, round(weight, 6))
    return None

# Process in parallel
def process_all(folder_path="output/csv", output_csv="output/subreddit_projection.csv", workers=8):
    sublists = load_sublist_data(folder_path)
    pairs = list(itertools.combinations(sublists, 2))

    print(f"Processing {len(pairs):,} subreddit pairs with {workers} workers...")

    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for res in executor.map(compute_pair, pairs, chunksize=5000):
            if res:
                results.append(res)

    # Save to output CSV
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Subreddit1", "Subreddit2", "Common"])
        writer.writerows(results)

    print(f"Finished. {len(results):,} connections saved to {output_csv}")


process_all()
