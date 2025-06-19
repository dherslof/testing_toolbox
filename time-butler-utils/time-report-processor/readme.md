# Time Report Processor

**NOTE:** This utility is custom made to **only** handle time reports from [time-butler](https://github.com/dherslof/time-butler)!

A Python script to append weekly, monthly, or project time reports from CSV files to a central Excel file. The script automatically detects the report type, prevents duplicate entries, and organizes data into year-based sheets for weekly and monthly reports.

---

## Features

- **Automatic report type detection** (weekly, monthly, project)
- **Prevents duplicate entries** when appending new data
- **Year-based sheet naming** for weekly and monthly reports (e.g., `monthly_2025`)
- **Project reports** get their own sheet, named after the project
- **Automatic column validation and conversion**
- **Summary output** after each run
- **Excel summary** For previous created documents for fast overview

---

## Usage

```sh
python time_report_processor.py <csv_file_path> [excel_file_path]
```

### Examples

```sh
python time_report_processor.py weekly_report.csv
python time_report_processor.py monthly_report.csv
python time_report_processor.py project_report42.csv project_reports.xlsx
```

- If `excel_file_path` is omitted, the default is `time_reports_archive.xlsx`.

---

## How It Works

- **CSV Input:** The script reads your CSV file and determines if it's a weekly, monthly, or project report based on its columns.
- **Excel Output:** Data is appended to the appropriate sheet in the Excel file:
  - **Weekly/Monthly:** Appended to a sheet named `weekly_<year>` or `monthly_<year>`.
  - **Project:** Appended to a sheet named after the project.
- **Duplicates:** Duplicate entries (based on key columns) are detected and skipped.
- **Summary:** After processing, a summary of the operation and the current state of the Excel file is printed.

---

## Requirements

- Python 3.7+
- [pandas](https://pandas.pydata.org/)
- [openpyxl](https://openpyxl.readthedocs.io/)

Install dependencies with:

```sh
pip install pandas openpyxl
```

---

## Logging

- Informative (quite verbose) logging with task summary by default.

---

## License

MIT License

---

## Author
[dherslof](https://github.com/dherslof)
