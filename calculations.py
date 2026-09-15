import pandas as pd

from normalizer import normalize_sqd_value


# ============================================================
# GENERAL HELPERS
# ============================================================

def calculate_percentage(frequency, total):
    """Return frequency / total * 100, or None if total is zero."""
    if total == 0:
        return None
    return (frequency / total) * 100.0


def interpret_percentage(percentage):
    """Interpret a CSM percentage using the required scale."""
    if percentage is None:
        return "N/A"
    if percentage < 60.0:
        return "Poor"
    if percentage < 80.0:
        return "Fair"
    if percentage < 90.0:
        return "Satisfactory"
    if percentage < 95.0:
        return "Very Satisfactory"
    return "Outstanding"


# ============================================================
# GENERAL FREQUENCY DISTRIBUTION
# ============================================================

def frequency_distribution(series):
    """Generate frequency/percentage distribution with validation."""
    cleaned = series.copy().fillna("Did not specify").astype(str).str.strip()
    cleaned = cleaned.replace("", "Did not specify")

    total_responses = len(cleaned)
    counts = cleaned.value_counts(dropna=False)

    results = []
    for category, frequency in counts.items():
        frequency = int(frequency)
        results.append({
            "Category": category,
            "Frequency": frequency,
            "Percentage": calculate_percentage(frequency, total_responses),
        })

    category_total = sum(item["Frequency"] for item in results)

    return {
        "results": results,
        "total": total_responses,
        "category_total": category_total,
        "percentage_total": 100.00 if total_responses > 0 else None,
        "validation": category_total == total_responses,
    }


# ============================================================
# AGE
# ============================================================

def classify_age(value):
    """Convert age into the required CSM age group."""
    if pd.isna(value):
        return "Did not specify"

    try:
        age = float(value)
    except (ValueError, TypeError):
        return "Did not specify"

    if age <= 19:
        return "19 and below"
    if age <= 34:
        return "20–34"
    if age <= 49:
        return "35–49"
    if age <= 64:
        return "50–64"
    return "65 or higher"


def age_distribution(series):
    """Generate the required ordered age-group distribution."""
    age_groups = series.apply(classify_age)
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
        frequency = int(counts.get(group, 0))
        results.append({
            "Category": group,
            "Frequency": frequency,
            "Percentage": calculate_percentage(frequency, total_responses),
        })

    category_total = sum(item["Frequency"] for item in results)

    return {
        "results": results,
        "total": total_responses,
        "category_total": category_total,
        "percentage_total": 100.00 if total_responses > 0 else None,
        "validation": category_total == total_responses,
    }


# ============================================================
# CITIZEN'S CHARTER
# ============================================================

def _normalize_valid_ratings(valid_ratings):
    """Defensively normalize a CC rating list."""
    if valid_ratings is None:
        return [1, 2, 3, 4]

    if isinstance(valid_ratings, (int, float)):
        return [int(valid_ratings)]

    if isinstance(valid_ratings, str):
        values = []
        for part in valid_ratings.replace(",", " ").split():
            try:
                values.append(int(float(part)))
            except (ValueError, TypeError):
                continue
        return values or [1, 2, 3, 4]

    try:
        return [int(float(value)) for value in valid_ratings]
    except (TypeError, ValueError):
        return [1, 2, 3, 4]


def citizen_charter_distribution(series, valid_ratings=None):
    """
    Generate CC frequency distribution.

    N/A is included in total responses and excluded from the
    valid-response percentage denominator.
    """
    valid_ratings = _normalize_valid_ratings(valid_ratings)

    values = []
    for value in series:
        if pd.isna(value):
            values.append("N/A")
            continue

        text = str(value).strip()
        if not text:
            values.append("N/A")
            continue

        try:
            rating = int(float(value))
        except (ValueError, TypeError):
            values.append("N/A")
            continue

        values.append(rating if rating in valid_ratings else "N/A")

    total_responses = len(values)
    na_count = values.count("N/A")
    valid_responses = total_responses - na_count

    results = []
    for rating in valid_ratings:
        frequency = values.count(rating)
        results.append({
            "Rating": rating,
            "Frequency": frequency,
            "Percentage": calculate_percentage(frequency, valid_responses),
        })

    results.append({
        "Rating": "N/A",
        "Frequency": na_count,
        "Percentage": None,
    })

    calculated_total = sum(item["Frequency"] for item in results)

    return {
        "results": results,
        "total_responses": total_responses,
        "valid_responses": valid_responses,
        "na": na_count,
        "calculated_total": calculated_total,
        "validation": calculated_total == total_responses,
    }


def calculate_cc_item_score(distribution, maximum_rating=4):
    """
    Calculate one CC item's weighted average score and percentage.

    Percentage is normalized by the item's actual maximum rating.
    CC2 therefore uses a 1–5 maximum.
    """
    valid_responses = distribution["valid_responses"]

    if valid_responses == 0:
        return {
            "score": None,
            "percentage": None,
            "interpretation": "N/A",
        }

    weighted_score = 0.0
    for item in distribution["results"]:
        rating = item["Rating"]
        if rating == "N/A":
            continue
        weighted_score += int(rating) * int(item["Frequency"])

    average_score = weighted_score / valid_responses
    percentage = (average_score / maximum_rating) * 100.0

    return {
        "score": average_score,
        "percentage": percentage,
        "interpretation": interpret_percentage(percentage),
    }


def calculate_cc_total_score(item_results, total_score_items, maximum_rating=4):
    """
    Calculate the configured CC total.

    IMPORTANT:
      CC1 = percentage(CC1.1) + percentage(CC1.3)
      CC2 = percentage(CC2.1)
      CC3 = percentage(CC3.1)

    The total percentage is intentionally the SUM of the configured
    item percentages. It is NOT recalculated as total_score /
    maximum_score * 100.

    All required items must exist and have a valid percentage.
    Otherwise the total is N/A rather than being calculated from
    incomplete data.
    """
    if isinstance(total_score_items, (str, int, float)):
        required_items = [str(total_score_items)]
    else:
        required_items = [str(item) for item in (total_score_items or [])]

    if not required_items:
        return {
            "score": None,
            "percentage": None,
            "interpretation": "N/A",
            "items_used": [],
            "missing_items": [],
        }

    missing_items = []
    percentages = []
    scores = []

    for item_name in required_items:
        item = item_results.get(item_name)
        if not isinstance(item, dict):
            missing_items.append(item_name)
            continue

        percentage = item.get("percentage")
        score = item.get("score")

        if percentage is None:
            missing_items.append(item_name)
            continue

        percentages.append(float(percentage))
        if score is not None:
            scores.append(float(score))

    if missing_items:
        return {
            "score": None,
            "percentage": None,
            "interpretation": "N/A",
            "items_used": required_items,
            "missing_items": missing_items,
        }

    total_percentage = sum(percentages)
    total_score = sum(scores) if len(scores) == len(required_items) else None

    return {
        "score": total_score,
        "percentage": total_percentage,
        "interpretation": interpret_percentage(total_percentage),
        "items_used": required_items,
        "missing_items": [],
    }


# ============================================================
# SQD
# ============================================================

def calculate_sqd(series):
    """
    Calculate SQD0–SQD8.

    Average Percentage:
        (count of 5 + count of 4)
        / (Total Respondents - N/A) * 100
    """
    normalized = [normalize_sqd_value(value) for value in series]

    count_5 = normalized.count(5)
    count_4 = normalized.count(4)
    count_3 = normalized.count(3)
    count_2 = normalized.count(2)
    count_1 = normalized.count(1)
    na_count = normalized.count("N/A")

    total_respondents = len(normalized)
    valid_responses = total_respondents - na_count

    if valid_responses == 0:
        average_percentage = None
    else:
        average_percentage = ((count_5 + count_4) / valid_responses) * 100.0

    calculated_total = (
        count_5 + count_4 + count_3 + count_2 + count_1 + na_count
    )

    return {
        "5 - VS": count_5,
        "4 - S": count_4,
        "3 - Neither": count_3,
        "2 - DS": count_2,
        "1 - VDS": count_1,
        "N/A": na_count,
        "Valid Responses": valid_responses,
        "Total Respondents": total_respondents,
        "Calculated Total": calculated_total,
        "Average Percentage": average_percentage,
        "Interpretation": interpret_percentage(average_percentage),
        "Validation": calculated_total == total_respondents,
    }


# ============================================================
# VALIDATION HELPERS
# ============================================================

def validate_frequency_distribution(data):
    return data["category_total"] == data["total"]


def validate_citizen_charter(data):
    return data["calculated_total"] == data["total_responses"]


def validate_sqd(data):
    return data["Calculated Total"] == data["Total Respondents"]
