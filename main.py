import argparse
import csv
import io
import re
import sys
import tarfile
from dataclasses import dataclass
from datetime import datetime
from os import PathLike

import requests


TOR_EXIT_LIST_URL = "https://collector.torproject.org/archive/exit-lists/"

TOR_EXIT_FILENAME = "exit-list-{year}-{month:02}.tar.xz"


RE_EXIT = re.compile(
    r"ExitNode\s*(?P<exit_node>[^\n\r]+)\s*"
    r"Published\s*(?P<published>[^\n\r]+)\s*"
    r"LastStatus\s*(?P<last_status>[^\n\r]+)\s*"
    r"ExitAddress\s*(?P<exit_address>[^\s]+)",
    re.MULTILINE | re.DOTALL | re.IGNORECASE,
)


@dataclass
class Exit:
    node: str
    published: datetime
    last_status: datetime
    adddress: str


def extract_nodes(file: bytes) -> list[Exit]:
    exits = []

    for exit_node, published, last_status, exit_address in RE_EXIT.findall(
        file.decode()
    ):
        exits.append(
            Exit(
                node=exit_node,
                published=datetime.strptime(published, "%Y-%m-%d %H:%M:%S"),
                last_status=datetime.strptime(last_status, "%Y-%m-%d %H:%M:%S"),
                adddress=exit_address,
            )
        )

    return exits


def extract_file(path: PathLike) -> dict[str, list[Exit]]:
    files = []

    if isinstance(path, io.BytesIO):
        fileobj, name = path, None
    else:
        fileobj, name = None, path

    with tarfile.open(name=name, fileobj=fileobj) as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue

            data = tar.extractfile(member).read()

            files.append((member.name, extract_nodes(data)))

    return dict(sorted(files, key=lambda i: i[0]))


def main():
    current_date = datetime.now()

    filename = TOR_EXIT_FILENAME.format(
        year=current_date.year, month=current_date.month
    )

    arg_parser = argparse.ArgumentParser(
        description="Download and parse the latest Tor exit node list."
    )
    arg_parser.add_argument(
        "--filename",
        type=str,
        default=filename,
        help=f"Name of the file to download (default: {filename}).",
    )
    arg_parser.add_argument(
        "--fileindex",
        type=int,
        default=-1,
        help="Index of the file to extract from the archive (default: -1 for last file).",
    )

    args = arg_parser.parse_args()

    url = TOR_EXIT_LIST_URL + args.filename

    response = requests.get(url)
    response.raise_for_status()

    file = io.BytesIO(response.content)

    files = extract_file(file)

    writer = csv.writer(sys.stdout)
    writer.writerow(["node", "published", "last_status", "address"])

    files_values = list(files.values())

    for exit_node in files_values[args.fileindex]:
        writer.writerow(
            [
                exit_node.node,
                exit_node.published.isoformat(),
                exit_node.last_status.isoformat(),
                exit_node.adddress,
            ]
        )


if __name__ == "__main__":
    main()
