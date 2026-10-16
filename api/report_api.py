import os
import json

from flask import Blueprint
from flask import jsonify
from flask import request

from config import REPORT_DIR

report_api = Blueprint(
    "report_api",
    __name__
)

# ================= GET REPORT BY DATE ================= #

@report_api.route("/api/report")
def get_report():

    date = request.args.get("date")

    if not date:

        return jsonify({
            "status": "error",
            "message": "Date parameter missing"
        }), 400

    file_path = os.path.join(
        REPORT_DIR,
        f"{date}.json"
    )

    if not os.path.exists(file_path):

        return jsonify({
            "status": "error",
            "message": "Report not found"
        }), 404

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return jsonify(data)

# ================= GET ALL REPORT DATES ================= #

@report_api.route("/api/reports")
def get_reports():

    reports = []

    for file in os.listdir(REPORT_DIR):

        if file.endswith(".json"):

            reports.append(
                file.replace(".json", "")
            )

    reports.sort(reverse=True)

    return jsonify(reports)