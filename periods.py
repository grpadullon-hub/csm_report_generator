from datetime import datetime
import pandas as pd


MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


def prepare_date_column(df, column="Date"):
    """Return a copy with Date converted to pandas datetime."""
    if column not in df.columns:
        raise ValueError(f"Missing required date column: {column}")

    result = df.copy()
    result[column] = pd.to_datetime(result[column], errors="coerce")

    invalid = int(result[column].isna().sum())
    if invalid:
        raise ValueError(
            f"{invalid} record(s) have an invalid or missing Date. "
            "A valid date is required for monthly/semestral filtering."
        )

    return result


def get_period_dates(report_type, year, month=None):
    """
    Return inclusive start/end timestamps for the selected report period.

    report_type:
      monthly
      first_semester
      second_semester
    """
    report_type = str(report_type).strip().lower()

    if report_type == "monthly":
        if month is None or not 1 <= int(month) <= 12:
            raise ValueError("Month must be between 1 and 12.")
        month = int(month)
        start = pd.Timestamp(year=int(year), month=month, day=1)
        end = start + pd.offsets.MonthEnd(1)
        return start, end

    if report_type == "first_semester":
        return (
            pd.Timestamp(year=int(year), month=1, day=1),
            pd.Timestamp(year=int(year), month=6, day=30),
        )

    if report_type == "second_semester":
        return (
            pd.Timestamp(year=int(year), month=7, day=1),
            pd.Timestamp(year=int(year), month=12, day=31),
        )

    raise ValueError(
        "Invalid report type. Use monthly, first_semester, or second_semester."
    )


def filter_by_period(df, report_type, year, month=None, date_column="Date"):
    """Filter the CSM master to the exact selected reporting period."""
    prepared = prepare_date_column(df, date_column)
    start, end = get_period_dates(report_type, year, month)

    mask = prepared[date_column].between(start, end, inclusive="both")
    filtered = prepared.loc[mask].copy()
    filtered.reset_index(drop=True, inplace=True)

    return filtered, start, end


def period_label(report_type, year, month=None):
    """Human-readable report label."""
    report_type = str(report_type).strip().lower()

    if report_type == "monthly":
        return f"{MONTH_NAMES[int(month) - 1]} {int(year)}"

    if report_type == "first_semester":
        return f"1st Semester (January–June) {int(year)}"

    if report_type == "second_semester":
        return f"2nd Semester (July–December) {int(year)}"

    raise ValueError("Invalid report type.")


def safe_period_filename(report_type, year, month=None):
    """Filesystem-safe period name."""
    report_type = str(report_type).strip().lower()

    if report_type == "monthly":
        return f"{MONTH_NAMES[int(month) - 1]}_{int(year)}"

    if report_type == "first_semester":
        return f"1st_Semester_January-June_{int(year)}"

    if report_type == "second_semester":
        return f"2nd_Semester_July-December_{int(year)}"

    raise ValueError("Invalid report type.")
