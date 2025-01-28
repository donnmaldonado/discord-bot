import gspread
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from config import SHEET_ID, WORKSHEET_NAME

scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']

# saves a list (row) with user and message as the tokens to google sheets on cloud
def save_data(row):
    credentials = Credentials.from_service_account_file('adam-bot-service-account-key.json', scopes=scopes)
    gc = gspread.authorize(credentials)

    gauth = GoogleAuth()
    drive = GoogleDrive(gauth)

    # open a google sheet
    gs = gc.open_by_key(SHEET_ID)
    # select a work sheet from its name
    worksheet1 = gs.worksheet(WORKSHEET_NAME)
    worksheet1.append_row(row)
