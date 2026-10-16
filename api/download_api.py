import os
import json
import csv

from io import StringIO

from flask import Blueprint
from flask import request
from flask import send_file

from datetime import datetime

from config import REPORT_DIR

download_api = Blueprint(
    "download_api",
    __name__
)

# ================= DOWNLOAD SINGLE DATE CSV ================= #

@download_api.route("/api/download")
def download_csv():

    date = request.args.get("date")

    file_path = os.path.join(
        REPORT_DIR,
        f"{date}.json"
    )

    if not os.path.exists(file_path):

        return "Report not found", 404

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    csv_file = f"{date}.csv"

    with open(
        csv_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "Serial No",
            "Timestamp",
            "IP Address",
            "Status"
        ])

        for row in data:

            writer.writerow([
                row["serial_no"],
                row["timestamp"],
                row["ip_address"],
                row["status"]
            ])

    return send_file(
        csv_file,
        as_attachment=True
    )

# ================= DOWNLOAD DATE RANGE CSV ================= #

@download_api.route("/api/download-range")
def download_range():

    start = request.args.get("start")
    end = request.args.get("end")

    start_date = datetime.strptime(
        start,
        "%Y-%m-%d"
    )

    end_date = datetime.strptime(
        end,
        "%Y-%m-%d"
    )

    combined = []

    for file in os.listdir(REPORT_DIR):

        if not file.endswith(".json"):
            continue

        file_date = file.replace(
            ".json",
            ""
        )

        current_date = datetime.strptime(
            file_date,
            "%Y-%m-%d"
        )

        if start_date <= current_date <= end_date:

            with open(
                os.path.join(REPORT_DIR, file),
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

                combined.extend(data)

    csv_file = "combined_report.csv"

    with open(
        csv_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as csvfile:

        writer = csv.writer(csvfile)

        writer.writerow([
            "Serial No",
            "Timestamp",
            "IP Address",
            "Status"
        ])

        for row in combined:

            writer.writerow([
                row["serial_no"],
                row["timestamp"],
                row["ip_address"],
                row["status"]
            ])

    return send_file(
        csv_file,
        as_attachment=True
    )