#!/usr/bin/env python3
"""
Script to get Pulumi outputs and update .env file
Run this after deploying with Pulumi to get the connection strings
"""
import subprocess
import json
import os
from pathlib import Path

def get_pulumi_outputs():
    """Get Pulumi stack outputs"""
    try:
        result = subprocess.run(
            ["pulumi", "stack", "output", "--json"],
            cwd="pulumi",
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error getting Pulumi outputs: {e}")
        print(f"stderr: {e.stderr}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing Pulumi outputs: {e}")
        return None

def get_storage_connection_string(resource_group_name, storage_account_name):
    """Get storage account connection string from Azure"""
    try:
        result = subprocess.run(
            [
                "az", "storage", "account", "show-connection-string",
                "--resource-group", resource_group_name,
                "--name", storage_account_name,
                "--query", "connectionString",
                "--output", "tsv"
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting storage connection string: {e}")
        return None

def update_env_file(outputs):
    """Update .env file with Pulumi outputs"""
    env_file = Path(".env")
    
    # Read existing .env if it exists
    env_vars = {}
    if env_file.exists():
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key] = value
    
    # Get storage connection string
    if "resource_group_name" in outputs and "storage_account_name" in outputs:
        print("Getting storage connection string from Azure...")
        conn_str = get_storage_connection_string(
            outputs["resource_group_name"],
            outputs["storage_account_name"]
        )
        if conn_str:
            env_vars["AZURE_STORAGE_CONNECTION_STRING"] = conn_str
            env_vars["AZURE_STORAGE_CONTAINER"] = "website-content"
            print("✓ Storage connection string updated")
    
    # Update web app URL if available
    if "web_app_url" in outputs:
        print(f"Web app URL: {outputs['web_app_url']}")
    
    # Write updated .env file
    with open(env_file, "w") as f:
        f.write("# Environment variables\n")
        f.write("# Generated/updated from Pulumi outputs\n\n")
        
        # Write Auth0 vars (keep existing or use defaults)
        f.write("# Auth0 Configuration\n")
        f.write(f"AUTH0_DOMAIN={env_vars.get('AUTH0_DOMAIN', 'your-auth0-domain.auth0.com')}\n")
        f.write(f"AUTH0_AUDIENCE={env_vars.get('AUTH0_AUDIENCE', 'your-api-identifier')}\n\n")
        
        # Write Azure Storage vars
        f.write("# Azure Storage Configuration\n")
        if "AZURE_STORAGE_CONNECTION_STRING" in env_vars:
            f.write(f"AZURE_STORAGE_CONNECTION_STRING={env_vars['AZURE_STORAGE_CONNECTION_STRING']}\n")
        else:
            f.write("# AZURE_STORAGE_CONNECTION_STRING=your-connection-string-here\n")
        
        f.write(f"AZURE_STORAGE_CONTAINER={env_vars.get('AZURE_STORAGE_CONTAINER', 'website-content')}\n\n")
        
        # Write app settings
        f.write("# Application Settings\n")
        f.write(f"ENVIRONMENT={env_vars.get('ENVIRONMENT', 'development')}\n")
        f.write(f"DEBUG={env_vars.get('DEBUG', 'True')}\n")
    
    print(f"✓ Updated {env_file}")

if __name__ == "__main__":
    print("Getting Pulumi outputs...")
    outputs = get_pulumi_outputs()
    
    if outputs:
        print("Pulumi outputs:")
        for key, value in outputs.items():
            print(f"  {key}: {value}")
        
        print("\nUpdating .env file...")
        update_env_file(outputs)
        print("\n✓ Done! You can now use the .env file for local development.")
    else:
        print("Failed to get Pulumi outputs. Make sure:")
        print("  1. You're in the project root directory")
        print("  2. Pulumi stack is deployed")
        print("  3. You're logged into Azure CLI (az login)")

