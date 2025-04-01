import libtorrent as lt
import time
import csv
import os
import shutil

# Read partial file names from CSV
csv_file = "Scripts/sublist.csv"
wanted_files = set()

with open(csv_file, newline="") as file:
    reader = csv.reader(file)
    for row in reader:
        wanted_files.add(row[0].strip().lower())

# Define torrent paths
torrent_path = "reddit.torrent"
download_dir = "./subreddits24"  # Custom download directory


os.makedirs(download_dir, exist_ok=True)

torrent_info = lt.torrent_info(torrent_path)


session = lt.session()
params = {
    "save_path": download_dir,  # Force all files into this folder
    "storage_mode": lt.storage_mode_t.storage_mode_sparse,
}
torrent_handle = session.add_torrent({"ti": torrent_info, **params})

# Disable all files initially
torrent_handle.prioritize_files([0] * torrent_info.num_files())

# Selectively enable files based on partial matches and pre-check if they exist
file_storage = torrent_info.files()
selected_indices = []

for idx in range(torrent_info.num_files()):
    file_path = file_storage.file_path(idx).lower()

    # Extract only the filename (ignore folder structure)
    filename = os.path.basename(file_path)

    # Check if file matches any entry in the CSV
    for partial_name in wanted_files:
        if f"{partial_name}_submissions.zst" == filename:
            full_path = os.path.join(download_dir, filename)

            # Skip if the file is already downloaded
            if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                print(f"Skipping (already exists): {filename}")
            else:
                torrent_handle.file_priority(idx, 1)  # Enable download
                selected_indices.append((idx, filename))
                print(f"Selected for download: {filename}")

if not selected_indices:
    print("No new matching files found. Exiting.")
    exit()

# Start downloading
print(f"Downloading {len(selected_indices)} selected files...")

while True:
    s = torrent_handle.status()
    file_progress = torrent_handle.file_progress()

    # Check if all selected files are fully downloaded
    if all(
        file_progress[idx] >= file_storage.file_size(idx) for idx, _ in selected_indices
    ):
        print("\nAll selected files downloaded. Stopping torrent...")
        session.remove_torrent(torrent_handle)  # Removes torrent but keeps files
        break

    # Print progress
    progress = s.progress * 100
    print(f"Progress: {progress:.2f}% - Downloaded {s.total_done} bytes", end="\r")
    time.sleep(5)

# **Move files to the final location (flatten the structure)**
for idx, filename in selected_indices:
    # Find the actual downloaded file path
    subdir_file_path = os.path.join(download_dir, file_storage.file_path(idx))
    final_path = os.path.join(download_dir, filename)

    # Move only if it exists in a subdirectory
    if os.path.exists(subdir_file_path) and subdir_file_path != final_path:
        shutil.move(subdir_file_path, final_path)  # Move the file
        print(f"Moved: {subdir_file_path} -> {final_path}")

# **Remove any leftover empty folders inside Download/**
for root, dirs, files in os.walk(download_dir, topdown=False):
    for d in dirs:
        dir_path = os.path.join(root, d)
        if not os.listdir(dir_path):  # If folder is empty
            os.rmdir(dir_path)

print("All files moved to:", download_dir)
