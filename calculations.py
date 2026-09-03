import pandas as pd

from normalizer import normalize_sqd_value


# ============================================================
# GENERAL HELPERS
# ============================================================

def calculate_percentage(frequency, total):
    """
    Calculate percentage.

    Returns None when total is zero.
    """
    if total == 0:
        return None

    return (frequency / total) * 100


def format_percentage(value):
    """
    Format percentage to two decimal places.
    """
    if value is None:
        return "N/A"

    return f"{value:.2f}%"


# ============================================================
# GENERAL FREQUENCY DISTRIBUTION
# ============================================================

def frequency_distribution(series):
    """
    Generate frequency and percentage distribution.

    Used for:
        - Name of Service
        - Client Type
        - Sex
        - Region

    Blank responses are classified as:
        Did not specify
    """

    cleaned = series.copy()

    cleaned = cleaned.fillna("Did not specify")

    cleaned = cleaned.astype(str).str.strip()

    cleaned = cleaned.replace(
        "",
        "Did not specify"
    )

    total_responses = len(cleaned)

    counts = cleaned.value_counts(
        dropna=False
    )

    results = []

    for category, frequency in counts.items():

        frequency = int(frequency)

        percentage = calculate_percentage(
            frequency,
            total_responses
        )

        results.append({
            "Category": category,
            "Frequency": frequency,
            "Percentage": percentage,
        })

    # --------------------------------------------------------
    # TOTAL CHECK
    # --------------------------------------------------------

    category_total = sum(
        item["Frequency"]
        for item in results
    )

    validation = (
        category_total == total_responses
    )

    return {
        "results": results,
        "total": total_responses,
        "category_total": category_total,
        "percentage_total": (
            100.00
            if total_responses > 0
            else None
        ),
        "validation": validation,
    }


# ============================================================
# AGE
# ============================================================

def classify_age(value):
    """
    Convert numerical age into the required CSM age group.
    """

    if pd.isna(value):
        return "Did not specify"

    try:
        age = float(value)

    except (ValueError, TypeError):
        return "Did not specify"

    if age <= 19:
        return "19 and below"

    elif age <= 34:
        return "20–34"

    elif age <= 49:
        return "35–49"

    elif age <= 64:
        return "50–64"

    else:
        return "65 or higher"


def age_distribution(series):
    """
    Generate CSM age-group distribution.
    """

    age_groups = series.apply(
        classify_age
    )

    total_responses = len(age_groups)

    counts = age_groups.value_counts()

    ordered_groups = [
        "19 and below",
        "20–34",
        "35–49",
        "50–64",
        "65 or higher",
        "Did not specify",
    ]

    results = []

    for group in ordered_groups:

        frequency = int(
            counts.get(group, 0)
        )

        percentage = calculate_percentage(
            frequency,
            total_responses
        )

        results.append({
            "Category": group,
            "Frequency": frequency,
            "Percentage": percentage,
        })

    # --------------------------------------------------------
    # TOTAL CHECK
    # --------------------------------------------------------

    category_total = sum(
        item["Frequency"]
        for item in results
    )

    validation = (
        category_total == total_responses
    )

    return {
        "results": results,
        "total": total_responses,
        "category_total": category_total,
        "percentage_total": (
            100.00
            if total_responses > 0
            else None
        ),
        "validation": validation,
    }


# ============================================================
# CITIZEN'S CHARTER
# ============================================================

def citizen_charter_distribution(
    series,
    valid_ratings=None
):
    """
    Calculate Citizen's Charter distribution.

    CC1 and CC3 use ratings 1–4.
    CC2 uses ratings 1–5.

    If valid_ratings is not supplied,
    the function automatically determines
    the appropriate rating range based on
    the column being processed.
    """

    if valid_ratings is None:
        valid_ratings = [1, 2, 3, 4]
    """
    Calculate CC1, CC2, or CC3.

    N/A is included in TOTAL RESPONSES,
    but excluded from the percentage denominator.

    valid_ratings example:

        CC1 = [1, 2, 3, 4]
        CC2 = [1, 2, 3, 4, 5]
        CC3 = [1, 2, 3, 4]
    """

    values = []

    for value in series:

        if pd.isna(value):
            values.append("N/A")
            continue

        text = str(value).strip()

        if text == "":
            values.append("N/A")
            continue

        try:
            rating = int(float(value))

        except (ValueError, TypeError):
            values.append("N/A")
            continue

        if rating in valid_ratings:
            values.append(rating)
        else:
            values.append("N/A")

    # --------------------------------------------------------
    # TOTAL RESPONSES
    # --------------------------------------------------------

    total_responses = len(values)

    # --------------------------------------------------------
    # N/A
    # --------------------------------------------------------

    na_count = values.count("N/A")

    # --------------------------------------------------------
    # VALID RESPONSES
    # --------------------------------------------------------

    valid_responses = (
        total_responses - na_count
    )

    results = []

    # --------------------------------------------------------
    # VALID RATINGS
    # --------------------------------------------------------

    for rating in valid_ratings:

        frequency = values.count(rating)

        percentage = calculate_percentage(
            frequency,
            valid_responses
        )

        results.append({
            "Rating": rating,
            "Frequency": frequency,
            "Percentage": percentage,
        })

    # --------------------------------------------------------
    # N/A
    # --------------------------------------------------------

    results.append({
        "Rating": "N/A",
        "Frequency": na_count,
        "Percentage": None,
    })

    # --------------------------------------------------------
    # TOTAL CHECK
    # --------------------------------------------------------

    calculated_total = sum(
        item["Frequency"]
        for item in results
    )

    validation = (
        calculated_total == total_responses
    )

    return {
        "results": results,
        "total_responses": total_responses,
        "valid_responses": valid_responses,
        "na": na_count,
        "calculated_total": calculated_total,
        "validation": validation,
    }


# ============================================================
# SQD
# ============================================================

def calculate_sqd(series):
    """
    Calculate SQD0–SQD8.

    Formula:

        SQD % =
        (5 + 4)
        ------------------------------
        (Total Responses - N/A)
        × 100

    N/A is displayed but excluded from
    the denominator.
    """

    normalized = [
        normalize_sqd_value(value)
        for value in series
    ]

    # --------------------------------------------------------
    # TOTAL RESPONSES
    # --------------------------------------------------------

    total_responses = len(normalized)

    # --------------------------------------------------------
    # FREQUENCIES
    # --------------------------------------------------------

    count_5 = normalized.count(5)
    count_4 = normalized.count(4)
    count_3 = normalized.count(3)
    count_2 = normalized.count(2)
    count_1 = normalized.count(1)

    na_count = normalized.count("N/A")

    # --------------------------------------------------------
    # VALID RESPONSES
    # --------------------------------------------------------

    valid_responses = (
        total_responses - na_count
    )

    # --------------------------------------------------------
    # SQD FORMULA
    # --------------------------------------------------------

    if valid_responses == 0:

        sqd_percentage = None

    else:

        sqd_percentage = (
            (count_5 + count_4)
            /
            (total_responses - na_count)
        ) * 100

    # --------------------------------------------------------
    # TOTAL CHECK
    # --------------------------------------------------------

    calculated_total = (
        count_5
        + count_4
        + count_3
        + count_2
        + count_1
        + na_count
    )

    validation = (
        calculated_total == total_responses
    )

    return {
        "5 - VS": count_5,
        "4 - S": count_4,
        "3 - Neither": count_3,
        "2 - DS": count_2,
        "1 - VDS": count_1,
        "N/A": na_count,

        "Valid Responses": valid_responses,

        "Total Responses": total_responses,

        "Calculated Total": calculated_total,

        "SQD %": sqd_percentage,

        "validation": validation,
    }


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_frequency_distribution(data):
    """
    Validate demographic/service distribution.
    """

    return (
        data["category_total"]
        ==
        data["total"]
    )


def validate_citizen_charter(data):
    """
    Validate Citizen's Charter calculation.
    """

    return (
        data["calculated_total"]
        ==
        data["total_responses"]
    )


def validate_sqd(data):
    """
    Validate SQD calculation.
    """

    return (
        data["Calculated Total"]
        ==
        data["Total Responses"]
    )