import gspread
from google.oauth2.service_account import Credentials
from config import SHEET_ID, WORKSHEET_NAME

SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Authenticate and get worksheet
def get_worksheet():
    credentials = Credentials.from_service_account_file('adam-bot-service-account-key.json', scopes=SCOPES)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(SHEET_ID).worksheet(WORKSHEET_NAME)

# Save a new row (user and message) to Google Sheets
def save_data(row):
    try:
        worksheet = get_worksheet()
        worksheet.append_row(row)
    except Exception as e:
        print(f"Error saving data: {e}")

# Append a reaction to an existing message in Column G (7th column)
def append_reaction(message_id, reaction):
    try:
        worksheet = get_worksheet()

        # Find the row containing the message_id (Column B, 2nd column)
        cell = worksheet.find(str(message_id), in_column=2)
        row = cell.row

        # Get current reactions, append new one
        current_value = worksheet.cell(row, 7).value or ""  
        updated_value = f"{current_value}, {reaction}" if current_value else reaction

        # Update the reactions column
        worksheet.update_cell(row, 7, updated_value)

    except gspread.exceptions.CellNotFound:
        print(f"Message ID {message_id} not found in Column B.")
    except Exception as e:
        print(f"Error updating reactions: {e}")
