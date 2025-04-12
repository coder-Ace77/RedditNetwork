import csv
from itertools import combinations

input_file = "redits.csv"
output_file = "pairs.csv"

subreddits = []
with open(input_file, "r") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  
    for i, row in enumerate(reader):
        if i >= 10000:  
            break
        subreddits.append(row[0])  

pairs = list(combinations(subreddits, 2))

with open(output_file, "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Subreddit1", "Subreddit2"])  
    writer.writerows(pairs)  

print(f"Generated {len(pairs)} pairs and saved them to {output_file}.")