from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT


def add_heading(document, text):

    paragraph = document.add_paragraph()

    run = paragraph.add_run(text)

    run.bold = True
    run.font.size = Pt(12)

    return paragraph


def add_frequency_table(document, title, data):

    add_heading(document, title)

    table = document.add_table(
        rows=1,
        cols=3
    )

    table.style = "Table Grid"

    headers = [
        "Category",
        "Frequency",
        "Percentage"
    ]

    for cell, header in zip(
        table.rows[0].cells,
        headers
    ):
        cell.text = header

    # --------------------------------------------------------
    # CATEGORY ROWS
    # --------------------------------------------------------

    for item in data["results"]:

        row = table.add_row().cells

        row[0].text = str(
            item["Category"]
        )

        row[1].text = str(
            item["Frequency"]
        )

        if item["Percentage"] is None:
            row[2].text = "N/A"
        else:
            row[2].text = (
                f"{item['Percentage']:.2f}%"
            )

    # --------------------------------------------------------
    # TOTAL ROW
    # --------------------------------------------------------

    row = table.add_row().cells

    row[0].text = "TOTAL"
    row[1].text = str(
        data["category_total"]
    )
    row[2].text = (
        f"{data['percentage_total']:.2f}%"
        if data["percentage_total"] is not None
        else "N/A"
    )

    # --------------------------------------------------------
    # VALIDATION ROW
    # --------------------------------------------------------

    row = table.add_row().cells

    row[0].text = "TOTAL CHECK"
    row[1].text = (
        f"{data['category_total']} / "
        f"{data['total']}"
    )

    row[2].text = (
        "PASS"
        if data["validation"]
        else "FAIL"
    )

    document.add_paragraph()


def add_cc_table(document, title, data):

    add_heading(document, title)

    table = document.add_table(
        rows=1,
        cols=3
    )

    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [
        "Rating",
        "Frequency",
        "Percentage",
    ]

    for cell, header in zip(
        table.rows[0].cells,
        headers
    ):
        cell.text = header

    # --------------------------------------------------------
    # DATA
    # --------------------------------------------------------

    for item in data["results"]:

        row = table.add_row().cells

        row[0].text = str(
            item["Rating"]
        )

        row[1].text = str(
            item["Frequency"]
        )

        if item["Percentage"] is None:
            row[2].text = "N/A"

        else:
            row[2].text = (
                f"{item['Percentage']:.2f}%"
            )

    # --------------------------------------------------------
    # TOTAL ROW
    # --------------------------------------------------------

    row = table.add_row().cells

    row[0].text = "TOTAL RESPONSES"
    row[1].text = str(
        data["total_responses"]
    )

    row[2].text = "100.00%"

    for cell in row:
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True

    # --------------------------------------------------------
    # VALID RESPONSES
    # --------------------------------------------------------

    row = table.add_row().cells

    row[0].text = "VALID RESPONSES"
    row[1].text = str(
        data["valid_responses"]
    )

    row[2].text = ""

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    row = table.add_row().cells

    row[0].text = "VALIDATION"
    row[1].text = (
        "PASS"
        if data["validation"]
        else "FAIL"
    )

    row[2].text = ""

    document.add_paragraph()


def add_sqd_table(document, report):

    add_heading(
        document,
        "Service Quality Dimensions (SQD0–SQD8)"
    )

    table = document.add_table(
        rows=1,
        cols=9
    )

    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers = [
        "SQD",
        "5 – VS",
        "4 – S",
        "3 – Neither",
        "2 – DS",
        "1 – VDS",
        "N/A",
        "Valid",
        "SQD %",
    ]

    for cell, header in zip(
        table.rows[0].cells,
        headers
    ):
        cell.text = header

    for sqd_name, result in report["SQD"].items():

        row = table.add_row().cells

        row[0].text = sqd_name
        row[1].text = str(result["5 - VS"])
        row[2].text = str(result["4 - S"])
        row[3].text = str(result["3 - Neither"])
        row[4].text = str(result["2 - DS"])
        row[5].text = str(result["1 - VDS"])
        row[6].text = str(result["N/A"])
        row[7].text = str(result["Valid Responses"])

        if result["SQD %"] is None:
            row[8].text = "N/A"
        else:
            row[8].text = f"{result['SQD %']:.2f}%"

    document.add_paragraph()


def create_word_report(
    report,
    output_path,
    office_name,
    reporting_period,
):

    document = Document()

    section = document.sections[0]

    section.top_margin = Inches(0.6)
    section.bottom_margin = Inches(0.6)
    section.left_margin = Inches(0.6)
    section.right_margin = Inches(0.6)

    title = document.add_paragraph()

    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    run = title.add_run(
        "CLIENT SATISFACTION MEASUREMENT (CSM) REPORT"
    )

    run.bold = True
    run.font.size = Pt(16)

    subtitle = document.add_paragraph()

    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    subtitle.add_run(
        f"{office_name}\n"
        f"{reporting_period}"
    )

    document.add_paragraph()

    add_heading(
        document,
        f"Total Respondents: {report['total_respondents']}"
    )

    add_frequency_table(
        document,
        "A. Name of Service",
        report["name_of_service"]
    )

    add_frequency_table(
        document,
        "B. Client Type",
        report["client_type"]
    )

    add_frequency_table(
        document,
        "C. Sex",
        report["sex"]
    )

    add_frequency_table(
        document,
        "D. Age",
        report["age"]
    )

    add_frequency_table(
        document,
        "E. Region of Residence",
        report["region"]
    )

    add_cc_table(
        document,
        "F. Citizen's Charter – CC1",
        report["CC1"]
    )

    add_cc_table(
        document,
        "G. Citizen's Charter – CC2",
        report["CC2"]
    )

    add_cc_table(
        document,
        "H. Citizen's Charter – CC3",
        report["CC3"]
    )

    add_sqd_table(
        document,
        report
    )

    document.save(output_path)