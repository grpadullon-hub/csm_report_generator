import sys

from config import INPUT_DIR, OUTPUT_DIR
from loader import load_excel
from validator import (
    validate_columns,
    validate_client_types,
    validate_sqd_values,
)
from normalizer import normalize_dataframe
from periods import filter_by_period, period_label, safe_period_filename
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
            "Please keep only one input Excel file in the 'input' folder."
        )

    return files[0]


def choose_report_period():
    print("\n" + "-" * 60)
    print("SELECT REPORT TYPE")
    print("-" * 60)
    print("1. Monthly")
    print("2. 1st Semester (January–June)")
    print("3. 2nd Semester (July–December)")

    while True:
        choice = input("\nEnter choice [1-3]: ").strip()

        if choice not in {"1", "2", "3"}:
            print("Please enter 1, 2, or 3.")
            continue

        year_text = input("Enter reporting year (e.g., 2026): ").strip()
        try:
            year = int(year_text)
            if not 1900 <= year <= 2100:
                raise ValueError
        except ValueError:
            print("Please enter a valid year between 1900 and 2100.")
            continue

        if choice == "1":
            month_text = input("Enter month [1-12]: ").strip()
            try:
                month = int(month_text)
                if not 1 <= month <= 12:
                    raise ValueError
            except ValueError:
                print("Please enter a valid month from 1 to 12.")
                continue

            return "monthly", year, month

        if choice == "2":
            return "first_semester", year, None

        return "second_semester", year, None


def build_output_path(period_file_name, client_group):
    return OUTPUT_DIR / (
        f"CSM_Report_{client_group}_{period_file_name}.docx"
    )


def main():
    print("=" * 60)
    print("CSM REPORT GENERATOR")
    print("Monthly / Semestral")
    print("=" * 60)

    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    input_file = get_input_file()
    print(f"\nInput file: {input_file.name}")

    df = load_excel(input_file)
    print(f"Rows loaded: {len(df)}")

    # Validate the master before filtering.
    validate_columns(df)
    validate_client_types(df)
    validate_sqd_values(df)
    print("Validation: PASSED")

    df = normalize_dataframe(df)

    report_type, year, month = choose_report_period()

    filtered_df, start_date, end_date = filter_by_period(
        df,
        report_type,
        year,
        month,
    )

    label = period_label(report_type, year, month)
    filename_period = safe_period_filename(report_type, year, month)

    print("\n" + "-" * 60)
    print(f"REPORTING PERIOD: {label}")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    print(f"Responses in selected period: {len(filtered_df)}")
    print("-" * 60)

    if filtered_df.empty:
        print(
            "\nWARNING: No CSM responses were found in the selected "
            "reporting period."
        )

    internal_df = filtered_df[
        filtered_df["A1. Type of Service"] == "Internal"
    ].copy()

    external_df = filtered_df[
        filtered_df["A1. Type of Service"] == "External"
    ].copy()

    print(f"Internal respondents: {len(internal_df)}")
    print(f"External respondents: {len(external_df)}")

    office_name = input("\nEnter Office Name: ").strip()

    reports = {
        "Internal": (
            internal_df,
            build_output_path(filename_period, "Internal"),
        ),
        "External": (
            external_df,
            build_output_path(filename_period, "External"),
        ),
    }

    for client_group, (group_df, output_path) in reports.items():
        report_data = generate_client_report(group_df)

        create_word_report(
            report_data,
            output_path,
            office_name,
            f"{label} - {client_group} Clients",
        )

    print("\nReports generated successfully.")
    print(f"\nInternal report: {reports['Internal'][1]}")
    print(f"External report: {reports['External'][1]}")
    print("\nDone.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("\nERROR:")
        print(exc)
        sys.exit(1)
