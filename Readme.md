
# Reddit Network Analysis

## Prerequisites

- Python >= 3.9
- Install dependencies from `pyproject.toml`

## Getting data

Run `scripts/main.py`

### Command-line Arguments

You can provide the following arguments when running the script:

- **`--file`**: Path to a CSV file containing a list of subreddits. Each subreddit should be on a separate line.
  - Example: `--file subreddits.csv`
- **`--json-output`**: Path where the JSON output will be saved. The default is `output.json`.
  - Example: `--json-output results.json`
- **`--graph-output`**: Path where the GraphML output will be saved. The default is `output.graphml`.
  - Example: `--graph-output results.graphml`
- **`--torrent-file`**: Path to the Reddit data torrent file. The default is `reddit.torrent`.
  - Example: `--torrent-file reddit_data.torrent`
- **`--download-dir`**: Directory to store downloaded datasets. The default is `./data/archived_submissions/`.
  - Example: `--download-dir ./data/reddit_submissions/`
- **`--post-threshold`**: Minimum number of posts for a user to be considered. Default is `1`.
  - Example: `--post-threshold 5`
- **`--from-date`**: Start date in `'YYYY-MM-DD'` format. Default is `2020-01-01`.
  - Example: `--from-date 2021-01-01`
- **`--to-date`**: End date in `'YYYY-MM-DD'` format. Default is `2023-12-31`.
  - Example: `--to-date 2022-12-31`
- **`values`**: A list of subreddits to process. If this argument is not provided, the script expects a CSV file as input via `--file`.

### Example Usage

```bash
python scripts/main.py --file subreddits.csv --json-output results.json --graph-output results.graphml --torrent-file reddit_data.torrent --download-dir ./data/archived_submissions/ --post-threshold 5 --from-date 2021-01-01 --to-date 2022-12-31
```

Or, you can directly provide subreddits as command-line arguments:

```bash
python scripts/main.py --json-output results.json --graph-output results.graphml --post-threshold 5 --from-date 2024-01-01 --to-date 2024-12-31 subreddit1 subreddit2 subreddit3
```

#### With default options

```bash
python scripts/main.py --file subreddits.csv
```

```bash
python scripts/main.py subreddit1 subreddit2 subreddit3
```

If neither `--file` nor `values` is provided, the script will output an error message.

### Output Files

- **JSON Output**: A JSON file containing the extracted subreddit data, user
  activity, and other processed information.
- **GraphML Output**: A GraphML file representing the subreddit interactions,
  users, and posts.

## Merging files

- If you have multiple `json` `graphml` files and want to merge them, change their names and list them in [graphml_files.csv](utils/graphml_files.csv) and run this [code](utils/mergegml.py). Move these renamed files to utils folder

## References

[Link to Available Sublist](https://docs.google.com/spreadsheets/d/1KMybtp6lWoG154eiNmh-FWVlCs40z8NnljzhYfHPM2c/edit?gid=952481735#gid=952481735)

[Link to Doc](https://docs.google.com/document/d/1GeB1Ji9qhLvGSaW175c7pY75rD81mBwAudBi1SpCxBg/edit?tab=t.1687nqsr0gjy)

[Top Subreddits list by members](https://docs.google.com/spreadsheets/d/1E5PU18h8G-GGRYponNVJ_Crhu5LkyEnOXQr7Vie353A/edit?usp=sharing)

[FinaList](https://docs.google.com/spreadsheets/d/1oT-zug2Rv-x4MXzl_3ykpTg8_wSVj2f8ZTKANL40TSc/edit?usp=sharing)
