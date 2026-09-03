import pandas as pd


def load_excel(file_path):
    """
    Load the CSU CSM Excel template.

    Expected structure:

        Row 1:
            Main/group headings

        Row 2:
            Actual field names

        Row 3 onward:
            CSM response data

    The template contains merged cells, particularly the Date
    column. Therefore, the two header rows are read separately
    and combined.
    """

    try:
        raw = pd.read_excel(
            file_path,
            header=None,
            engine="openpyxl"
        )

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input Excel file was not found:\n{file_path}"
        )

    except Exception as exc:
        raise RuntimeError(
            f"Unable to read Excel file:\n{file_path}\n\n"
            f"Reason: {exc}"
        )

    if raw.empty:
        raise ValueError(
            "The Excel file contains no data."
        )

    # --------------------------------------------------------
    # HEADER ROWS
    # --------------------------------------------------------

    # Excel Row 1 -> pandas index 0
    header_row_1 = raw.iloc[0]

    # Excel Row 2 -> pandas index 1
    header_row_2 = raw.iloc[1]

    headers = []

    for first, second in zip(
        header_row_1,
        header_row_2
    ):

        # Prefer the actual field name in Row 2.
        if pd.notna(second):
            header = str(second).strip()

        # If Row 2 is blank because of a vertically
        # merged cell, use Row 1.
        elif pd.notna(first):
            header = str(first).strip()

        else:
            header = ""

        headers.append(header)

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    # Data starts after the two header rows.
    df = raw.iloc[2:].copy()

    # Assign our reconstructed headers.
    df.columns = headers

    # Remove completely empty rows.
    df = df.dropna(how="all").copy()

    # --------------------------------------------------------
    # REMOVE EMPTY / TEMPLATE RECORDS
    # --------------------------------------------------------

    # A real CSM response should contain a value in
    # "A1. Type of Service".
    if "A1. Type of Service" in df.columns:

        df = df[
            df["A1. Type of Service"].notna()
        ].copy()

    # Reset index.
    df.reset_index(drop=True, inplace=True)

    return df