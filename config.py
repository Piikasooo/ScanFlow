import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))
CHANNEL_ID = os.getenv("CHANNEL_ID")

# URLs для n8n
N8N_SCAN_URL = os.getenv("N8N_WEBHOOK_URL")
N8N_STAT_URL = os.getenv("N8N_STAT_URL")
N8N_FAMILY_URL = os.getenv("N8N_FAMILY_URL")
N8N_FLYER_URL = os.getenv("N8N_FLYER_URL")