import csv

def round_robin_to_csv(skip_rows, limit):
    with open('redits.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header
        data = [(row[0], float(row[1]), row[2]) for row in reader]

    sorted_data = sorted(data, key=lambda x: x[1])

    # Apply skip and limit
    processed_data = sorted_data[skip_rows:skip_rows + limit]

    lists = [[], [], [], []]
    for index, row in enumerate(processed_data):
        assigned_list = index % 4
        lists[assigned_list].append(row[0])
        print(f"Assigning row: {row} to list {assigned_list + 1}")

    for i, lst in enumerate(lists):
        filename = f"output_list_{i + 1}.csv"
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in lst:
                writer.writerow([row])  # wrap string in list
        print(f"Saved {len(lst)} rows to {filename}")

if __name__ == "__main__":
    skip_rows = int(input("Enter the number of rows to skip: "))
    limit = int(input("Enter the limit (total number of rows): "))

    round_robin_to_csv(skip_rows, limit)
