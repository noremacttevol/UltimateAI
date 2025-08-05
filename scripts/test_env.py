from dotenv import load_dotenv
load_dotenv()

import os

# Test that environment variables are loaded
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("SUPABASE_SERVICE_KEY:", os.getenv("SUPABASE_SERVICE_KEY")[:10] + "..." if os.getenv("SUPABASE_SERVICE_KEY") else None)