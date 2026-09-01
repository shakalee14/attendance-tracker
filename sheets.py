import gspread
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "1Co5SuHTMtNbQPTTPPrJr7fYcqI4090VpEgrbW_I-QsA"

SERVICE_ACCOUNT_FILE = "white-library-507322-g2-32b748dfb397.json"


def get_roster():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    worksheet = spreadsheet.sheet1

    records = worksheet.get_all_records()

    return records


if __name__ == "__main__":
    roster = get_roster()

    print(f"Found {len(roster)} roster records")

    for person in roster:
        print(person)

def write_attendance_results(results, worksheet_name):
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=scopes
    )

    client = gspread.authorize(credentials)

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    try:
        worksheet = spreadsheet.worksheet(worksheet_name)

        # Clear old results if this session is uploaded again
        worksheet.clear()

    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title=worksheet_name,
            rows=100,
            cols=3
        )

    worksheet.append_row([
        "Fellow Name",
        "Email",
        "Attendance Status"
    ])

    rows_to_write = []

    for result in results:
        rows_to_write.append([
            result["name"],
            result["email"],
            result["status"]
        ])

    if rows_to_write:
        worksheet.append_rows(rows_to_write)

    return worksheet_name