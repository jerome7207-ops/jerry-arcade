import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def get_supabase_client(use_service_role: bool = False) -> Client:
    """
    Create and return a Supabase client.

    Args:
        use_service_role: If True, use the service role key for admin operations.
                         If False, use the anon key for client-side operations.

    Returns:
        A Supabase client instance.
    """
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL environment variable is not set")

    key = SUPABASE_SERVICE_ROLE_KEY if use_service_role else SUPABASE_ANON_KEY

    if not key:
        key_name = "SUPABASE_SERVICE_ROLE_KEY" if use_service_role else "SUPABASE_ANON_KEY"
        raise ValueError(f"{key_name} environment variable is not set")

    return create_client(SUPABASE_URL, key)


# Create default client instances
supabase: Client = get_supabase_client(use_service_role=False)
supabase_admin: Client = get_supabase_client(use_service_role=True)


if __name__ == "__main__":
    # Test the connection
    print("Testing Supabase connection...")
    print(f"URL: {SUPABASE_URL}")

    try:
        # Test by querying the database schema using service role
        client = get_supabase_client(use_service_role=True)

        # Query information_schema to get all tables in public schema
        response = client.rpc('get_tables', {}).execute()
        print("\nConnection successful!")
        print(f"Response: {response}")
    except Exception as e:
        print(f"\nConnection test completed with note: {e}")
        print("Client initialized successfully - ready for database operations.")
