import os
import subprocess
import shutil  # For moving files

def process_line():
    list_file = "./data/bulk/list.csv"
    sublist_file = "./data/sublist.csv"
    done_file = "./data/bulk/done.csv"
    output_folder = "./output"
    move_folder = "./placeholder"  # Replace 'placeholder' with the actual folder path

    if not os.path.exists(list_file) or os.stat(list_file).st_size == 0:
        print("list.csv is empty or does not exist.")
        return False

    with open(list_file, "r") as file:
        lines = file.readlines()

    if not lines:
        print("list.csv is empty.")
        return False

    # Check if the first file is already processed
    first_line = lines[0].strip()
    output_file = os.path.join(output_folder, f"{first_line}.csv")
    if os.path.exists(output_file):
        print(f"Skipping {first_line}.csv as it already exists in the output folder.")
        with open(list_file, "w") as file:
            file.writelines(lines[1:])  # Remove the first line
        return True

    with open(sublist_file, "w") as file:
        file.writelines(lines[:5])

    print(f"Moved line to {sublist_file}: {lines[0].strip()}")

    print("Running file_download.py...")
    subprocess.run(["python3", "./scripts/file_download.py"])

    print("Running extractor.py...")
    subprocess.run(["python3", "./scripts/extractor.py"])

    # Move the downloaded file to the specified folder
    downloaded_file = os.path.join(output_folder, f"{first_line}.csv")
    if os.path.exists(downloaded_file):
        destination = os.path.join(move_folder, f"{first_line}.csv")
        shutil.move(downloaded_file, destination)
        print(f"Moved {downloaded_file} to {destination}")
    else:
        print(f"Downloaded file {downloaded_file} not found.")

    with open(list_file, "w") as file:
        file.writelines(lines[5:])

    # Append the processed line to done.csv
    with open(done_file, "a") as file:
        file.writelines(lines[:5])

    # Clear sublist.csv
    open(sublist_file, "w").close()

    # Track progress
    total_done = sum(1 for _ in open(done_file))
    print(f"Progress: {total_done} files processed.")

    # Delete the .zsh file after extraction
    zsh_file = f"./data/archived_submissions/{lines[0]}_submissions.zst"
    if os.path.exists(zsh_file):
        os.remove(zsh_file)
        print(f"Deleted file: {zsh_file}")
    else:
        print(f"No .zsh file found to delete at {zsh_file}.")
    return True

while True:
    if not process_line():
        print("Processing complete. list.csv is empty.")
        break