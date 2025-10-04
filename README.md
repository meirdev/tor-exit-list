# Tor Exit List

Export a list of Tor exit nodes to CSV from [torproject.org](https://collector.torproject.org/archive/exit-lists/).


## Usage

```bash
uv run python main.py [-h] [--filename FILENAME] [--fileindex FILEINDEX]
```

## Example of Output

```csv
node,published,last_status,address
64D74AAA74F30DC2CFB36343CE5D4451B9A4DBA8,2025-10-03T22:01:58,2025-10-04T01:00:00,171.25.193.25
0DC16FEAA5A5E27A974009CBF7748BB6FAAE6DE1,2025-10-03T20:11:10,2025-10-04T01:00:00,80.67.167.81
...
```
