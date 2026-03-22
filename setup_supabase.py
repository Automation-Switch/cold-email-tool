"""
Run this once to set up the Supabase schema.
Usage: .venv-fresh/bin/python setup_supabase.py
"""
from supabase_client import get_supabase

def setup():
    sb = get_supabase()

    # Create user_profiles table
    sb.rpc("create_user_profiles_if_not_exists", {}).execute()

    # Create runs table
    sb.rpc("create_runs_if_not_exists", {}).execute()

    print("Schema setup complete.")

if __name__ == "__main__":
    setup()
