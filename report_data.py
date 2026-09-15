from calculations import (
    frequency_distribution,
    age_distribution,
    citizen_charter_distribution,
    calculate_cc_item_score,
    calculate_cc_total_score,
    calculate_sqd,
)


# ============================================================
# CITIZEN'S CHARTER CONFIGURATION
# ============================================================

CC_STRUCTURE = {
    "CC1": {
        "legacy_column": "CC1",
        "items": ["CC1.1", "CC1.2", "CC1.3"],
        "valid_ratings": [1, 2, 3, 4],
        "maximum_rating": 4,
        "total_score_items": ["CC1.1", "CC1.3"],
    },
    "CC2": {
        "legacy_column": "CC2",
        "items": ["CC2.1", "CC2.2", "CC2.3", "CC2.4", "CC2.5"],
        "valid_ratings": [1, 2, 3, 4, 5],
        "maximum_rating": 5,
        "total_score_items": ["CC2.1"],
    },
    "CC3": {
        "legacy_column": "CC3",
        "items": ["CC3.1", "CC3.2", "CC3.3", "CC3.4"],
        "valid_ratings": [1, 2, 3, 4],
        "maximum_rating": 4,
        "total_score_items": ["CC3.1"],
    },
}


def _calculate_legacy_cc(df, structure):
    column = structure["legacy_column"]
    if column not in df.columns:
        return None

    return citizen_charter_distribution(
        df[column],
        structure["valid_ratings"],
    )


def _calculate_item_based_cc(df, structure):
    """
    Use item-level CC calculations only when the source actually
    contains item columns.

    A total is produced only when ALL configured total-score items
    are present. This prevents incomplete source columns from
    producing a misleading total.
    """
    item_columns_present = [
        item for item in structure["items"] if item in df.columns
    ]

    if not item_columns_present:
        return None

    items = {}
    for item_name in item_columns_present:
        distribution = citizen_charter_distribution(
            df[item_name],
            structure["valid_ratings"],
        )
        score = calculate_cc_item_score(
            distribution,
            structure["maximum_rating"],
        )

        items[item_name] = {
            "distribution": distribution,
            "score": score["score"],
            "percentage": score["percentage"],
            "interpretation": score["interpretation"],
        }

    required = structure["total_score_items"]
    if not all(item in items for item in required):
        total_score = {
            "score": None,
            "percentage": None,
            "interpretation": "N/A",
            "items_used": required,
            "missing_items": [item for item in required if item not in items],
        }
    else:
        total_score = calculate_cc_total_score(
            items,
            required,
            structure["maximum_rating"],
        )

    return {
        "items": items,
        "total_score": total_score,
    }


def generate_citizen_charter_data(df):
    """
    Preserve legacy CC1/CC2/CC3 distributions and optionally add
    item-level CC tables when the source contains item columns.
    """
    report = {}

    for cc_name, structure in CC_STRUCTURE.items():
        legacy_distribution = _calculate_legacy_cc(df, structure)
        item_based = _calculate_item_based_cc(df, structure)

        cc_result = {
            "legacy_distribution": legacy_distribution,
            "items": {},
            "total_score": {
                "score": None,
                "percentage": None,
                "interpretation": "N/A",
                "items_used": structure["total_score_items"],
                "missing_items": structure["total_score_items"],
            },
        }

        if item_based is not None:
            cc_result["items"] = item_based["items"]
            cc_result["total_score"] = item_based["total_score"]

        report[cc_name] = cc_result

    return report


def generate_client_report(df):
    required_columns = [
        "A2. Name of Service",
        "B1. Client Type",
        "B2. Sex",
        "B3. Age",
        "B4. Region of Residence",
    ]
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(
            "Missing report columns: " + ", ".join(missing)
        )

    report = {
        "total_respondents": len(df),
        "name_of_service": frequency_distribution(df["A2. Name of Service"]),
        "client_type": frequency_distribution(df["B1. Client Type"]),
        "sex": frequency_distribution(df["B2. Sex"]),
        "age": age_distribution(df["B3. Age"]),
        "region": frequency_distribution(df["B4. Region of Residence"]),
        "citizen_charter": generate_citizen_charter_data(df),
        "sqd": {},
    }

    for number in range(9):
        column = f"SQD{number}"
        if column not in df.columns:
            raise ValueError(f"Missing required SQD column: {column}")
        report["sqd"][column] = calculate_sqd(df[column])

    return report
