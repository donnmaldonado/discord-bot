import os
from dotenv import load_dotenv

# Load enviorment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATA_SHEET_ID = os.getenv("SHEETS_ID")
MESSAGES_WORKSHEET = os.getenv("MESSAGES_WORKSHEET")
ROLES_WORKSHEET = os.getenv("ROLES_WORKSHEET")
EMAILS_SHEET_ID = os.getenv("EMAILS_SHEET_ID")
EMAILS_WORKSHEET = os.getenv("EMAILS_WORKSHEET")
INACTIVITY_THRESHOLD = 604800 # time in seconds (1 week)
INACTIVITY_LOOP_TIME = 86400 # time in seconds (1 day)