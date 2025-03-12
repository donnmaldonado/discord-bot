import gspread
from google.oauth2.service_account import Credentials
from config import DATA_SHEET_ID, MESSAGES_WORKSHEET, ROLES_WORKSHEET, EMAILS_SHEET_ID, EMAILS_WORKSHEET, TRANSFER_SHEET_ID, TRANSFER_WORKSHEET 

# Define the required Google API scopes
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

# Authenticate and retrieve a Google Sheets worksheet
# Parameters:
# - sheet_id (str): The ID of the Google Sheet
# - worksheet (str): The name of the worksheet to retrieve
# Returns:
# - A gspread worksheet object

def get_worksheet(sheet_id, worksheet):
    credentials = Credentials.from_service_account_file('acosus-discord-d7560833c35f.json', scopes=SCOPES)
    gc = gspread.authorize(credentials)
    return gc.open_by_key(sheet_id).worksheet(worksheet)

# Save a new row (containing user and message data) to Google Sheets
# Parameters:
# - row (list): A list containing the user and message data to be appended
# specifically list should contain [user_id, message_id, reference, channel, sitcker, reactions, timestamp]

def save_message_data(row):
    try:
        worksheet = get_worksheet(DATA_SHEET_ID, MESSAGES_WORKSHEET)
        worksheet.append_row(row)
    except Exception as e:
        print(f"Error saving data: {e}")

# Append a reaction to an existing message in Column G (7th column)
# Parameters:
# - message_id (str or int): The unique identifier of the message
# - reaction (str): The reaction to append

def append_reaction(message_id, reaction):
    try:
        worksheet = get_worksheet(DATA_SHEET_ID, MESSAGES_WORKSHEET)
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

# Save roles associated with a user in Google Sheets
# Parameters:
# - user_id (str): The identifier of the user
# - roles (list): A list of roles associated with the user

def save_roles_data(user_id, roles):
    worksheet = get_worksheet(DATA_SHEET_ID, ROLES_WORKSHEET)
    roles_str = ",".join(roles) if roles else "None"
    cell = worksheet.find(str(user_id), in_column=1)
    if cell == None:
        worksheet.append_row([user_id, roles_str])
    else:
        row = cell.row
        worksheet.update_cell(row, 2, roles_str)


# Verify if a transfer student exists based on their email
# Parameters:
# - email (str): The email of the student
# Returns:
# - bool: True if the student exists, False otherwise

def verify_transfer_student(email):
    worksheet = get_worksheet(TRANSFER_SHEET_ID, TRANSFER_WORKSHEET)
    cell = worksheet.find(email, in_column=6)
    if cell == None:
        return False
    else:
        return True

# Save an email associated with a unique identifier to Google Sheets
# Parameters:
# - user_id (str): A unique identifier for the email entry
# - email (str): The email address to be stored

def save_email(user_id, email):
    worksheet = get_worksheet(EMAILS_SHEET_ID, EMAILS_WORKSHEET)
    cell = worksheet.find(user_id, in_column=1)
    if cell == None:
        worksheet.append_row([user_id, email])
    else:
        row = cell.row
        worksheet.update_cell(row, 2, email)

# Check if a unique identifier has already been verified
# Parameters:
# - user_id (str): The unique identifier to check
# Returns:
# - bool: True if the unique identifier exists, False otherwise

def already_verified(user_id):
    worksheet = get_worksheet(EMAILS_SHEET_ID, EMAILS_WORKSHEET)
    cell = worksheet.find(user_id, in_column=1)
    if cell == None:
        return False
    else:
        return True