# import json
# import logging
# import time
# import paramiko
# from datetime import datetime
# import os
# import csv
# import sys
#
# DEFAULT_PORT = 22
# TIMEOUT = 10
# READ_TIMEOUT = 3
#
# # ================= DIRECTORIES ================= #
#
# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# BASE_DIR = r"C:\\Users\\Jaleshwar\\PycharmProjects\\NetworkAutomationBackUp\\"
# # BASE_DIR = os.path.abspath(__file__)
#
# BACKUP_BASE_DIR = os.path.join(
#     BASE_DIR,
#     "backups"
# )
#
# REPORT_DIR = os.path.join(
#     BASE_DIR,
#     "reports"
# )
# print(REPORT_DIR)
# CREDENTIAL_FILE = os.path.join(
#     BASE_DIR,
#     "credentials/credentials.csv"
# )
#
# os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
# os.makedirs(REPORT_DIR, exist_ok=True)
#
# # ================= DATE ================= #
#
# CURRENT_DATE = datetime.now().strftime(
#     "%Y-%m-%d"
# )
#
# CURRENT_TIMESTAMP = datetime.now().strftime(
#     "%Y-%m-%d %H:%M:%S"
# )
#
# # ================= DATE WISE ================= #
#
# BACKUP_DIR = os.path.join(
#     BACKUP_BASE_DIR,
#     CURRENT_DATE
# )
#
# JSON_REPORT_FILE = os.path.join(
#     REPORT_DIR,
#     f"{CURRENT_DATE}.json"
# )
#
# os.makedirs(BACKUP_DIR, exist_ok=True)
#
# # ================= LOGGER ================= #
#
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler(
#             os.path.join(
#                 BASE_DIR,
#                 "ssh_command_execution.log"
#             )
#         ),
#         logging.StreamHandler()
#     ]
# )
#
# # ================= SELECTED IPS ================= #
#
# selected_ips = []
#
# if len(sys.argv) > 1:
#
#     selected_ips = sys.argv[1].split(",")
#
# # ================= NORMALIZE OUTPUT ================= #
#
# def normalize_output(data):
#
#     normalized_lines = []
#
#     for line in data.splitlines():
#
#         line = line.rstrip()
#
#         if line.startswith("!Time:"):
#             continue
#
#         if "Current Time" in line:
#             continue
#
#         normalized_lines.append(line)
#
#     return "\n".join(normalized_lines)
#
# # ================= SSH CLIENT ================= #
#
# def create_ssh_client(
#     ip,
#     username,
#     password
# ):
#
#     logging.info(
#         f"Connecting to {ip}..."
#     )
#
#     client = paramiko.SSHClient()
#
#     client.set_missing_host_key_policy(
#         paramiko.AutoAddPolicy()
#     )
#
#     client.connect(
#         hostname=ip,
#         port=DEFAULT_PORT,
#         username=username,
#         password=password,
#         look_for_keys=False,
#         allow_agent=False,
#         timeout=TIMEOUT
#     )
#
#     logging.info(
#         f"Connected to {ip}"
#     )
#
#     return client
#
# # ================= UPDATE JSON REPORT ================= #
#
# def update_json_report(
#     serial_no,
#     ip,
#     status
# ):
#
#     report_entry = {
#
#         "serial_no": serial_no,
#
#         "timestamp":
#         datetime.now().strftime(
#             "%Y-%m-%d %H:%M:%S"
#         ),
#
#         "ip_address": ip,
#
#         "status": status
#     }
#
#     data = []
#
#     # ================= LOAD EXISTING JSON ================= #
#
#     if os.path.exists(JSON_REPORT_FILE):
#
#         try:
#
#             with open(
#                 JSON_REPORT_FILE,
#                 "r",
#                 encoding="utf-8"
#             ) as file:
#
#                 data = json.load(file)
#
#         except json.JSONDecodeError:
#
#             data = []
#
#     # ================= APPEND ================= #
#
#     data.append(report_entry)
#
#     # ================= SAVE ================= #
#
#     with open(
#         JSON_REPORT_FILE,
#         "w",
#         encoding="utf-8"
#     ) as file:
#
#         json.dump(
#             data,
#             file,
#             indent=4
#         )
#
# # ================= EXECUTE COMMAND ================= #
#
# def execute_command(
#     shell,
#     command
# ):
#
#     output = ""
#
#     shell.send(
#         "terminal length 0\n"
#     )
#
#     time.sleep(2)
#
#     while shell.recv_ready():
#
#         shell.recv(5000)
#
#     shell.send(command + "\n")
#
#     time.sleep(2)
#
#     start_time = time.time()
#
#     while True:
#
#         if shell.recv_ready():
#
#             chunk = shell.recv(5000).decode(
#                 "utf-8",
#                 errors="ignore"
#             )
#
#             output += chunk
#
#             start_time = time.time()
#
#         if time.time() - start_time > READ_TIMEOUT:
#             break
#
#     output = output.replace(
#         '\r',
#         ''
#     )
#
#     return output
#
# # ================= COMPARE AND UPDATE ================= #
#
# def compare_and_update(
#     initial_backup_file,
#     command_output,
#     serial_no,
#     ip
# ):
#
#     try:
#
#         with open(
#             initial_backup_file,
#             "r",
#             encoding="utf-8"
#         ) as f:
#
#             old_output = normalize_output(
#                 f.read()
#             )
#
#         new_output = normalize_output(
#             command_output
#         )
#
#         # ================= DIFFERENCE ================= #
#
#         if old_output != new_output:
#
#             logging.info(
#                 f"Difference found for {ip}"
#             )
#
#             with open(
#                 initial_backup_file,
#                 "w",
#                 encoding="utf-8"
#             ) as f:
#
#                 f.write(new_output)
#
#             logging.info(
#                 f"Backup updated: {initial_backup_file}"
#             )
#
#             update_json_report(
#                 serial_no,
#                 ip,
#                 "Difference Found"
#             )
#
#         # ================= NO DIFFERENCE ================= #
#
#         else:
#
#             logging.info(
#                 f"No difference found for {ip}"
#             )
#
#             update_json_report(
#                 serial_no,
#                 ip,
#                 "No Difference Found"
#             )
#
#     # ================= INITIAL BACKUP ================= #
#
#     except FileNotFoundError:
#
#         logging.info(
#             f"Initial backup not found for {ip}"
#         )
#
#         with open(
#             initial_backup_file,
#             "w",
#             encoding="utf-8"
#         ) as f:
#
#             f.write(command_output)
#
#         logging.info(
#             f"Initial backup created: {initial_backup_file}"
#         )
#
#         update_json_report(
#             serial_no,
#             ip,
#             "Initial Backup Created"
#         )
#
# # ================= READ CSV ================= #
#
# def read_csv_and_connect(file_path):
#
#     with open(
#         file_path,
#         mode='r'
#     ) as file:
#
#         reader = csv.DictReader(file)
#
#         serial_no = 1
#
#         for row in reader:
#
#             ip = row.get(
#                 'IpAddress'
#             ) or row.get('ip')
#
#             # ================= FILTER IPS ================= #
#
#             if selected_ips:
#
#                 if "ALL" not in selected_ips:
#
#                     if ip not in selected_ips:
#
#                         continue
#
#             username = row.get(
#                 'UserName'
#             ) or row.get('username')
#
#             password = row.get(
#                 'Password'
#             ) or row.get('password')
#
#             # ================= SKIP INVALID ================= #
#
#             if not ip or not username or not password:
#
#                 logging.warning(
#                     f"Skipping row: {row}"
#                 )
#
#                 continue
#
#             try:
#
#                 client = create_ssh_client(
#                     ip,
#                     username,
#                     password
#                 )
#
#                 shell = client.invoke_shell()
#
#                 time.sleep(2)
#
#                 logging.info(
#                     f"Executing command on {ip}"
#                 )
#
#                 output = execute_command(
#                     shell,
#                     "show run"
#                 )
#
#                 # ================= BACKUP FILE ================= #
#
#                 initial_backup_file = os.path.join(
#                     BACKUP_DIR,
#                     f"{ip}_output.txt"
#                 )
#
#                 compare_and_update(
#                     initial_backup_file,
#                     output,
#                     serial_no,
#                     ip
#                 )
#
#                 client.close()
#
#                 serial_no += 1
#
#             except Exception as e:
#
#                 logging.error(
#                     f"Error with {ip}: {e}"
#                 )
#
#                 update_json_report(
#                     serial_no,
#                     ip,
#                     f"Failed - {str(e)}"
#                 )
#
# # ================= MAIN ================= #
#
# if __name__ == "__main__":
#
#     read_csv_and_connect(
#         CREDENTIAL_FILE
#     )


#
# import json
# import logging
# import time
# import paramiko
# from datetime import datetime
# import os
# import csv
# import sys
# DEFAULT_PORT = 22
# TIMEOUT = 10
# READ_TIMEOUT = 3
#
#
# # ================= BASE DIRECTORY ================= #
# BASE_DIR = os.path.dirname(
#     os.path.dirname(
#         os.path.abspath(__file__)))
# BACKUP_BASE_DIR = os.path.join(BASE_DIR, "backups")
# REPORT_DIR = os.path.join(BASE_DIR, "reports")
# CREDENTIAL_FILE = os.path.join(
#     BASE_DIR,
#     "credentials",
#     "credentials.csv"
# )
# os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
# os.makedirs(REPORT_DIR, exist_ok=True)
#
#
# # ================= DATE ================= #
# CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
# CURRENT_TIMESTAMP = datetime.now().strftime(
#     "%Y-%m-%d_%H-%M-%S"
# )
# JSON_REPORT_FILE = os.path.join(
#     REPORT_DIR,
#     f"{CURRENT_DATE}.json")
#
#
# # ================= LOGGER ================= #
# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s",
#     handlers=[
#         logging.FileHandler(
#             os.path.join(
#                 BASE_DIR,
#                 "ssh_command_execution.log"
#             )
#         ),
#         logging.StreamHandler()])
#
#
# # ================= SELECTED IPS ================= #
# selected_ips = []
# if len(sys.argv) > 1:
#     selected_ips = sys.argv[1].split(",")
#
#
# # ================= NORMALIZE OUTPUT ================= #
# def normalize_output(data):
#     normalized_lines = []
#     for line in data.splitlines():
#         line = line.rstrip()
#         if line.startswith("!Time:"):
#             continue
#         if "Current Time" in line:
#             continue
#         normalized_lines.append(line)
#     return "\n".join(normalized_lines)
#
#
# # ================= JSON REPORT ================= #
# def update_json_report(
#     serial_no,
#     ip,
#     ssh_status="",
#     command_status="",
#     backup_status="",
#     backup_file="",
#     error=""
# ):
#     report_entry = {
#         "serial_no": serial_no,
#         "timestamp":
#         datetime.now().strftime(
#             "%Y-%m-%d %H:%M:%S"
#         ),
#         "ip_address": ip,
#         "ssh_status": ssh_status,
#         "command_status": command_status,
#         "backup_status": backup_status,
#         "backup_file": backup_file,
#         "error": error}
#     data = []
#     if os.path.exists(JSON_REPORT_FILE):
#         try:
#             with open(
#                 JSON_REPORT_FILE,
#                 "r",
#                 encoding="utf-8"
#             ) as file:
#                 data = json.load(file)
#         except json.JSONDecodeError:
#             data = []
#     data.append(report_entry)
#     with open(
#         JSON_REPORT_FILE,
#         "w",
#         encoding="utf-8"
#     ) as file:
#         json.dump(data, file, indent=4)
#
#
# # ================= SSH CLIENT ================= #
# def create_ssh_client(ip, username, password):
#     logging.info(f"Connecting to {ip}...")
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(
#         paramiko.AutoAddPolicy())
#     client.connect(
#         hostname=ip,
#         port=DEFAULT_PORT,
#         username=username,
#         password=password,
#         auth_timeout=30,
#         banner_timeout=60,
#         look_for_keys=True,
#         allow_agent=True,
#         timeout=TIMEOUT)
#     logging.info(f"Connected to {ip}")
#     return client
#
#
#
# # ================= EXECUTE COMMAND ================= #
# def execute_command(shell, command):
#     output = ""
#     shell.send("terminal length 0\n")
#     time.sleep(2)
#     while shell.recv_ready():
#         shell.recv(5000)
#     shell.send(command + "\n")
#     time.sleep(2)
#     start_time = time.time()
#     while True:
#         if shell.recv_ready():
#             chunk = shell.recv(5000).decode(
#                 "utf-8",
#                 errors="ignore")
#             output += chunk
#             start_time = time.time()
#         if time.time() - start_time > READ_TIMEOUT:
#             break
#     output = output.replace('\r', '')
#     return output
#
#
# # ================= GET LATEST BACKUP ================= #
# def get_latest_backup_file(ip_backup_dir):
#     if not os.path.exists(ip_backup_dir):
#         return None
#     files = [
#         os.path.join(ip_backup_dir, file)
#         for file in os.listdir(ip_backup_dir)
#         if file.endswith(".txt")]
#     if not files:
#         return None
#     files.sort(key=os.path.getmtime, reverse=True)
#     return files[0]
#
#
# # ================= COMPARE AND SAVE ================= #
# def compare_and_save(
#     ip, command_output):
#     ip_backup_dir = os.path.join(
#         BACKUP_BASE_DIR, ip)
#     os.makedirs(ip_backup_dir, exist_ok=True)
#     latest_backup_file = get_latest_backup_file(ip_backup_dir)
#     new_backup_file = os.path.join(
#         ip_backup_dir,
#         f"{ip}_{CURRENT_TIMESTAMP}.txt")
#     normalized_new_output = normalize_output(
#         command_output)
#
#
#     # ================= INITIAL BACKUP ================= #
#     if latest_backup_file is None:
#         with open(
#             new_backup_file, "w", encoding="utf-8") as f:
#             f.write(normalized_new_output)
#         return ("Initial Backup Created", new_backup_file)
#     # ================= COMPARE ================= #
#     with open(latest_backup_file, "r", encoding="utf-8") as f:
#         old_output = normalize_output(f.read())
#
#
#     # ================= DIFFERENCE FOUND ================= #
#     if old_output != normalized_new_output:
#         with open(new_backup_file, "w", encoding="utf-8") as f:
#             f.write(normalized_new_output)
#         return ("Difference Found", new_backup_file)
#     return ("No Difference Found", "")
#
#
# # ================= READ CSV ================= #
# def read_csv_and_connect(file_path):
#     with open(file_path, mode='r') as file:
#         reader = csv.DictReader(file)
#         serial_no = 1
#         for row in reader:
#             ip = row.get('IpAddress') or row.get('ip')
#             if selected_ips:
#                 if "ALL" not in selected_ips:
#                     if ip not in selected_ips:
#                         continue
#             username = row.get('UserName') or row.get('username')
#             password = row.get('Password') or row.get('password')
#             if not ip or not username or not password:
#                 logging.warning(f"Skipping row: {row}")
#                 continue
#             try:
#                 client = create_ssh_client(
#                     ip,
#                     username,
#                     password)
#                 ssh_status = "Success"
#                 shell = client.invoke_shell()
#                 time.sleep(2)
#                 try:
#                     output = execute_command(
#                         shell,
#                         "show run"
#                     )
#
#                     command_status = "Success"
#
#                 except Exception as cmd_error:
#
#                     update_json_report(
#                         serial_no,
#                         ip,
#                         ssh_status=ssh_status,
#                         command_status="Failed",
#                         error=str(cmd_error)
#                     )
#
#                     continue
#
#                 # ================= BACKUP ================= #
#
#                 backup_status, backup_file = compare_and_save(
#                     ip,
#                     output
#                 )
#
#                 update_json_report(
#                     serial_no,
#                     ip,
#                     ssh_status=ssh_status,
#                     command_status=command_status,
#                     backup_status=backup_status,
#                     backup_file=backup_file
#                 )
#
#                 client.close()
#
#             except Exception as ssh_error:
#
#                 logging.error(
#                     f"SSH Failed for {ip}: {ssh_error}"
#                 )
#
#                 update_json_report(
#                     serial_no,
#                     ip,
#                     ssh_status="Failed",
#                     command_status="Not Executed",
#                     error=str(ssh_error)
#                 )
#
#             serial_no += 1
#
# # ================= MAIN ================= #
#
# if __name__ == "__main__":
#
#     read_csv_and_connect(
#         CREDENTIAL_FILE
#     )


"""
import json
import logging
import time
import paramiko
from datetime import datetime
import os
import csv
import sys
import re

DEFAULT_PORT = 22
TIMEOUT = 60
READ_TIMEOUT = 30


# ================= BASE DIRECTORY ================= #
BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)))

BACKUP_BASE_DIR = os.path.join(
    BASE_DIR,
    "backups")

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports")

CREDENTIAL_FILE = os.path.join(
    BASE_DIR,
    "credentials",
    "credentials.csv")

os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)


# ================= DATE ================= #
CURRENT_DATE = datetime.now().strftime(
    "%Y-%m-%d")

CURRENT_TIMESTAMP = datetime.now().strftime(
    "%Y-%m-%d_%H-%M-%S")

JSON_REPORT_FILE = os.path.join(
    REPORT_DIR,
    f"{CURRENT_DATE}.json")


# ================= LOGGER ================= #
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(
                BASE_DIR,
                "ssh_command_execution.log")),
        logging.StreamHandler()])
selected_ips = []
if len(sys.argv) > 1:
    selected_ips = sys.argv[1].split(",")


def normalize_output(data):
    normalized_lines = []
    for line in data.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        if line.startswith("!Time:"):
            continue
        if "Current Time" in line:
            continue
        line = re.sub(r'.*?\bIST\b','IST', line)
        line = re.sub(r'[ \t]+',' ', line)
        normalized_lines.append(line.strip())
    return "\n".join(normalized_lines)


def update_json_report(serial_no, ip, command, ssh_status="", command_status="",
                       backup_status="",backup_file="", error=""):
    report_entry = {
        "serial_no": serial_no,
        "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ip_address": ip,
        "command": command,
        "ssh_status": ssh_status,
        "command_status": command_status,
        "backup_status": backup_status,
        "backup_file": backup_file,
        "error": error}
    data = []
    if os.path.exists(JSON_REPORT_FILE):
        try:
            with open(
                JSON_REPORT_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = []
    data.append(report_entry)
    with open(
        JSON_REPORT_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)



def create_ssh_client(ip, username, password):
    logging.info(f"Connecting to {ip}...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    transport = paramiko.Transport((ip, DEFAULT_PORT))
    security_options = transport.get_security_options()
    security_options.kex = [
        "diffie-hellman-group14-sha1",
        "diffie-hellman-group1-sha1",
        "diffie-hellman-group-exchange-sha1",
        "diffie-hellman-group-exchange-sha256"]
    security_options.key_types = [
        "ssh-rsa",
        "ssh-dss",
        "ecdsa-sha2-nistp256",
        "ssh-ed25519"]
    transport.connect(username=username, password=password)
    client._transport = transport
    logging.info(f"Connected to {ip}")
    return client


def execute_command(shell, command):
    output = ""
    shell.send("terminal length 0\n")
    time.sleep(2)
    while shell.recv_ready():
        shell.recv(5000)
    shell.send(command + "\n")
    time.sleep(2)
    start_time = time.time()
    while True:
        if shell.recv_ready():
            chunk = shell.recv(65535).decode("utf-8", errors="ignore")
            output += chunk
            start_time = time.time()
        if time.time() - start_time > READ_TIMEOUT:
            break
    output = output.replace('\r','')
    return output


def sanitize_command(command):
    return command.replace(" ", "_").replace("/", "_")


def get_latest_backup_file(command_backup_dir):
    if not os.path.exists(command_backup_dir):
        return None
    files = [
        os.path.join(command_backup_dir, file)
        for file in os.listdir(command_backup_dir)
        if file.endswith(".txt")]
    if not files:
        return None
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0]


def compare_and_save(ip, command, command_output):
    command_folder = sanitize_command(command)
    ip_backup_dir = os.path.join(BACKUP_BASE_DIR, ip)
    command_backup_dir = os.path.join(ip_backup_dir, command_folder)
    os.makedirs(command_backup_dir, exist_ok=True)
    latest_backup_file = get_latest_backup_file(command_backup_dir)
    new_backup_file = os.path.join(command_backup_dir,
        f"{ip}_{CURRENT_TIMESTAMP}.txt")
    normalized_new_output = normalize_output(command_output)
    if latest_backup_file is None:
        with open(new_backup_file, "w", encoding="utf-8") as f:
            f.write(normalized_new_output)
        logging.info(f"Initial backup created for {ip} - {command}")
        return ("Initial Backup Created", new_backup_file)
    with open(latest_backup_file, "r", encoding="utf-8") as f:
        old_output = normalize_output(f.read())
    if old_output != normalized_new_output:
        with open(new_backup_file, "w", encoding="utf-8") as f:
            f.write(normalized_new_output)
        logging.info(f"Difference found for {ip} - {command}")
        return ("Difference Found", new_backup_file)
    logging.info(f"No difference found for {ip} - {command}")
    return ("No Difference Found", "")


def read_csv_and_connect(file_path):
    with open(file_path, mode='r') as file:
        reader = csv.DictReader(file)
        serial_no = 1
        for row in reader:
            ip = row.get('IpAddress') or row.get('ip')
            if selected_ips:
                if "ALL" not in selected_ips:
                    if ip not in selected_ips:
                        continue
            username = row.get('UserName') or row.get('username')
            password = row.get('Password') or row.get('password')
            command1 = row.get('Command1')
            command2 = row.get('Command2')
            commands = []
            if command1:
                commands.append(command1)
            if command2:
                commands.append(command2)
            if not ip or not username or not password:
                logging.warning(f"Skipping row: {row}")
                continue
            try:
                client = create_ssh_client(ip, username, password)
                ssh_status = "Success"
                shell = client.invoke_shell()
                time.sleep(3)
            except Exception as ssh_error:
                logging.error(f"SSH Failed for {ip}: {ssh_error}")
                for command in commands:
                    update_json_report(serial_no=serial_no, ip=ip, command=command, ssh_status="Failed",
                        command_status="Not Executed", backup_status="", backup_file="", error=str(ssh_error))
                serial_no += 1
                continue
            for command in commands:
                try:
                    logging.info(f"Executing '{command}' on {ip}")
                    output = execute_command(shell, command)
                    command_status = "Success"
                    backup_status, backup_file = compare_and_save(ip, command, output)
                    update_json_report(
                        serial_no=serial_no,
                        ip=ip,
                        command=command,
                        ssh_status=ssh_status,
                        command_status=command_status,
                        backup_status=backup_status,
                        backup_file=backup_file, error="")
                except Exception as cmd_error:
                    logging.error(f"Command Failed on {ip} - {command}: {cmd_error}")
                    update_json_report(
                        serial_no=serial_no,
                        ip=ip,
                        command=command,
                        ssh_status=ssh_status,
                        command_status="Failed",
                        backup_status="",
                        backup_file="",
                        error=str(cmd_error))
            client.close()
            serial_no += 1

if __name__ == "__main__":
    logging.info(
        "========== BACKUP PROCESS STARTED ==========")
    read_csv_and_connect(
        CREDENTIAL_FILE)
    logging.info(
        "========== BACKUP PROCESS COMPLETED ==========")

"""


#
#
# import json
# import logging
# import time
# import paramiko
# from datetime import datetime
# import os
# import csv
# import sys
# import re
# import warnings
#
# from cryptography.utils import CryptographyDeprecationWarning
#
# warnings.filterwarnings(
#     "ignore",
#     category=CryptographyDeprecationWarning
# )
#
# # ================= CONSTANTS ================= #
#
# DEFAULT_PORT = 22
# TIMEOUT = 30
# READ_TIMEOUT = 10
#
# # ================= BASE DIRECTORY ================= #
#
# BASE_DIR = os.path.dirname(
#     os.path.dirname(
#         os.path.abspath(__file__)
#     )
# )
#
# BACKUP_BASE_DIR = os.path.join(
#     BASE_DIR,
#     "backups"
# )
#
# REPORT_DIR = os.path.join(
#     BASE_DIR,
#     "reports"
# )
#
# CREDENTIAL_FILE = os.path.join(
#     BASE_DIR,
#     "credentials",
#     "credentials.csv"
# )
#
# os.makedirs(BACKUP_BASE_DIR, exist_ok=True)
# os.makedirs(REPORT_DIR, exist_ok=True)
#
# # ================= DATE ================= #
#
# CURRENT_DATE = datetime.now().strftime(
#     "%Y-%m-%d"
# )
#
# CURRENT_TIMESTAMP = datetime.now().strftime(
#     "%Y-%m-%d_%H-%M-%S"
# )
#
# JSON_REPORT_FILE = os.path.join(
#     REPORT_DIR,
#     f"{CURRENT_DATE}.json"
# )
#
# # ================= CLEAR JSON REPORT ================= #
#
# with open(
#     JSON_REPORT_FILE,
#     "w",
#     encoding="utf-8"
# ) as file:
#
#     json.dump([], file)
#
# # ================= LOGGER ================= #
#
# logging.basicConfig(
#
#     level=logging.INFO,
#
#     format="%(asctime)s - %(levelname)s - %(message)s",
#
#     handlers=[
#
#         logging.FileHandler(
#
#             os.path.join(
#                 BASE_DIR,
#                 "ssh_command_execution.log"
#             )
#         ),
#
#         logging.StreamHandler()
#     ]
# )
#
# # ================= SELECTED IPS ================= #
#
# selected_ips = []
#
# if len(sys.argv) > 1:
#
#     selected_ips = sys.argv[1].split(",")
#
# # ================= NORMALIZE OUTPUT ================= #
#
# def normalize_output(data):
#
#     normalized_lines = []
#
#     for line in data.splitlines():
#
#         line = line.rstrip()
#
#         line = re.sub(
#
#             r'\w{3}\s+\w{3}\s+\d+\s+\d+:\d+:\d+(\.\d+)?\s+IST\s+\d{4}',
#
#             '',
#
#             line
#         )
#
#         if line.startswith("!Time:"):
#             continue
#
#         if "Current Time" in line:
#             continue
#
#         if "Last configuration change" in line:
#             continue
#
#         if "NVRAM config last updated" in line:
#             continue
#
#         if not line.strip():
#             continue
#
#         normalized_lines.append(line)
#
#     return "\n".join(normalized_lines)
#
# # ================= JSON REPORT ================= #
# def update_json_report(
#
#     serial_no,
#     ip,
#
#     ssh_status="",
#
#     config_command_status="",
#     interface_command_status="",
#
#     config_backup_status="",
#     interface_backup_status="",
#
#     config_backup_file="",
#     interface_backup_file="",
#
#     error=""
# ):
#
#     report_entry = {
#
#         "SNo": serial_no,
#
#         "Timestamp":
#         datetime.now().strftime(
#             "%d-%m-%Y %H:%M:%S"
#         ),
#
#         "IPAddress": ip,
#
#         "SSHStatus": ssh_status,
#
#         "ConfigCommandStatus":
#             config_command_status,
#
#         "InterfaceCommandStatus":
#             interface_command_status,
#
#         "ConfigBackupStatus":
#             config_backup_status,
#
#         "InterfaceBackupStatus":
#             interface_backup_status,
#
#         "ConfigBackupFile":
#             config_backup_file,
#
#         "InterfaceBackupFile":
#             interface_backup_file,
#
#         "Error": error
#     }
#
#     data = []
#
#     # ================= LOAD OLD JSON ================= #
#
#     if os.path.exists(JSON_REPORT_FILE):
#
#         try:
#
#             with open(
#                 JSON_REPORT_FILE,
#                 "r",
#                 encoding="utf-8"
#             ) as file:
#
#                 data = json.load(file)
#
#         except:
#
#             data = []
#
#     # ================= APPEND ================= #
#
#     data.append(report_entry)
#
#     # ================= SAVE ================= #
#
#     with open(
#         JSON_REPORT_FILE,
#         "w",
#         encoding="utf-8"
#     ) as file:
#
#         json.dump(
#             data,
#             file,
#             indent=4
#         )
#
# # ================= SSH CLIENT ================= #
#
# def create_ssh_client(ip, username, password):
#
#     logging.info(f"Connecting to {ip}...")
#
#     client = paramiko.SSHClient()
#
#     client.set_missing_host_key_policy(
#         paramiko.AutoAddPolicy()
#     )
#
#     transport = paramiko.Transport(
#         (ip, DEFAULT_PORT)
#     )
#
#     security_options = transport.get_security_options()
#
#     security_options.kex = [
#
#         "diffie-hellman-group14-sha1",
#
#         "diffie-hellman-group1-sha1",
#
#         "diffie-hellman-group-exchange-sha1",
#
#         "diffie-hellman-group-exchange-sha256"
#     ]
#
#     security_options.key_types = [
#
#         "ssh-rsa",
#
#         "ssh-dss",
#
#         "ecdsa-sha2-nistp256",
#
#         "ssh-ed25519"
#     ]
#
#     transport.connect(
#         username=username,
#         password=password
#     )
#
#     client._transport = transport
#
#     logging.info(f"Connected to {ip}")
#
#     return client
#
# # ================= EXECUTE COMMAND ================= #
#
# def execute_command(shell, command):
#
#     output = ""
#
#     while shell.recv_ready():
#
#         shell.recv(65535)
#
#     shell.send("terminal length 0\n")
#
#     shell.send("terminal width 512\n")
#
#     time.sleep(1)
#
#     while shell.recv_ready():
#
#         shell.recv(65535)
#
#     shell.send(command + "\n")
#
#     time.sleep(2)
#
#     start_time = time.time()
#
#     last_data_time = time.time()
#
#     while True:
#
#         if shell.recv_ready():
#
#             chunk = shell.recv(65535).decode(
#
#                 "utf-8",
#
#                 errors="ignore"
#             )
#
#             output += chunk
#
#             last_data_time = time.time()
#
#         else:
#
#             time.sleep(0.5)
#
#         if time.time() - last_data_time > READ_TIMEOUT:
#
#             break
#
#         if time.time() - start_time > 300:
#
#             break
#
#     output = output.replace(
#         '\r',
#         ''
#     )
#
#     return output
#
# # ================= SANITIZE COMMAND ================= #
#
# def sanitize_command(command):
#
#     return command.replace(
#         " ",
#         "_"
#     ).replace(
#         "/",
#         "_"
#     )
#
# # ================= GET LATEST BACKUP ================= #
#
# def get_latest_backup_file(command_backup_dir):
#
#     if not os.path.exists(command_backup_dir):
#
#         return None
#
#     files = [
#
#         os.path.join(
#             command_backup_dir,
#             file
#         )
#
#         for file in os.listdir(command_backup_dir)
#
#         if file.endswith(".txt")
#     ]
#
#     if not files:
#
#         return None
#
#     files.sort(
#
#         key=os.path.getmtime,
#
#         reverse=True
#     )
#
#     return files[0]
#
# # ================= COMPARE AND SAVE ================= #
#
# def compare_and_save(
#         ip,
#         command,
#         command_output
# ):
#
#     command_folder = sanitize_command(command)
#
#     ip_backup_dir = os.path.join(
#         BACKUP_BASE_DIR,
#         ip
#     )
#
#     command_backup_dir = os.path.join(
#         ip_backup_dir,
#         command_folder
#     )
#
#     os.makedirs(
#         command_backup_dir,
#         exist_ok=True
#     )
#
#     latest_backup_file = get_latest_backup_file(
#         command_backup_dir
#     )
#
#     new_backup_file = os.path.join(
#
#         command_backup_dir,
#
#         f"{ip}_{command_folder}_{CURRENT_TIMESTAMP}.txt"
#     )
#
#     normalized_new_output = normalize_output(
#         command_output
#     )
#
#     # ================= INITIAL BACKUP ================= #
#
#     if latest_backup_file is None:
#
#         with open(
#             new_backup_file,
#             "w",
#             encoding="utf-8"
#         ) as f:
#
#             f.write(
#                 normalized_new_output
#             )
#
#         logging.info(
#             f"Initial backup created for {ip} - {command}"
#         )
#
#         return (
#             "Initial Backup Created",
#             new_backup_file
#         )
#
#     # ================= READ OLD BACKUP ================= #
#
#     with open(
#         latest_backup_file,
#         "r",
#         encoding="utf-8"
#     ) as f:
#
#         old_output = normalize_output(
#             f.read()
#         )
#
#     # ================= DIFFERENCE FOUND ================= #
#
#     if old_output != normalized_new_output:
#
#         with open(
#             new_backup_file,
#             "w",
#             encoding="utf-8"
#         ) as f:
#
#             f.write(
#                 normalized_new_output
#             )
#
#         logging.info(
#             f"Difference found for {ip} - {command}"
#         )
#
#         return (
#             "Difference Found",
#             new_backup_file
#         )
#
#     # ================= NO DIFFERENCE ================= #
#
#     logging.info(
#         f"No difference found for {ip} - {command}"
#     )
#
#     return (
#         "No Difference Found",
#         ""
#     )
#
# # ================= READ CSV ================= #
#
# def read_csv_and_connect(file_path):
#
#     with open(
#         file_path,
#         mode='r'
#     ) as file:
#
#         reader = csv.DictReader(file)
#
#         serial_no = 1
#
#         for row in reader:
#
#             ip = row.get(
#                 'IpAddress'
#             ) or row.get('ip')
#
#             # ================= FILTER IPS ================= #
#
#             if selected_ips:
#
#                 if "ALL" not in selected_ips:
#
#                     if ip not in selected_ips:
#
#                         continue
#
#             username = row.get(
#                 'UserName'
#             ) or row.get('username')
#
#             password = row.get(
#                 'Password'
#             ) or row.get('password')
#
#             # ================= DYNAMIC COMMANDS ================= #
#
#             commands = []
#
#             for key, value in row.items():
#
#                 if key.lower().startswith("command") and value:
#
#                     commands.append(
#                         value.strip()
#                     )
#
#             # ================= VALIDATION ================= #
#
#             if not ip or not username or not password:
#
#                 logging.warning(
#                     f"Skipping row: {row}"
#                 )
#
#                 continue
#
#             # ================= SSH CONNECTION ================= #
#
#             try:
#
#                 client = create_ssh_client(
#
#                     ip,
#                     username,
#                     password
#                 )
#
#                 ssh_status = "Success"
#
#                 shell = client.invoke_shell()
#
#                 time.sleep(3)
#
#             except Exception as ssh_error:
#
#                 logging.error(
#                     f"SSH Failed for {ip}: {ssh_error}"
#                 )
#
#                 update_json_report(
#
#                     serial_no=serial_no,
#
#                     ip=ip,
#
#                     ssh_status="Failed",
#
#                     config_backup_status="Failed",
#
#                     interface_backup_status="Failed",
#
#                     config_backup_file="",
#
#                     interface_backup_file=""
#                 )
#
#                 serial_no += 1
#
#                 continue
#
#
#             # ================= DEFAULT VALUES ================= #
#
#             config_status = ""
#             interface_status = ""
#
#             config_backup_status = ""
#             interface_backup_status = ""
#
#             config_backup_file = ""
#             interface_backup_file = ""
#
#             # ================= EXECUTE COMMANDS ================= #
#
#             for command in commands:
#
#                 try:
#
#                     logging.info(
#                         f"Executing '{command}' on {ip}"
#                     )
#
#                     output = execute_command(
#                         shell,
#                         command
#                     )
#
#                     if not output.strip():
#                         raise Exception(
#                             "Empty command output received"
#                         )
#
#                     backup_status, backup_file = compare_and_save(
#
#                         ip,
#                         command,
#                         output
#                     )
#
#                     # ================= SHOW RUN ================= #
#                     cmd = command.lower().strip()
#                     # Configuration Commands
#                     if cmd in [
#                         "show run",
#                         "show running-config",
#                         "admin display-config"
#                     ]:
#                         config_status = "Success"
#                         config_backup_status = backup_status
#                         config_backup_file = os.path.basename(backup_file) if backup_file else ""
#
#                     # Interface Commands
#                     elif cmd in [
#                         "show interfaces",
#                         "show int description",
#                         "show port"
#                     ]:
#                         interface_status = "Success"
#                         interface_backup_status = backup_status
#                         interface_backup_file = os.path.basename(backup_file) if backup_file else ""
#
#                 except Exception as cmd_error:
#
#                     logging.error(
#                         f"Command Failed on {ip} - {command}: {cmd_error}"
#                     )
#
#             # ================= SINGLE JSON ENTRY ================= #
#
#             update_json_report(
#
#                 serial_no=serial_no,
#
#                 ip=ip,
#
#                 ssh_status=ssh_status,
#
#                 config_command_status=config_status,
#
#                 interface_command_status=interface_status,
#
#                 config_backup_status=config_backup_status,
#
#                 interface_backup_status=interface_backup_status,
#
#                 config_backup_file=config_backup_file,
#
#                 interface_backup_file=interface_backup_file,
#
#                 error=""
#             )
# # ================= MAIN ================= #
#
# if __name__ == "__main__":
#
#     logging.info(
#         "========== BACKUP PROCESS STARTED =========="
#     )
#
#     read_csv_and_connect(
#         CREDENTIAL_FILE
#     )
#
#     logging.info(
#         "========== BACKUP PROCESS COMPLETED =========="
#     )






# update
#

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

    ssh_status="",

    config_command_status="",
    interface_command_status="",

    config_backup_status="",
    interface_backup_status="",

    config_backup_file="",
    interface_backup_file="",

    error=""
):

    report_entry = {

        "SNo": serial_no,

        "Timestamp":
        datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S"
        ),

        "IPAddress": ip,

        "SSHStatus": ssh_status,

        "ConfigCommandStatus":
            config_command_status,

        "InterfaceCommandStatus":
            interface_command_status,

        "ConfigBackupStatus":
            config_backup_status,

        "InterfaceBackupStatus":
            interface_backup_status,

        "ConfigBackupFile":
            config_backup_file,

        "InterfaceBackupFile":
            interface_backup_file,

        "Error": error
    }

    data = []

    # ================= LOAD OLD JSON ================= #

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

    # ================= APPEND ================= #

    data.append(report_entry)

    # ================= SAVE ================= #

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

    # ---- FIX: instead of hardcoding algorithm names (which may or may not
    # exist in whatever Paramiko/cryptography version is installed on a given
    # machine), we ask Paramiko itself which algorithms it actually
    # implements (via its internal *_info dicts) and only keep the ones that
    # are both in our "candidate" wishlist AND genuinely supported. This
    # eliminates the "unknown cipher" warnings entirely, regardless of
    # Paramiko version, because we never pass a name Paramiko doesn't know.
    #
    # The candidate lists below deliberately include BOTH modern algorithms
    # (for newer devices like the curve25519/gcm-based one we tested) AND
    # older/legacy ones (for old Cisco gear that only speaks
    # diffie-hellman-group1-sha1 / group14-sha1 etc). Whichever subset
    # Paramiko + the remote device both support will be used automatically.

    def _filter_supported(candidates, info_dict_name):

        info = getattr(paramiko.Transport, info_dict_name, {})

        supported = [name for name in candidates if name in info]

        return supported

    kex_candidates = [

        "curve25519-sha256",
        "curve25519-sha256@libssh.org",

        "ecdh-sha2-nistp256",
        "ecdh-sha2-nistp384",
        "ecdh-sha2-nistp521",

        "diffie-hellman-group16-sha512",
        "diffie-hellman-group18-sha512",
        "diffie-hellman-group14-sha256",
        "diffie-hellman-group14-sha1",
        "diffie-hellman-group-exchange-sha256",
        "diffie-hellman-group-exchange-sha1",
        "diffie-hellman-group1-sha1"
    ]

    key_type_candidates = [

        "rsa-sha2-256",
        "rsa-sha2-512",

        "ssh-rsa",

        "ecdsa-sha2-nistp256",

        "ssh-ed25519",

        "ssh-dss"
    ]

    cipher_candidates = [

        "aes128-ctr",
        "aes192-ctr",
        "aes256-ctr",

        "aes128-gcm@openssh.com",
        "aes256-gcm@openssh.com",

        "chacha20-poly1305@openssh.com",

        "aes128-cbc",
        "aes192-cbc",
        "aes256-cbc"
    ]

    kex_supported = _filter_supported(kex_candidates, "_kex_info")

    key_types_supported = _filter_supported(key_type_candidates, "_key_info")

    ciphers_supported = _filter_supported(cipher_candidates, "_cipher_info")

    if kex_supported:
        security_options.kex = kex_supported

    if key_types_supported:
        security_options.key_types = key_types_supported

    if ciphers_supported:
        security_options.ciphers = ciphers_supported

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

                    config_backup_status="Failed",

                    interface_backup_status="Failed",

                    config_backup_file="",

                    interface_backup_file=""
                )

                serial_no += 1

                continue


            # ================= DEFAULT VALUES ================= #

            config_status = ""
            interface_status = ""

            config_backup_status = ""
            interface_backup_status = ""

            config_backup_file = ""
            interface_backup_file = ""

            # ================= EXECUTE COMMANDS ================= #

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
                    cmd = command.lower().strip()
                    # Configuration Commands
                    if cmd in [
                        "show run",
                        "show running-config",
                        "admin display-config"
                    ]:
                        config_status = "Success"
                        config_backup_status = backup_status
                        config_backup_file = os.path.basename(backup_file) if backup_file else ""

                    # Interface Commands
                    elif cmd in [
                        "show interfaces",
                        "show int description",
                        "show port"
                    ]:
                        interface_status = "Success"
                        interface_backup_status = backup_status
                        interface_backup_file = os.path.basename(backup_file) if backup_file else ""

                except Exception as cmd_error:

                    logging.error(
                        f"Command Failed on {ip} - {command}: {cmd_error}"
                    )

            # ================= SINGLE JSON ENTRY ================= #

            update_json_report(

                serial_no=serial_no,

                ip=ip,

                ssh_status=ssh_status,

                config_command_status=config_status,

                interface_command_status=interface_status,

                config_backup_status=config_backup_status,

                interface_backup_status=interface_backup_status,

                config_backup_file=config_backup_file,

                interface_backup_file=interface_backup_file,

                error=""
            )
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
