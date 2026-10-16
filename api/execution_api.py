import subprocess
import sys
from flask import Blueprint
from flask import jsonify

execution_api = Blueprint(
    "execution_api",
    __name__
)

@execution_api.route("/run-script")
def run_script():

    try:

        subprocess.Popen([
            sys.executable,
            "automation/ssh_backup.py"
        ])

        return jsonify({
            "status": "success",
            "message": "Automation Started"
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        })