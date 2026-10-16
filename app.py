import sys
import csv
import subprocess
import io
import json
import os
from flask import send_file
from flask import jsonify
from api.auth_api import auth_api
from flask import (
    Flask,
    render_template,
    session,
    redirect,
    request)


app = Flask(__name__)
app.secret_key = "networkautomation"
app.register_blueprint(auth_api)


@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


@app.route("/get-devices")
def get_devices():
    devices = []
    with open("credentials/credentials.csv","r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ip = row.get("IpAddress")
            if ip:
                devices.append(ip)
    return jsonify(devices)


@app.route("/run-script", methods=["POST"])
def run_script():
    data = request.get_json()
    ips = data.get("ips", [])
    try:
        if "ALL" in ips:
            subprocess.Popen(
                [sys.executable, "automation/ssh_backup.py"])
            return {
                "message": "Automation started for ALL devices"}
        else:
            subprocess.Popen([
                    sys.executable,
                    "automation/ssh_backup.py",
                    ",".join(ips)])
            return {
                "message": f"Automation started for {ips}"}
    except Exception as e:
        return {"message": str(e)}


@app.route("/api/report")
def api_report():
    date = request.args.get("date")
    report_file = os.path.join("reports", f"{date}.json")
    if not os.path.exists(report_file):
        return jsonify([])
    with open(report_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    return jsonify(data)


@app.route("/api/download")
def download_csv():
    date = request.args.get("date")
    report_file = os.path.join("reports", f"{date}.json")
    if not os.path.exists(report_file):
        return {"message": "Report not found"}, 404
    with open(report_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "SNo",
        "Timestamp",
        "IPAddress",
        "SSHStatus",
        "ConfigCommandStatus",
        "InterfaceCommandStatus",
        "ConfigBackupStatus",
        "InterfaceBackupStatus",
        "ConfigBackupFile",
        "InterfaceBackupFile",
        "Error"
    ])

    for row in data:
        writer.writerow([
            row.get("SNo", ""),
            row.get("Timestamp", ""),
            row.get("IPAddress", ""),
            row.get("SSHStatus", ""),
            row.get("ConfigCommandStatus", ""),
            row.get("InterfaceCommandStatus", ""),
            row.get("ConfigBackupStatus", ""),
            row.get("InterfaceBackupStatus", ""),
            row.get("ConfigBackupFile", ""),
            row.get("InterfaceBackupFile", ""),
            row.get("Error", "")
        ])

    memory_file = io.BytesIO()
    memory_file.write(
        output.getvalue().encode("utf-8"))
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{date}.csv")


@app.route("/api/download-range")
def download_range_csv():
    start = request.args.get("start")
    end = request.args.get("end")
    report_dir = "reports"
    combined_data = []
    for file_name in os.listdir(report_dir):
        if not file_name.endswith(".json"):
            continue
        file_date = file_name.replace(".json", "")
        if start <= file_date <= end:
            file_path = os.path.join(
                report_dir,
                file_name)
            with open(
                    file_path,
                    "r",
                    encoding="utf-8"
            ) as file:
                data = json.load(file)
                combined_data.extend(data)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "SNo",
        "Timestamp",
        "IPAddress",
        "SSHStatus",
        "ConfigCommandStatus",
        "InterfaceCommandStatus",
        "ConfigBackupStatus",
        "InterfaceBackupStatus",
        "ConfigBackupFile",
        "InterfaceBackupFile",
        "Error"])
    for row in combined_data:
        writer.writerow([
            row.get("SNo"),
            row.get("Timestamp"),
            row.get("IPAddress"),
            row.get("SSHStatus"),
            row.get("ConfigCommandStatus"),
            row.get("InterfaceCommandStatus"),
            row.get("ConfigBackupStatus"),
            row.get("InterfaceBackupStatus"),
            row.get("ConfigBackupFile"),
            row.get("InterfaceBackupFile"),
            row.get("Error")])
    memory_file = io.BytesIO()
    memory_file.write(
        output.getvalue().encode("utf-8"))
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="text/csv",
        as_attachment=True,
        download_name=f"{start}_to_{end}.csv")


#####Schedular
@app.route(
    "/schedule-task",
    methods=["POST"])
def schedule_task():
    data = request.get_json()
    schedule_type = data.get("type")
    schedule_time = data.get("time")

    task_name = "NetworkAutomationBackup"
    python_path = sys.executable
    script_path = os.path.join(
        os.getcwd(),
        "automation",
        "ssh_backup.py")
    command = f'"{python_path}" "{script_path}"'
    try:
        subprocess.run(
            f'schtasks /Delete /TN "{task_name}" /F',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        create_command = (
            f'schtasks /Create '
            f'/SC {schedule_type} '
            f'/TN "{task_name}" '
            f'/TR "{command}" '
            f'/ST {schedule_time} '
            f'/F')
        subprocess.run(
            create_command,
            shell=True,
            check=True)
        return {
            "message":
               f"Task scheduled {schedule_type} at {schedule_time}"}
    except Exception as e:
        return {
            "message": str(e)}, 500


if __name__ == "__main__":
    app.run(debug=True)
