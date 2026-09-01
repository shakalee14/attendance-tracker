from datetime import datetime

def get_session_date(rows):
    # infers session date to create tab name
    for row in rows:
        join_time = row.get("Join Time")

        if join_time:
            session_datetime = datetime.strptime(
                join_time,
                "%m/%d/%Y %I:%M:%S %p"
            )

            return session_datetime.strftime("%b %-d, %Y")

    return None


def calculate_attendance(rows):
    attendance = {}

    for row in rows:
        email = row["User Email"].strip().lower()
        name = row["Name (Original Name)"].strip()
        duration = int(row["Duration (Minutes)"])

        if not email:
            continue

        if email not in attendance:
            attendance[email] = {
                "name": name,
                "email": email,
                "total_duration": 0
            }

        attendance[email]["total_duration"] += duration

    for person in attendance.values():
        if person["total_duration"] >= 80:
            person["status"] = "Present"
        else:
            person["status"] = "Absent"

    return attendance

def match_roster_to_attendance(roster, attendance):
    results = []

    for fellow in roster:
        email = fellow["Email"].strip().lower()

        zoom_record = attendance.get(email)

        if zoom_record:
            status = zoom_record["status"]
        else:
            status = "Absent"

        results.append({
            "name": fellow["Fellow Name"],
            "email": fellow["Email"],
            "status": status
        })

    return results