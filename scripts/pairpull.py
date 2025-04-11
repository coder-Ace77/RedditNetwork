import csv
import os
from itertools import combinations

def compute_projection_sorted(sub1_path, sub2_path):
    shared_weight_sum = 0
    degree1 = 0
    degree2 = 0

    with open(sub1_path, newline='', encoding='utf-8') as f1, open(sub2_path, newline='', encoding='utf-8') as f2:
        r1 = csv.reader(f1)
        r2 = csv.reader(f2)
        next(r1), next(r2)  # skip headers

        row1 = next(r1, None)
        row2 = next(r2, None)

        while row1 and row2:
            user1, weight1 = row1[0], float(row1[1])
            user2, weight2 = row2[0], float(row2[1])
            degree1 += weight1
            degree2 += weight2

            if user1 == user2:
                shared_weight_sum += min(weight1, weight2)
                row1 = next(r1, None)
                row2 = next(r2, None)
            elif user1 < user2:
                row1 = next(r1, None)
            else:
                row2 = next(r2, None)

        # Finish summing degrees
        while row1:
            degree1 += float(row1[1])
            row1 = next(r1, None)

        while row2:
            degree2 += float(row2[1])
            row2 = next(r2, None)

    norm_weight = shared_weight_sum / min(degree1, degree2) if min(degree1, degree2) > 0 else 0
    return shared_weight_sum, norm_weight

def generate_subreddit_projection(sublist_dir="output/csv", output_file="output/final_subreddit_graph.csv"):

    files = [f for f in os.listdir(sublist_dir) if f.endswith(".csv")]
    file_paths = [os.path.join(sublist_dir, f) for f in files]
    subreddit_names = [os.path.splitext(f)[0] for f in files]

    pairs = combinations(zip(subreddit_names, file_paths), 2)

    with open(output_file, "w", newline='', encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["Subreddit1", "Subreddit2", "SharedWeight", "NormalizedWeight"])

        for (name1, path1), (name2, path2) in pairs:
            shared, norm = compute_projection_sorted(path1, path2)
            if shared > 0:
                writer.writerow([name1, name2, round(shared, 3), round(norm, 4)])
                print(f"{name1} - {name2}: Shared = {shared:.1f}, Normalized = {norm:.4f}")

    print(f"\n Final graph written to '{output_file}'.")

generate_subreddit_projection()
