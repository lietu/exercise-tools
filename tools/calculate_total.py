import csv
from datetime import datetime, timedelta

import rich
from humanize import precisedelta, naturaldelta
from typer import Typer

from settings import conf

COLUMNS = [
    "Activity Type",
    "Date",
    "Favorite",
    "Title",
    "Distance",
    "Calories",
    "Total Time",
    "Avg HR",
    "Max HR",
    "Aerobic TE",
    "Avg Bike Cadence",
    "Max Bike Cadence",
    "Max Speed",
    "Total Descent",
    "Avg Stride Length",
    "Avg Vertical Ratio",
    "Avg Vertical Oscillation",
    "Avg Ground Contact Time",
    "Training Stress Score®",
    "Avg Power",
    "Max Power",
    "Grit",
    "Flow",
    "Avg. Swolf",
    "Avg Stroke Rate",
    "Total Reps",
    "Total Sets",
    "Dive Time",
    "Min Temp",
    "Surface Interval",
    "Decompression",
    "Best Lap Time",
    "Number of Laps",
    "Max Temp",
    "Moving Time",
    "Elapsed Time",
    "Min Elevation",
    "Max Elevation",
]

_ = COLUMNS

DATE_COL = "Date"
CALORIES_COL = "Calories"
TOTAL_TIME_COL = "Total Time"
TIME_COL = "Time"
AVG_HR_COL = "Avg HR"
DT_FORMAT = "%Y-%m-%d %H:%M:%S"
DAY_SECONDS = 60 * 60 * 24

app = Typer()


@app.command()
def calculate_total(src="Activities.csv"):
    filter_before = datetime.strptime(conf.FILTER_BEFORE, DT_FORMAT)
    last_dt = None
    first_dt = None
    total_sec = 0
    hr_tot = 0
    rows = 0
    calories_tot = 0

    with open(src, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        row: dict
        for row in reader:
            dt = datetime.strptime(row[DATE_COL], DT_FORMAT)
            if dt < filter_before:
                continue

            first_dt = dt
            if not last_dt:
                last_dt = dt

            rows += 1

            try:
                dt_tot = datetime.strptime(
                    row[TOTAL_TIME_COL], "%H:%M:%S"
                )  # Works for <= 24h
            except ValueError:
                try:
                    dt_tot = datetime.strptime(
                        row[TIME_COL], "%H:%M:%S"
                    )  # Works for <= 24h
                except ValueError:
                    rich.print("Skipping", row)
                    continue

            delta = timedelta(
                hours=dt_tot.hour, minutes=dt_tot.minute, seconds=dt_tot.second
            )
            delta_sec = delta.total_seconds()
            total_sec += delta_sec
            hr_tot += int(row[AVG_HR_COL]) * delta_sec
            calories_tot += int(row[CALORIES_COL])

    hr_avg = hr_tot / total_sec

    first_dt_start = first_dt.replace(hour=0, minute=0, second=0)
    last_dt_end = last_dt.replace(hour=23, minute=59, second=59)

    first_last = last_dt_end - first_dt_start
    total_delta = timedelta(seconds=total_sec)
    days = round(first_last.total_seconds() / DAY_SECONDS)
    per_day = timedelta(seconds=total_sec / days)
    per_week = timedelta(seconds=total_sec / days * 7)

    rich.print("Data from", days, "days")
    rich.print(first_dt, "to", last_dt)
    print("")
    rich.print("Total exercise:", precisedelta(total_delta))
    rich.print("Per day:", naturaldelta(per_day))
    rich.print(
        "Per week:",
        naturaldelta(per_week),
        "or",
        round(per_week.total_seconds() / 60.0),
        "minutes",
    )
    print("")
    rich.print(f"Estimated total calories: {calories_tot:.0f} kcal")
    rich.print(f"Per day: {calories_tot / days:.0f} kcal")
    print("")
    rich.print(f"HR Avg: {hr_avg:.1f} BPM")
    print("")


if __name__ == "__main__":
    app()
