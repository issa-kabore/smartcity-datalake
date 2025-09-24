import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

TABLE_NAME_LOCATIONS = "openaq_locations"
TABLE_NAME_MEASUREMENTS = "openaq_measurements"

