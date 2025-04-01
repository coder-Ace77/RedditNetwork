import json
import logging.handlers
import os
from datetime import datetime
from logging import Logger

import pandas as pd
import zstandard


def config_logger() -> Logger:
    # sets up logging to the console as well as a file
    log = logging.getLogger("bot")
    log.setLevel(logging.INFO)
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
    log_str_handler = logging.StreamHandler()
    log_str_handler.setFormatter(log_formatter)
    log.addHandler(log_str_handler)
    if not os.path.exists("logs"):
        os.makedirs("logs")
    log_file_handler = logging.handlers.RotatingFileHandler(
        os.path.join("logs", "bot.log"), maxBytes=1024 * 1024 * 16, backupCount=5
    )
    log_file_handler.setFormatter(log_formatter)
    log.addHandler(log_file_handler)
    return log


log = config_logger()


def write_line_json(handle, obj):
    handle.write(json.dumps(obj))
    handle.write("\n")


def write_line_single(handle, obj, field):
    if field in obj:
        handle.write(obj[field])
    else:
        log.info(f"{field} not in object {obj['id']}")
    handle.write("\n")


def write_line_csv(writer, obj, is_submission):
    output_list = []
    output_list.append(str(obj["score"]))
    output_list.append(
        datetime.fromtimestamp(int(obj["created_utc"])).strftime("%Y-%m-%d")
    )
    if is_submission:
        output_list.append(obj["title"])
    output_list.append(f"u/{obj['author']}")
    if "permalink" in obj:
        output_list.append(f"https://www.reddit.com{obj['permalink']}")
    else:
        output_list.append(
            f"https://www.reddit.com/r/{obj['subreddit']}/comments/{obj['link_id'][3:]}/_/{obj['id']}"
        )
    if is_submission:
        if obj["is_self"]:
            if "selftext" in obj:
                output_list.append(obj["selftext"])
            else:
                output_list.append("")
        else:
            output_list.append(obj["url"])
    else:
        output_list.append(obj["body"])
    writer.writerow(output_list)


def read_and_decode(
    reader, chunk_size, max_window_size, previous_chunk=None, bytes_read=0
):
    chunk = reader.read(chunk_size)
    bytes_read += chunk_size
    if previous_chunk is not None:
        chunk = previous_chunk + chunk
    try:
        return chunk.decode()
    except UnicodeDecodeError:
        if bytes_read > max_window_size:
            raise UnicodeError(
                f"Unable to decode frame after reading {bytes_read:,} bytes"
            )
        log.info(f"Decoding error with {bytes_read:,} bytes, reading another chunk")
        return read_and_decode(reader, chunk_size, max_window_size, chunk, bytes_read)


def read_lines_zst(file_name: str):
    with open(file_name, "rb") as file_handle:
        buffer = ""
        reader = zstandard.ZstdDecompressor(max_window_size=2**31).stream_reader(
            file_handle
        )
        while True:
            chunk = read_and_decode(reader, 2**27, (2**29) * 2)

            if not chunk:
                break
            lines = (buffer + chunk).split("\n")

            for line in lines[:-1]:
                yield line.strip(), file_handle.tell()

            buffer = lines[-1]

        reader.close()


if __name__ == "__main__":
    subreddits = pd.read_csv("data/sublist.csv", header=None)

    sublists = subreddits[0].tolist()  # Extract only subreddit names as a list
    print(sublists)

    # Better to compile the info of individual subs into a single file
    output_file = "./output/output"
    from_date = datetime.strptime("2024-01-01", "%Y-%m-%d")
    to_date = datetime.strptime("2024-12-31", "%Y-%m-%d")

    for subname in sublists:
        # Replace it with a text file filled with subreddit names
        input_file = f"./data/archived_submissions/{subname}_submissions.zst"
