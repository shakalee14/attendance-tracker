import os
import json

import gspread
from google.oauth2.service_account import Credentials


SPREADSHEET_ID = "1Co5SuHTMtNbQPTTPPrJr7fYcqI4090VpEgrbW_I-QsA"


def get_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets"
    ]

    service_account_json = os.environ.get(
        "GOOGLE_SERVICE_ACCOUNT_JSON"
    )

    if service_account_json:
        service_account_info = json.loads(
            service_account_json
        )

        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=scopes
        )
    else:
        credentials = Credentials.from_service_account_file(
            "white-library-507322-g2-32b748dfb397.json",
            scopes=scopes
        )

    return gspread.authorize(credentials)


def get_roster():
    client = get_client()

    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    worksheet = spreadsheet.sheet1

    return worksheet.get_all_records()


def write_attendance_results(results, worksheet_name):
    client = get_client()

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

    rows_to_write = [
        [
            result["name"],
            result["email"],
            result["status"]
        ]
        for result in results
    ]

    if rows_to_write:
        worksheet.append_rows(rows_to_write)

    return worksheet_name