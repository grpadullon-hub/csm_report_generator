from config import REQUIRED_COLUMNS


def validate_columns(df):
    """
    Ensure all required columns exist.
    """

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        message = (
            "The Excel file is missing the following required columns:\n\n"
            + "\n".join(f"- {column}" for column in missing)
        )

        raise ValueError(message)


def validate_client_types(df):
    """
    Validate Internal/External classification.
    """

    values = (
        df["A1. Type of Service"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    allowed = {"Internal", "External"}

    invalid = sorted(
        set(values) - allowed
    )

    if invalid:
        raise ValueError(
            "Invalid values found in "
            "'A1. Type of Service':\n"
            + "\n".join(f"- {value}" for value in invalid)
        )


def validate_sqd_values(df):
    """
    SQD values must be 1, 2, 3, 4, 5 or N/A/blank.
    """

    for column in [
        "SQD0",
        "SQD1",
        "SQD2",
        "SQD3",
        "SQD4",
        "SQD5",
        "SQD6",
        "SQD7",
        "SQD8",
    ]:

        if column not in df.columns:
            continue

        values = df[column].dropna()

        invalid = []

        for value in values:

            text = str(value).strip().upper()

            if text in {"N/A", "NA", "N.A."}:
                continue

            try:
                number = int(float(value))
            except (ValueError, TypeError):
                invalid.append(value)
                continue

            if number not in {1, 2, 3, 4, 5}:
                invalid.append(value)

        if invalid:
            raise ValueError(
                f"Invalid values found in {column}: "
                f"{sorted(set(map(str, invalid)))}"
            )