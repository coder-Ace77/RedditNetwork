import argparse
import sys
from datetime import datetime

import pandas as pd
from extractor import extract_subreddit_submissions
from file_download import dump_subreddit_submissions


def main():
    parser = argparse.ArgumentParser(
        description="Read arguments from a file or a list of subreddits."
    )
    parser.add_argument(
        "--file",
        type=str,
        help="CSV file containing sublist of subreddits",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        help="JSON output location",
        default="",
    )
    parser.add_argument(
        "--csv-output-dir",
        type=str,
        help="CSV output location",
        default="output/csv/",
    )
    parser.add_argument(
        "--torrent-file",
        type=str,
        help="Location of the reddit data torrent file",
        default="reddit.torrent",
    )
    parser.add_argument(
        "--download-dir",
        type=str,
        help="Directory to store downloaded datasets",
        default="./data/archived_submissions/",
    )
    parser.add_argument(
        "--post-threshold",
        default=1,
        type=int,
        help="Minimum number of posts to consider user",
    )
    parser.add_argument(
        "--from-date",
        type=str,
        default="2020-01-01",
        help="Date string in 'YYYY-MM-DD' format",
    )
    parser.add_argument(
        "--to-date",
        default="2023-12-31",
        type=str,
        help="Date string in 'YYYY-MM-DD' format",
    )
    parser.add_argument("values", nargs="*", help="List of subreddits to process")

    args = parser.parse_args()
    subreddits = []

    # If a file is provided, read the CSV file and get the list of subreddits
    if args.file:
        try:
            df = pd.read_csv(args.file, names=["subs"])
            subreddits = [sub.strip().lower() for sub in df["subs"]]

        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error while reading the file: {e}", file=sys.stderr)
            sys.exit(1)

    # If there are values provided via command line arguments, extend the list
    if args.values:
        subreddits.extend([v.strip().lower() for v in args.values])

    # If neither file nor values were provided, print an error
    if not subreddits:
        print(
            "No subreddits provided. Either pass a CSV file or a list of subreddits.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Print the subreddits to be processed
    print(f"Processing the following subreddits: {subreddits}")

    json_path = args.json_output
    csv_output_dir = args.csv_output_dir
    download_dir = args.download_dir
    torrent_path = args.torrent_file

    try:
        from_date = datetime.strptime(args.from_date, "%Y-%m-%d")
        to_date = datetime.strptime(args.to_date, "%Y-%m-%d")
        print(f"\tfrom: {from_date}\n\tto: {to_date}")
    except ValueError:
        print("Error: Invalid date format. Please use 'YYYY-MM-DD'.", file=sys.stderr)
        sys.exit(1)

    print("-" * 40)
    print("Downloading...")
    dumped_data_paths = dump_subreddit_submissions(
        subreddits, download_dir, torrent_path
    )
    failed_downloads = set(subreddits) - set(dumped_data_paths.keys())
    if len(failed_downloads) > 0:
        print(f"Failed to download {failed_downloads}")
    print("-" * 40)

    for sub in dumped_data_paths:
        print(f"Processing {sub}...")
        extract_subreddit_submissions(
            subreddit_name=sub,
            input_file=dumped_data_paths[sub],
            from_date=from_date,
            to_date=to_date,
            json_path=json_path,
            csv_output_dir=csv_output_dir,
            min_posts=args.post_threshold,
        )
        print("-" * 40)


if __name__ == "__main__":
    main()
