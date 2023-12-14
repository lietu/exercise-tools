import csv
from datetime import datetime

import rich
from typer import Typer

DATE_COL = "Date"
DT_FORMAT = "%Y-%m-%d %H:%M:%S"

app = Typer()


def to_dt(date_str) -> datetime:
    return datetime.strptime(date_str, DT_FORMAT)


def read_csv(src):
    rows = []
    first = None
    last = None

    try:
        with open(src, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            row: dict
            for row in reader:
                rows.append(row)
                dt = to_dt(row[DATE_COL])

                if not first or dt < first:
                    first = dt

                if not last or dt > last:
                    last = dt
    except FileNotFoundError:
        pass

    return rows, first, last


def write_csv(dst, rows):
    fields = rows[0].keys()

    with open(dst, newline="", mode="w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    rich.print(f"Wrote {len(rows)} rows of data to {dst}")


@app.command()
def calculate_total(src="Activities-latest.csv", dst="Activities.csv"):
    rows, old_first, old_last = read_csv(dst)
    new_rows, new_first, new_last = read_csv(src)

    rich.print(f"Updating {dst} from {src}")
    rich.print(f"Already have data from", old_first, "to", old_last)
    rich.print(f"Update has data from", new_first, "to", new_last)

    old_dates = [row[DATE_COL] for row in rows]

    updates = 0
    for new_row in new_rows:
        if new_row[DATE_COL] not in old_dates:
            dt = to_dt(new_row[DATE_COL])
            rich.print("Found update from", dt)
            rows.append(new_row)
            updates += 1

    rich.print(f"{updates} updates found")
    if updates > 0:
        rows.sort(key=lambda row: to_dt(row[DATE_COL]), reverse=True)
        write_csv(dst, rows)


if __name__ == "__main__":
    app()
