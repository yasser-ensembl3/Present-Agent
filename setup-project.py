#!/usr/bin/env python3
"""
MiniVault Project Setup Script
==============================
This script automatically creates:
1. A new Notion parent page with all required databases
2. The .env.local file with all credentials and new Notion IDs

Usage:
    python3 setup-project.py "Project Name"

Example:
    python3 setup-project.py "Founder MTL"
"""

import urllib.request
import json
import sys
import os

# =============================================================================
# CONFIGURATION - Edit these values with your credentials
# =============================================================================

CONFIG = {
    # NextAuth
    "NEXTAUTH_SECRET": "your-nextauth-secret-here",

    # Google OAuth
    "GOOGLE_CLIENT_ID": "your-google-client-id.apps.googleusercontent.com",
    "GOOGLE_CLIENT_SECRET": "your-google-client-secret",

    # GitHub OAuth
    "GITHUB_ID": "your-github-oauth-id",
    "GITHUB_SECRET": "your-github-oauth-secret",

    # Notion
    "NOTION_TOKEN": "your-notion-integration-token",
    "NOTION_PARENT_PAGE_ID": "your-notion-parent-page-id",  # Parent page for all projects

    # API Keys
    "OPENAI_API_KEY": "your-openai-api-key",
    "ANTHROPIC_API_KEY": "your-anthropic-api-key",
    "GOOGLE_API_KEY": "your-google-api-key",
    "GOOGLE_AUTH_KEY": "your-google-auth-key",

    # Google Service Account (as single line JSON)
    "GOOGLE_SERVICE_ACCOUNT_KEY": '{"type":"service_account","project_id":"your-project-id","private_key_id":"your-private-key-id","private_key":"your-private-key","client_email":"your-service-account@your-project.iam.gserviceaccount.com","client_id":"your-client-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/your-service-account","universe_domain":"googleapis.com"}',
}

# =============================================================================
# DATABASE SCHEMAS
# =============================================================================

DATABASES = [
    {
        "name": "Tasks",
        "icon": "\U0001F4CB",
        "properties": {
            "Name": {"title": {}},
            "Status": {"rich_text": {}},
            "Priority": {"rich_text": {}},
            "Assignee": {"rich_text": {}},
            "Tags": {"rich_text": {}},
            "Due Date": {"date": {}}
        }
    },
    {
        "name": "Goals",
        "icon": "\U0001F3AF",
        "properties": {
            "Metric Name": {"title": {}},
            "Number": {"number": {"format": "number"}},
            "Last Updated": {"date": {}}
        }
    },
    {
        "name": "Metrics",
        "icon": "\U0001F4CA",
        "properties": {
            "Metric Name": {"title": {}},
            "Number": {"number": {"format": "number"}},
            "Last Updated": {"date": {}}
        }
    },
    {
        "name": "Milestones",
        "icon": "\U0001F3C1",
        "properties": {
            "Name": {"title": {}},
            "Description": {"rich_text": {}},
            "Due Date": {"date": {}},
            "Completion %": {"number": {"format": "number"}}
        }
    },
    {
        "name": "Documents",
        "icon": "\U0001F4DA",
        "properties": {
            "Title": {"title": {}},
            "Description": {"rich_text": {}},
            "URL": {"url": {}},
            "Type": {"rich_text": {}}
        }
    },
    {
        "name": "Feedback",
        "icon": "\U0001F4AC",
        "properties": {
            "Title": {"title": {}},
            "User Name": {"rich_text": {}},
            "Feedback": {"rich_text": {}},
            "Date": {"date": {}}
        }
    }
]

# =============================================================================
# NOTION API FUNCTIONS
# =============================================================================

def notion_request(method, endpoint, data=None):
    """Make a request to the Notion API."""
    url = f"https://api.notion.com/v1/{endpoint}"
    headers = {
        "Authorization": f"Bearer {CONFIG['NOTION_TOKEN']}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers, method=method)
    else:
        req = urllib.request.Request(url, headers=headers, method=method)

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def create_project_page(project_name):
    """Create the main project page in Notion."""
    data = {
        "parent": {"page_id": CONFIG["NOTION_PARENT_PAGE_ID"]},
        "properties": {
            "title": {"title": [{"text": {"content": project_name}}]}
        },
        "icon": {"emoji": "\U0001F680"}
    }
    return notion_request("POST", "pages", data)

def create_database(parent_page_id, db_config):
    """Create a database in Notion."""
    data = {
        "parent": {"page_id": parent_page_id},
        "title": [{"text": {"content": db_config["name"]}}],
        "icon": {"emoji": db_config["icon"]},
        "properties": db_config["properties"]
    }
    return notion_request("POST", "databases", data)

# =============================================================================
# ENV FILE GENERATION
# =============================================================================

def generate_env_file(project_name, project_page_id, database_ids):
    """Generate the .env.local file content."""

    # Fix the service account key - need to unescape the \\n to \n for the actual file
    service_account = CONFIG["GOOGLE_SERVICE_ACCOUNT_KEY"].replace("\\\\n", "\\n")

    return f"""NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET={CONFIG["NEXTAUTH_SECRET"]}
GOOGLE_CLIENT_ID={CONFIG["GOOGLE_CLIENT_ID"]}
GOOGLE_CLIENT_SECRET={CONFIG["GOOGLE_CLIENT_SECRET"]}
GITHUB_ID={CONFIG["GITHUB_ID"]}
GITHUB_SECRET={CONFIG["GITHUB_SECRET"]}
NOTION_TOKEN={CONFIG["NOTION_TOKEN"]}
OPENAI_API_KEY={CONFIG["OPENAI_API_KEY"]}
ANTHROPIC_API_KEY={CONFIG["ANTHROPIC_API_KEY"]}
GOOGLE_API_KEY={CONFIG["GOOGLE_API_KEY"]}
GOOGLE_AUTH_KEY={CONFIG["GOOGLE_AUTH_KEY"]}
GOOGLE_SERVICE_ACCOUNT_KEY={service_account}

# Project Configuration
NEXT_PUBLIC_PROJECT_NAME={project_name}
NEXT_PUBLIC_PROJECT_DESCRIPTION=

# Notion Databases - {project_name}
NEXT_PUBLIC_NOTION_DB_TASKS={database_ids["Tasks"]}
NEXT_PUBLIC_NOTION_DB_GOALS={database_ids["Goals"]}
NEXT_PUBLIC_NOTION_DB_METRICS={database_ids["Metrics"]}
NEXT_PUBLIC_NOTION_DB_MILESTONES={database_ids["Milestones"]}
NEXT_PUBLIC_NOTION_DB_DOCUMENTS={database_ids["Documents"]}
NEXT_PUBLIC_NOTION_DB_FEEDBACK={database_ids["Feedback"]}
NEXT_PUBLIC_NOTION_PROJECT_PAGE_ID={project_page_id}
"""

# =============================================================================
# MAIN
# =============================================================================

def main():
    # Get project name from command line
    if len(sys.argv) < 2:
        print("Usage: python3 setup-project.py \"Project Name\"")
        print("Example: python3 setup-project.py \"Founder MTL\"")
        sys.exit(1)

    project_name = sys.argv[1]
    script_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"\n{'='*60}")
    print(f"  MiniVault Setup - {project_name}")
    print(f"{'='*60}\n")

    # Check if .env.local already exists
    env_path = os.path.join(script_dir, ".env.local")
    if os.path.exists(env_path):
        response = input(".env.local already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)

    # 1. Create project page
    print(f"Creating Notion page '{project_name}'...")
    try:
        page = create_project_page(project_name)
        project_page_id = page["id"].replace("-", "")
        print(f"  \u2705 Page created: {project_page_id}")
    except Exception as e:
        print(f"  \u274C Error creating page: {e}")
        sys.exit(1)

    # 2. Create databases
    database_ids = {}
    for db_config in DATABASES:
        print(f"Creating {db_config['name']} database...")
        try:
            db = create_database(page["id"], db_config)
            db_id = db["id"].replace("-", "")
            database_ids[db_config["name"]] = db_id
            print(f"  \u2705 {db_config['name']}: {db_id}")
        except Exception as e:
            print(f"  \u274C Error creating {db_config['name']}: {e}")
            sys.exit(1)

    # 3. Generate .env.local
    print("\nGenerating .env.local...")
    env_content = generate_env_file(project_name, project_page_id, database_ids)

    with open(env_path, "w") as f:
        f.write(env_content)
    print(f"  \u2705 .env.local created")

    # 4. Summary
    print(f"\n{'='*60}")
    print("  Setup Complete!")
    print(f"{'='*60}")
    print(f"\nNotion page: https://notion.so/{project_page_id}")
    print(f"\nNext steps:")
    print(f"  1. npm install")
    print(f"  2. npm run dev")
    print(f"  3. Open http://localhost:3000")
    print()

if __name__ == "__main__":
    main()
