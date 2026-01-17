#!/usr/bin/env python3
"""
Test script to verify Supabase connection and list all tables with their contents.
Run this script locally where you have internet access to Supabase.
"""

import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")


def test_connection():
    """Test basic Supabase connection."""
    print("=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)
    print(f"\nURL: {SUPABASE_URL}")
    print(f"Service Key: {SUPABASE_SERVICE_ROLE_KEY[:20]}..." if SUPABASE_SERVICE_ROLE_KEY else "Not set")

    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        print("\n✓ Client created successfully!")
        return client
    except Exception as e:
        print(f"\n✗ Failed to create client: {e}")
        return None


def list_tables(client):
    """List all tables in the public schema."""
    print("\n" + "=" * 60)
    print("DISCOVERING TABLES")
    print("=" * 60)

    # Common table names to try
    common_tables = [
        'users', 'profiles', 'posts', 'items', 'products', 'orders',
        'games', 'scores', 'leaderboard', 'players', 'sessions',
        'arcade', 'jerry', 'high_scores', 'game_scores', 'accounts',
        'settings', 'comments', 'categories', 'tags', 'messages',
        'notifications', 'logs', 'events', 'tasks', 'todos'
    ]

    found_tables = []

    for table in common_tables:
        try:
            result = client.table(table).select('*').limit(1).execute()
            found_tables.append(table)
            print(f"✓ Found table: {table}")
        except Exception as e:
            error_str = str(e).lower()
            if "does not exist" not in error_str and "404" not in error_str and "relation" not in error_str:
                # Only print unexpected errors
                if "403" in error_str or "401" in error_str:
                    continue  # Skip permission errors silently
                print(f"  ? {table}: {e}")

    return found_tables


def show_table_contents(client, tables):
    """Show the contents of all discovered tables."""
    print("\n" + "=" * 60)
    print("TABLE CONTENTS")
    print("=" * 60)

    for table in tables:
        print(f"\n--- {table.upper()} ---")
        try:
            result = client.table(table).select('*').execute()
            data = result.data

            if not data:
                print("  (empty table)")
                continue

            # Get column names from first row
            columns = list(data[0].keys())
            print(f"  Columns: {', '.join(columns)}")
            print(f"  Rows: {len(data)}")
            print()

            # Print first 10 rows
            for i, row in enumerate(data[:10]):
                print(f"  Row {i + 1}:")
                for key, value in row.items():
                    # Truncate long values
                    str_value = str(value)
                    if len(str_value) > 50:
                        str_value = str_value[:50] + "..."
                    print(f"    {key}: {str_value}")
                print()

            if len(data) > 10:
                print(f"  ... and {len(data) - 10} more rows")

        except Exception as e:
            print(f"  Error reading table: {e}")


def main():
    """Main function to run all tests."""
    client = test_connection()
    if not client:
        print("\nFailed to connect. Please check your credentials.")
        return

    tables = list_tables(client)

    if tables:
        print(f"\n✓ Found {len(tables)} table(s): {', '.join(tables)}")
        show_table_contents(client, tables)
    else:
        print("\n⚠ No tables found in the public schema.")
        print("\nThis could mean:")
        print("  1. No tables have been created yet")
        print("  2. Tables exist but aren't exposed via PostgREST")
        print("  3. Row Level Security (RLS) is blocking access")
        print("\nTo create tables, use the Supabase dashboard or run SQL migrations.")


if __name__ == "__main__":
    main()
