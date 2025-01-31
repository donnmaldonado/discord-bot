import os
from dotenv import load_dotenv

# Load enviorment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SHEET_ID = os.getenv("SHEETS_ID")
WORKSHEET_NAME = os.getenv("WORKSHEET_NAME")
INACTIVITY_THRESHOLD = 604800 # time in seconds (1 week)
INACTIVITY_LOOP_TIME = 86400 # time in seconds (1 day)