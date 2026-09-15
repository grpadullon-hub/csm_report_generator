import pandas as pd


def load_excel(file_path):
    """
    Load the CSU CSM Excel template.

    Expected:
      Row 1 = section/group headings
      Row 2 = actual field names
      Row 3+ = response data

    Handles vertically merged cells such as Date.
    """
    try:
        raw = pd.read_excel(
            file_path,
            header=None,
            engine="openpyxl",
        )
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Input Excel file was not found:\n{file_path}"
        )
    except Exception as exc:
        raise RuntimeError(
            f"Unable to read Excel file:\n{file_path}\n\nReason: {exc}"
        )

    if raw.empty:
        raise ValueError("The Excel file contains no data.")

    if len(raw.index) < 2:
        raise ValueError(
            "The Excel file does not contain the required two header rows."
        )

    header_row_1 = raw.iloc[0]
    header_row_2 = raw.iloc[1]

    headers = []
    for first, second in zip(header_row_1, header_row_2):
        if pd.notna(second):
            header = str(second).strip()
        elif pd.notna(first):
            header = str(first).strip()
        else:
            header = ""
        headers.append(header)

    df = raw.iloc[2:].copy()
    df.columns = headers
    df = df.dropna(how="all").copy()

    if "A1. Type of Service" in df.columns:
        df = df[df["A1. Type of Service"].notna()].copy()

    df.reset_index(drop=True, inplace=True)
    return df
