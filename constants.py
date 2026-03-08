from dataclasses import dataclass
from pathlib import Path
import os
# constants.py

# Absolute path to the temp downloads directory.
# Centralized here so that both the downloader and the cleanup cron job
# always reference the same location regardless of the working directory
# the bot is started from.
# Override by setting the TEMP_DOWNLOADS_DIR environment variable.
TEMP_DOWNLOADS_DIR: Path = Path(
    os.environ.get(
        "TEMP_DOWNLOADS_DIR",
        str(Path(__file__).resolve().parent / "temp_downloads"),
    )
).resolve()

# ---------------- DEPARTMENTS ---------------- #

DEPARTMENTS = {
    "Software": "software",
    "Electrical": "electrical",
    "Mechanical": "mechanical",
    "Civil": "civil",
    "Chemical": "chemical",
    "Biomedical": "biomedical",
}

# ---------------- STREAMS ---------------- #

SOFTWARE_STREAMS = {
    "AI": "ai",
    "Software": "software",
    "IT": "it",
    "Cyber": "cyber",
}

ELECTRICAL_STREAMS = {
    "Power": "power",
    "Computer": "computer",
    "Communication": "communication",
    "Control": "control",
    "Electronics": "electronics"
}

# ---------------- YEARS & SEMESTERS ---------------- #

YEARS = {
    "Second Year": "second_year",
    "Third Year": "third_year",
    "Fourth Year": "fourth_year",
    "Fifth Year": "fifth_year",
}

SEMESTERS = {
    "First Semester": "first_semester",
    "Second Semester": "second_semester",
}

# ---------------- MATERIAL TYPES ---------------- #

MATERIAL_TYPES = {
    "Books": "books",
    "Slides": "slides",
    "Exams": "exams",
}

