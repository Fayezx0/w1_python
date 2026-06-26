from pathlib import Path 
import csv

def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    """
    Read a CSV file and return a list of rows (dicts).
    Raises errors if file is not found or empty.
    """
    path = Path(path)
    # 1. Check if file exists before trying to open
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    # 2. Open and read
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    # 3. Check if empty
    if not rows:
        raise ValueError("CSV has no data rows")

    return rows