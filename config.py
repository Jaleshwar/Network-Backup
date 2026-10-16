import os
from datetime import datetime

# ================= BASE PATH ================= #

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ================= DIRECTORIES ================= #

BACKUP_BASE_DIR = os.path.join(
    BASE_DIR,
    "backups"
)

REPORT_DIR = os.path.join(
    BASE_DIR,
    "reports"
)

LOG_DIR = os.path.join(
    BASE_DIR,
    "logs"
)

CREDENTIALS_DIR = os.path.join(
    BASE_DIR,
    "credentials"
)

# ================= FILES ================= #

CREDENTIALS_FILE = os.path.join(
    CREDENTIALS_DIR,
    "credentials.csv"
)

# ================= DATE ================= #

CURRENT_DATE = datetime.now().strftime(
    "%Y-%m-%d"
)

CURRENT_TIMESTAMP = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)

# ================= DATE-WISE PATHS ================= #

BACKUP_DIR = os.path.join(
    BACKUP_BASE_DIR,
    CURRENT_DATE
)

JSON_REPORT_FILE = os.path.join(
    REPORT_DIR,
    f"{CURRENT_DATE}.json"
)

# ================= CREATE DIRECTORIES ================= #

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

# ================= LOG FILE ================= #

LOG_FILE = os.path.join(
    LOG_DIR,
    "automation.log"
)

# ================= SSH CONFIG ================= #

DEFAULT_PORT = 22
TIMEOUT = 10
READ_TIMEOUT = 3