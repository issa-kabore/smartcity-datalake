from dotenv import load_dotenv
from smartcity.utils import get_secret


COUNTRY = "FRANCE"
CITY = "CLERMONT FERRAND"

# Load environment variables from .env file
load_dotenv()

OPENAQ_API_KEY = get_secret("openaq-api-key", "OPENAQ_API_KEY")
SUPABASE_URL = get_secret("supabase-url", "SUPABASE_URL")
SUPABASE_KEY = get_secret("supabase-key", "SUPABASE_KEY")

TABLE_NAME_LOCATIONS = "openaq_locations"
TABLE_NAME_MEASUREMENTS = "openaq_measurements"

