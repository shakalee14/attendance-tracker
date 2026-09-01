import csv
from datetime import datetime

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from attendance import (
    calculate_attendance,
    match_roster_to_attendance,
)
from sheets import get_roster, write_attendance_results


app = Flask(__name__)


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def handle_submit():
    # Validate uploaded file
    if "attendance_file" not in request.files:
        return "No file included in request", 400

    uploaded_file = request.files["attendance_file"]

    if uploaded_file.filename == "":
        return "No selected file", 400

    filename = secure_filename(uploaded_file.filename)

    if not filename.lower().endswith(".csv"):
        return "Please upload a CSV file", 400

    # Get and validate the session date selected by staff
    session_date = request.form.get("session_date")

    if not session_date:
        return "Please select a session date", 400

    selected_date = datetime.strptime(
        session_date,
        "%Y-%m-%d"
    ).date()

    # Read the uploaded CSV
    csv_file = uploaded_file.stream.read().decode("utf-8").splitlines()
    reader = csv.DictReader(csv_file)
    rows = list(reader)

    # Only process Zoom records from the selected session date
    session_rows = []

    for row in rows:
        join_time = datetime.strptime(
            row["Join Time"],
            "%m/%d/%Y %I:%M:%S %p"
        )

        if join_time.date() == selected_date:
            session_rows.append(row)

    # Calculate attendance for the selected session
    attendance = calculate_attendance(session_rows)

    # Get the Fellow roster from Google Sheets
    roster = get_roster()

    # Match the roster against Zoom attendance
    results = match_roster_to_attendance(
        roster,
        attendance
    )

    # Create a readable worksheet name
    formatted_date = selected_date.strftime("%b %-d, %Y")
    worksheet_name = f"Attendance - {formatted_date}"

    # Write results to Google Sheets
    write_attendance_results(
        results,
        worksheet_name
    )

    print(f"Total CSV rows: {len(rows)}")
    print(f"Rows for selected session: {len(session_rows)}")
    print(f"Updated worksheet: {worksheet_name}")

    present_count = sum(
        1 for result in results
        if result["status"] == "Present"
    )

    absent_count = sum(
        1 for result in results
        if result["status"] == "Absent"
    )

    return render_template(
        "results.html",
        results=results,
        worksheet_name=worksheet_name,
        present_count=present_count,
        absent_count=absent_count,
        session_date=formatted_date
    )


if __name__ == "__main__":
    app.run(debug=True)