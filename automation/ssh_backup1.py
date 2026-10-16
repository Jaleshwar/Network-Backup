import json
import logging
import time
import paramiko
from datetime import datetime
import os
import csv
import sys
import re
import warnings

from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings(
    "ignore",
    category=CryptographyDeprecationWarning
)

# ================= CONSTANTS ================= #

DEFAULT_PORT = 22
TIMEOUT = 30
READ_TIMEOUT = 10

# ================= BASE DIRECTORY ================= #

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

BACKUP_BASE_DIR = os.path.join(
    BASE_DIR,
    "backups"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

CREDENTIAL_FILE = os.path.join(
    BASE_DIR,
    "credentials",
    "credentials.csv"
)

os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ================= DATE ================= #

CURRENT_DATE = datetime.now().strftime(
    "%Y-%m-%d"
)

CURRENT_TIMESTAMP = datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S"
)

JSON_REPORT_FILE = os.path.join(
    REPORT_DIR,
    f"{CURRENT_DATE}.json"
)

# ================= CLEAR JSON REPORT ================= #

with open(
    JSON_REPORT_FILE,
    "w",
    encoding="utf-8"
) as file:

    json.dump([], file)

# ================= LOGGER ================= #

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s - %(levelname)s - %(message)s",

    handlers=[

        logging.FileHandler(

            os.path.join(
                BASE_DIR,
                "ssh_command_execution.log"
            )
        ),

        logging.StreamHandler()
    ]
)

# ================= SELECTED IPS ================= #

selected_ips = []

if len(sys.argv) > 1:

    selected_ips = sys.argv[1].split(",")

# ================= NORMALIZE OUTPUT ================= #

def normalize_output(data):

    normalized_lines = []

    for line in data.splitlines():

        line = line.rstrip()

        line = re.sub(

            r'\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+(\.\d+)?\s+IST\s+\d{4}',

            '',

            line
        )

        if line.startswith("!Time:"):
            continue

        if "Current Time" in line:
            continue

        if "Last configuration change" in line:
            continue

        if "NVRAM config last updated" in line:
            continue

        if not line.strip():
            continue

        normalized_lines.append(line)

    return "\n".join(normalized_lines)

# ================= JSON REPORT ================= #

def update_json_report(
        serial_no,
        ip,
        ssh_status,
        config_status,
        interface_status,
        config_backup_status,
        interface_backup_status,
        config_backup_file,
        interface_backup_file,
        error_message=""
):

    current_date = datetime.now().strftime(
        "%d-%m-%Y %H:%M:%S"
    )

    new_entry = {

        "SNo": serial_no,

        "Timestamp": current_date,

        "IPAddress": ip,

        "SSHStatus": ssh_status,

        "ConfigCommandStatus": config_status,

        "InterfaceCommandStatus": interface_status,

        "ConfigBackupStatus": config_backup_status,

        "InterfaceBackupStatus": interface_backup_status,

        "ConfigBackupFile": config_backup_file,

        "InterfaceBackupFile": interface_backup_file,

        "Error": error_message
    }

    data = []

    if os.path.exists(JSON_REPORT_FILE):

        try:

            with open(
                JSON_REPORT_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

        except:

            data = []

    data.append(new_entry)

    with open(
        JSON_REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4
        )

# ================= SSH CLIENT ================= #

def create_ssh_client(ip, username, password):

    logging.info(f"Connecting to {ip}...")

    client = paramiko.SSHClient()

    client.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    transport = paramiko.Transport(
        (ip, DEFAULT_PORT)
    )

    security_options = transport.get_security_options()

    security_options.kex = [

        "diffie-hellman-group14-sha1",

        "diffie-hellman-group1-sha1",

        "diffie-hellman-group-exchange-sha1",

        "diffie-hellman-group-exchange-sha256"
    ]

    security_options.key_types = [

        "ssh-rsa",

        "ssh-dss",

        "ecdsa-sha2-nistp256",

        "ssh-ed25519"
    ]

    transport.connect(
        username=username,
        password=password
    )

    client._transport = transport

    logging.info(f"Connected to {ip}")

    return client

# ================= EXECUTE COMMAND ================= #

def execute_command(shell, command):

    output = ""

    while shell.recv_ready():

        shell.recv(65535)

    shell.send("terminal length 0\n")

    shell.send("terminal width 512\n")

    time.sleep(1)

    while shell.recv_ready():

        shell.recv(65535)

    shell.send(command + "\n")

    time.sleep(2)

    start_time = time.time()

    last_data_time = time.time()

    while True:

        if shell.recv_ready():

            chunk = shell.recv(65535).decode(

                "utf-8",

                errors="ignore"
            )

            output += chunk

            last_data_time = time.time()

        else:

            time.sleep(0.5)

        if time.time() - last_data_time > READ_TIMEOUT:

            break

        if time.time() - start_time > 300:

            break

    output = output.replace(
        '\r',
        ''
    )

    return output

# ================= SANITIZE COMMAND ================= #

def sanitize_command(command):

    return command.replace(
        " ",
        "_"
    ).replace(
        "/",
        "_"
    )

# ================= GET LATEST BACKUP ================= #

def get_latest_backup_file(command_backup_dir):

    if not os.path.exists(command_backup_dir):

        return None

    files = [

        os.path.join(
            command_backup_dir,
            file
        )

        for file in os.listdir(command_backup_dir)

        if file.endswith(".txt")
    ]

    if not files:

        return None

    files.sort(

        key=os.path.getmtime,

        reverse=True
    )

    return files[0]

# ================= COMPARE AND SAVE ================= #

def compare_and_save(
        ip,
        command,
        command_output
):

    command_folder = sanitize_command(command)

    ip_backup_dir = os.path.join(
        BACKUP_BASE_DIR,
        ip
    )

    command_backup_dir = os.path.join(
        ip_backup_dir,
        command_folder
    )

    os.makedirs(
        command_backup_dir,
        exist_ok=True
    )

    latest_backup_file = get_latest_backup_file(
        command_backup_dir
    )

    new_backup_file = os.path.join(

        command_backup_dir,

        f"{ip}_{command_folder}_{CURRENT_TIMESTAMP}.txt"
    )

    normalized_new_output = normalize_output(
        command_output
    )

    # ================= INITIAL BACKUP ================= #

    if latest_backup_file is None:

        with open(
            new_backup_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                normalized_new_output
            )

        logging.info(
            f"Initial backup created for {ip} - {command}"
        )

        return (
            "Initial Backup Created",
            new_backup_file
        )

    # ================= READ OLD BACKUP ================= #

    with open(
        latest_backup_file,
        "r",
        encoding="utf-8"
    ) as f:

        old_output = normalize_output(
            f.read()
        )

    # ================= DIFFERENCE FOUND ================= #

    if old_output != normalized_new_output:

        with open(
            new_backup_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                normalized_new_output
            )

        logging.info(
            f"Difference found for {ip} - {command}"
        )

        return (
            "Difference Found",
            new_backup_file
        )

    # ================= NO DIFFERENCE ================= #

    logging.info(
        f"No difference found for {ip} - {command}"
    )

    return (
        "No Difference Found",
        ""
    )

# ================= READ CSV ================= #

def read_csv_and_connect(file_path):

    with open(
        file_path,
        mode='r'
    ) as file:

        reader = csv.DictReader(file)

        serial_no = 1

        for row in reader:

            ip = row.get(
                'IpAddress'
            ) or row.get('ip')

            # ================= FILTER IPS ================= #

            if selected_ips:

                if "ALL" not in selected_ips:

                    if ip not in selected_ips:

                        continue

            username = row.get(
                'UserName'
            ) or row.get('username')

            password = row.get(
                'Password'
            ) or row.get('password')

            # ================= DYNAMIC COMMANDS ================= #

            commands = []

            for key, value in row.items():

                if key.lower().startswith("command") and value:

                    commands.append(
                        value.strip()
                    )

            # ================= VALIDATION ================= #

            if not ip or not username or not password:

                logging.warning(
                    f"Skipping row: {row}"
                )

                continue

            # ================= SSH CONNECTION ================= #

            try:

                client = create_ssh_client(

                    ip,
                    username,
                    password
                )

                ssh_status = "Success"

                shell = client.invoke_shell()

                time.sleep(3)

            except Exception as ssh_error:

                logging.error(
                    f"SSH Failed for {ip}: {ssh_error}"
                )

                update_json_report(

                    serial_no=serial_no,

                    ip=ip,

                    ssh_status="Failed",

                    config_status="Failed",

                    interface_status="Failed",

                    config_backup_status="Failed",

                    interface_backup_status="Failed",

                    config_backup_file="",

                    interface_backup_file="",

                    error_message=str(ssh_error)
                )

                serial_no += 1

                continue

            # ================= EXECUTE COMMANDS ================= #

            try:

                config_status = ""
                interface_status = ""

                config_backup_status = ""
                interface_backup_status = ""

                config_backup_file = ""
                interface_backup_file = ""

                for command in commands:

                    try:

                        logging.info(
                            f"Executing '{command}' on {ip}"
                        )

                        output = execute_command(
                            shell,
                            command
                        )

                        if not output.strip():

                            raise Exception(
                                "Empty command output received"
                            )

                        backup_status, backup_file = compare_and_save(

                            ip,
                            command,
                            output
                        )

                        # ================= SHOW RUN ================= #

                        if command.lower() == "show run":

                            config_status = backup_status

                            config_backup_status = backup_status

                            config_backup_file = backup_file

                        # ================= SHOW INTERFACES ================= #

                        elif command.lower() == "show interfaces":

                            interface_status = backup_status

                            interface_backup_status = backup_status

                            interface_backup_file = backup_file

                    except Exception as cmd_error:

                        logging.error(
                            f"Command Failed on {ip} - {command}: {cmd_error}"
                        )

                # ================= SINGLE JSON ENTRY ================= #

                update_json_report(

                    serial_no=serial_no,

                    ip=ip,

                    ssh_status=ssh_status,

                    config_status=config_status,

                    interface_status=interface_status,

                    config_backup_status=config_backup_status,

                    interface_backup_status=interface_backup_status,

                    config_backup_file=os.path.basename(
                        config_backup_file
                    ) if config_backup_file else "",

                    interface_backup_file=os.path.basename(
                        interface_backup_file
                    ) if interface_backup_file else "",

                    error_message=""
                )

                client.close()

            except Exception as main_error:

                logging.error(
                    f"Main execution failed for {ip}: {main_error}"
                )

            serial_no += 1

# ================= MAIN ================= #

if __name__ == "__main__":

    logging.info(
        "========== BACKUP PROCESS STARTED =========="
    )

    read_csv_and_connect(
        CREDENTIAL_FILE
    )

    logging.info(
        "========== BACKUP PROCESS COMPLETED =========="
    )