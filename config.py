from pathlib import Path

# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"


# ============================================================
# REQUIRED EXCEL COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
    "Date",
    "A1. Type of Service",
    "A2. Name of Service",
    "B1. Client Type",
    "B2. Sex",
    "B3. Age",
    "B4. Region of Residence",
    "B5. Email Address",
    "CC1",
    "CC2",
    "CC3",
    "SQD0",
    "SQD1",
    "SQD2",
    "SQD3",
    "SQD4",
    "SQD5",
    "SQD6",
    "SQD7",
    "SQD8",
]


# ============================================================
# AGE GROUPS
# ============================================================

AGE_GROUPS = [
    "19 and below",
    "20–34",
    "35–49",
    "50–64",
    "65 or higher",
    "Did not specify",
]


# ============================================================
# SQD RATINGS
# ============================================================

SQD_RATINGS = [5, 4, 3, 2, 1]

SQD_COLUMNS = [
    "SQD0",
    "SQD1",
    "SQD2",
    "SQD3",
    "SQD4",
    "SQD5",
    "SQD6",
    "SQD7",
    "SQD8",
]


# ============================================================
# CITIZEN'S CHARTER
# ============================================================

CC_COLUMNS = [
    "CC1",
    "CC2",
    "CC3",
]


# ============================================================
# CLIENT TYPES
# ============================================================

INTERNAL = "Internal"
EXTERNAL = "External"