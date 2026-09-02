# Attendance Tracker

A small web application that helps program staff automatically record Fellow attendance using a Zoom attendance report and a Google Sheets roster.

Live URL: https://attendance-tracker-79b5.onrender.com/

## How to Use the Attendance Tracker

#### 1. Download the Zoom attendance report

After a Zoom session, download the attendance report as a CSV file. For more on how to get the attendance sheet, visit [zoom instructions here.](https://support.zoom.com/hc/en/article?id=zm_kb&sysparm_article=KB0073594)

The application expects the attendance sheet to include the following columns:

* `Name (Original Name)`
* `User Email`
* `Join Time`
* `Duration (Minutes)`

#### 2. Open the Attendance Tracker

Open the Attendance Tracker in your web browser.

#### 3. Upload the CSV

Click **Select attendance CSV** and choose the Zoom attendance CSV file.

#### 4. Select the session date

Choose the date of the Zoom session you want to process.

The application will only use attendance records from the selected date.

#### 5. Record attendance

Click **Record Attendance**.

The application will process the attendance report and update the Program Roster Google Sheet.

#### 6. Review the results

After processing, you should be able to view the results with the following:

* The session date
* The total number of Fellows processed
* The number marked Present
* The number marked Absent
* Individual attendance results

The same results are also written to an attendance tab in the Google Sheet.


#### Attendance Policy

It's assumed that session attendees need to attend most of the session to receive credit. This app marks someone absent who misses more than 10 minutes.

For example, a fellow is therefore marked:

* **Present:** attended for 80 minutes or more
* **Absent:** attended for less than 80 minutes

If a Fellow appears in multiple Zoom attendance records on the selected date, their attendance durations are added together.

For more info on how this app was made, including in depth technical explanations, review the summaries below.

---

## Requirements Overview

Program staff upload a Zoom attendance CSV through the browser and select the date of the session they want to process.

The application:

1. Reads the uploaded Zoom attendance report.
2. Filters attendance records to the selected session date.
3. Combines multiple Zoom attendance records for the same person.
4. Calculates each person's total attendance duration.
5. Matches attendance records against the Fellow roster in Google Sheets.
6. Marks each Fellow as **Present** or **Absent**.
7. Writes the results to a new or existing attendance tab in the Google Sheet.

## System Architecture

The application uses a simple architecture designed for the scope of this prototype.

```text
Program Staff
      |
      v
Flask Web Application
      |
      +----> Zoom Attendance CSV
      |             |
      |             v
      |      Filter by Session Date
      |             |
      |             v
      |      Calculate Attendance
      |
      +----> Google Sheets API
                    |
                    v
              Fellow Roster
                    |
                    v
            Attendance Results
```

### Technologies Used

* **Python**
* **Flask**
* **Google Sheets API**
* **gspread**
* **Gunicorn** for deployment

The application is deployed as a small web service.

---

# Decisions and Edge Cases

The assessment instructions intentionally leave some details unspecified. I made the following decisions for this prototype hoping it would make a better user experience and add some flexibility.

## Multiple dates in the Zoom CSV

### What I noticed

The sample Zoom attendance data contained records from more than one date, for example August 19th and August 26 sessions.

### Decision

Rather than assuming that the first date in the CSV is the correct session, the application asks the staff member to select the session date. This gives staff some flexibility but is also a feature that can easily be removed. This also assumes this application can be used for future dates.

The application only processes Zoom records with a `Join Time` matching the selected date.

---

## Multiple Zoom records for the same Fellow (data cleaning)

### What I noticed

A person may join and leave a Zoom session multiple times.

### Decision

The application groups attendance records by normalized email address and adds the total duration for that person.

### Why

A Fellow who temporarily leaves and rejoins the session should receive credit for their total attendance time.

---

## Email capitalization (more data cleaning)

### What I noticed

Email addresses may use different capitalization in Zoom and the roster.

### Decision

Email addresses are normalized to lowercase before matching records.

### Why

Email addresses should match regardless of capitalization differences.

---

## Fellow appears in the roster but not in Zoom

### Decision

The Fellow is included in the final attendance results and marked **Absent**.

### Why

The roster represents the people expected to attend the session. This assumption can easily be fixed once we confirm with program staff if this is the right call for these fellows.

---

## Zoom participant does not appear in the roster

### Decision

The participant is not added to the final attendance results.

### Why

The attendance sheet is intended to record attendance for Fellows in the official program roster.

In a production implementation, this could also be surfaced as an exception for staff review. Exceptions can be separately flagged and probably color coded via the google api.

---

## Reprocessing the same session

### Decision

If an attendance tab already exists for the selected session date, the application clears and replaces the previous results.

### Why

This makes it possible to correct an upload or rerun the attendance process without creating duplicate attendance tabs. Of course the other option would be to flag and disable someone from uploading a date twice - I don't believe we would want to simply just add more records to it.

---

# Assumptions and Open Questions

This prototype makes several assumptions that I would confirm with program staff before building a production system.

### Attendance duration

The application uses Zoom's `Duration (Minutes)` field as the source of truth for attendance time.

A production implementation should confirm whether this field always reflects the organization's desired attendance policy.

### Session identification

This prototype uses a staff-selected calendar date to identify the session.

### Roster eligibility

This prototype processes all Fellows returned by the roster.

A production system should confirm whether attendance should be limited to Fellows with a specific enrollment status, cohort, or program.

### Unmatched participants

The prototype ignores Zoom participants who are not on the Fellow roster.

A production system could provide staff with a list of unmatched participants for review.

---

# Running Locally

## Prerequisites

Before running the application, make sure you have Python 3 installed.

## 1. Clone the repository

```bash
git clone <repository-url>
cd attendance-tracker
```

## 2. Create a virtual environment

```bash
python3 -m venv venv
```

## 3. Activate the virtual environment

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

After activation, your terminal should show `(venv)`.

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

## 5. Configure Google Sheets credentials

The application requires a Google service account with access to the Program Roster Google Sheet.

For local development, place the Google service account credentials JSON file in the project root with the filename expected by `sheets.py`.

For security, this credentials file is excluded from Git and should never be committed to the repository.

The service account must also be given access to the Google Sheet.

## 6. Run the application

```bash
python app.py
```

Then open the application in your browser:

```text
http://127.0.0.1:5000
```

## Deployment Credentials

For the deployed application, Google service account credentials are provided through the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable rather than a credentials file.

---

# AI and Outside Resources

AI tools were used during development as a resource for assistance with implementation and debugging. The initial plan was reviewed, and edge cases were examined, including debugging help to use Render, the free platform used to deploy the application.

The final solution was reviewed and tested independently. Implementation decisions—including how to handle multiple attendance dates, repeated Zoom attendance records, email normalization, and roster matching—were evaluated based on the requirements and behavior of the sample data.

The solution was tested locally by uploading the provided Zoom attendance data and verifying that the resulting attendance records were written to the Google Sheet.

---

# Next Steps

If New Roots decided to move forward with a production attendance solution, I would recommend the following steps:

1. **Confirm the attendance workflow with program staff.**
   Understand how staff currently download reports, identify sessions, and handle exceptions.

2. **Validate the attendance policy and data rules.**
   Confirm how late arrivals, early departures, multiple Zoom joins, and unmatched participants should be handled.

3. **Define the source of truth for sessions and Fellows.**
   Determine whether sessions should be identified by Zoom meeting IDs, a program database, or another system.

4. **Improve exception handling and staff review workflows.**
   Surface unmatched participants, invalid records, and ambiguous attendance situations rather than silently processing them. For bigger lists this is especially important, but this of course depends on the size of meetings list to process.

The prototype focuses on validating the core workflow first: reducing manual attendance processing while keeping the workflow understandable for non-technical staff.
