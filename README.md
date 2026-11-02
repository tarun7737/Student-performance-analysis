# Student Performance Analysis & Data Visualization

**Created by Tarun Katara**

A Python dashboard for analyzing student marks from an uploaded CSV or Excel file.
It uses Pandas for data processing and Matplotlib for charts.

## Features
- Upload CSV, XLSX, or XLS files
- Map the student name/ID column and subject marks columns
- Clean invalid and missing mark values
- Calculate totals, averages, percentages, ranks, and Pass/Fail results
- Show class KPIs and student-wise results
- Visualize top students, subject averages, score distribution, Pass/Fail split, and subject comparisons
- Download analyzed results as a CSV file

## Input file format
Use one row per student, with a header row. Example:

| Student | Maths | Science | English |
|---|---:|---:|---:|
| Amit | 85 | 80 | 75 |
| Priya | 95 | 90 | 85 |
| Rahul | 70 | 75 | 80 |

Column names can differ. After uploading, select the student identifier and subject marks columns in the dashboard.
Marks outside the configured range (0 to maximum marks) are excluded. Blank or non-numeric marks are treated as missing.
The percentage is calculated using the average of available valid subject marks divided by the configured maximum marks.

## Run locally
1. Install Python 3.9 or newer.
2. Open a terminal in this project folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the dashboard:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown in the terminal and upload a CSV or Excel file.

## Project structure
- `app.py` - Streamlit dashboard and analysis logic
- `sample_students.csv` - sample input data
- `requirements.txt` - required Python packages

## Resume description
**Student Performance Analysis & Data Visualization | Python, Pandas, Matplotlib, Streamlit**
- Built an interactive dashboard that accepts CSV and Excel files for student performance analysis.
- Cleaned uploaded data and calculated totals, averages, percentages, ranks, and pass/fail outcomes using Pandas.
- Developed Matplotlib visualizations for subject-wise averages, student rankings, score distribution, and pass/fail analysis.
- Enabled users to download analyzed results as a CSV report.

**Created by Tarun Katara**
