from calculations import (
    frequency_distribution,
    age_distribution,
    citizen_charter_distribution,
    calculate_sqd,
)


def generate_client_report(df):

    report = {}

    report["total_respondents"] = len(df)

    report["name_of_service"] = frequency_distribution(
        df["A2. Name of Service"]
    )

    report["client_type"] = frequency_distribution(
        df["B1. Client Type"]
    )

    report["sex"] = frequency_distribution(
        df["B2. Sex"]
    )

    report["age"] = age_distribution(
        df["B3. Age"]
    )

    report["region"] = frequency_distribution(
        df["B4. Region of Residence"]
    )

    report["CC1"] = citizen_charter_distribution(
        df["CC1"]
    )

    report["CC2"] = citizen_charter_distribution(
        df["CC2"]
    )

    report["CC3"] = citizen_charter_distribution(
        df["CC3"]
    )

    report["SQD"] = {}

    for number in range(0, 9):

        column = f"SQD{number}"

        report["SQD"][column] = calculate_sqd(
            df[column]
        )

    return report