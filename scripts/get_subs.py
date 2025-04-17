import os
import csv

def write_filenames_to_csv(directory, output_csv):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"Error: Directory '{directory}' does not exist.")
        return

    # Get all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Remove extensions from filenames
    filenames_without_extension = [os.path.splitext(f)[0] for f in files]

    # Write filenames to a CSV file
    with open(output_csv, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Filename"])  # Write header
        for filename in filenames_without_extension:
            writer.writerow([filename])

    print(f"File names written to '{output_csv}' successfully.")

# Example usage
if __name__ == "__main__":
    directory = "./hash"  # Replace with your directory path
    output_csv = "file_list.csv"  # Output CSV file
    write_filenames_to_csv(directory, output_csv)