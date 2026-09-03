import sys
from pathlib import Path

from config import INPUT_DIR, OUTPUT_DIR
from loader import load_excel
from validator import (
    validate_columns,
    validate_client_types,
    validate_sqd_values,
)
from normalizer import normalize_dataframe
from report_data import generate_client_report
from report_writer import create_word_report


def get_input_file():

    files = list(INPUT_DIR.glob("*.xlsx"))

    if not files:

        raise FileNotFoundError(
            "No Excel file was found in the input folder."
        )

    if len(files) > 1:

        raise ValueError(
            "More than one Excel file was found.\n\n"
            "Please keep only one input Excel file in the "
            "'input' folder."
        )

    return files[0]


def main():

    print("=" * 60)
    print("CSM REPORT GENERATOR")
    print("=" * 60)

    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    input_file = get_input_file()

    print(f"\nInput file: {input_file.name}")

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    df = load_excel(input_file)

    print(f"Rows loaded: {len(df)}")

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    validate_columns(df)
    validate_client_types(df)
    validate_sqd_values(df)

    print("Validation: PASSED")

    # --------------------------------------------------------
    # NORMALIZE
    # --------------------------------------------------------

    df = normalize_dataframe(df)

    # --------------------------------------------------------
    # INTERNAL
    # --------------------------------------------------------

    internal_df = df[
        df["A1. Type of Service"] == "Internal"
    ].copy()

    # --------------------------------------------------------
    # EXTERNAL
    # --------------------------------------------------------

    external_df = df[
        df["A1. Type of Service"] == "External"
    ].copy()

    print(f"Internal respondents: {len(internal_df)}")
    print(f"External respondents: {len(external_df)}")

    # --------------------------------------------------------
    # REPORT DATA
    # --------------------------------------------------------

    internal_report = generate_client_report(
        internal_df
    )

    external_report = generate_client_report(
        external_df
    )

    # --------------------------------------------------------
    # REPORT INFORMATION
    # --------------------------------------------------------

    office_name = input(
        "\nEnter Office Name: "
    ).strip()

    reporting_period = input(
        "Enter Reporting Period: "
    ).strip()

    # --------------------------------------------------------
    # WORD REPORTS
    # --------------------------------------------------------

    internal_output = (
        OUTPUT_DIR
        / f"CSM_Report_Internal_{reporting_period.replace(' ', '_')}.docx"
    )

    external_output = (
        OUTPUT_DIR
        / f"CSM_Report_External_{reporting_period.replace(' ', '_')}.docx"
    )

    create_word_report(
        internal_report,
        internal_output,
        office_name,
        f"{reporting_period} - Internal Clients",
    )

    create_word_report(
        external_report,
        external_output,
        office_name,
        f"{reporting_period} - External Clients",
    )

    print("\nReports generated successfully.")

    print(f"\nInternal report:")
    print(internal_output)

    print(f"\nExternal report:")
    print(external_output)

    print("\nDone.")


if __name__ == "__main__":

    try:
        main()

    except Exception as exc:

        print("\nERROR:")
        print(exc)

        sys.exit(1)