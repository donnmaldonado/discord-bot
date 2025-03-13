import os
from dotenv import load_dotenv

# Load enviorment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SERVER_ID = os.getenv("SERVER_ID")
VERIFIED_ROLE = os.getenv("VERIFIED_ROLE")
TRANSFER_STUDENT_ROLE = os.getenv("TRANSFER_STUDENT_ROLE")
DATA_SHEET_ID = os.getenv("DATA_SHEET_ID")
MESSAGES_WORKSHEET = os.getenv("MESSAGES_WORKSHEET")
ROLES_WORKSHEET = os.getenv("ROLES_WORKSHEET")
EMAILS_SHEET_ID = os.getenv("EMAILS_SHEET_ID")
EMAILS_WORKSHEET = os.getenv("EMAILS_WORKSHEET")
TRANSFER_SHEET_ID = os.getenv("TRANSFER_SHEET_ID")
TRANSFER_WORKSHEET = os.getenv("TRANSFER_WORKSHEET")
INACTIVITY_THRESHOLD = 604800 #time in seconds (1 week)
INACTIVITY_LOOP_TIME = 86400  #time in seconds (1 day)