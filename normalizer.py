import pandas as pd


def clean_text(value):
    """
    Convert blank or missing values to 'Did not specify'.
    """

    if pd.isna(value):
        return "Did not specify"

    text = str(value).strip()

    if text == "":
        return "Did not specify"

    return text


def normalize_dataframe(df):
    """
    Clean the text fields in the CSM dataset.

    This function does NOT change valid numerical values.
    """

    df = df.copy()

    text_columns = [
        "A1. Type of Service",
        "A2. Name of Service",
        "B1. Client Type",
        "B2. Sex",
        "B4. Region of Residence",
    ]

    for column in text_columns:

        if column in df.columns:
            df[column] = df[column].apply(clean_text)

    return df


def normalize_sqd_value(value):
    """
    Normalize SQD responses.

    Valid values:
        1, 2, 3, 4, 5

    N/A, blank, and recognized N/A variations:
        N/A
    """

    if pd.isna(value):
        return "N/A"

    text = str(value).strip().upper()

    if text in {"N/A", "NA", "N.A.", "N.A"}:
        return "N/A"

    try:
        number = int(float(value))
    except (ValueError, TypeError):
        return "N/A"

    if number in {1, 2, 3, 4, 5}:
        return number

    return "N/A"