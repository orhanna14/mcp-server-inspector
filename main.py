#!/usr/bin/env python3
"""
MCP Server Inspector Tool
Launches the MCP inspector to test and debug MCP servers.
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path


def get_inspector_proxy_address():
    """Get the inspector proxy address for local development."""
    # For local development, we'll use localhost
    return "http://localhost:6277"


def launch_inspector():
    """Launch the MCP inspector with the research server."""
    print("🚀 Launching MCP Server Inspector...")
    
    # Check if we're in the right directory
    project_dir = Path(__file__).parent
    mcp_project_dir = project_dir / "mcp_project"
    
    if not mcp_project_dir.exists():
        print("❌ Error: mcp_project directory not found!")
        print("Please make sure you're in the correct directory.")
        return
    
    # Change to mcp_project directory
    os.chdir(mcp_project_dir)
    
    # Install dependencies if needed
    print("📦 Installing dependencies...")
    try:
        subprocess.run(["uv", "sync"], check=True, capture_output=True)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return
    
    # Launch the inspector
    print("🔧 Starting MCP Inspector...")
    print("This will open the inspector in your browser.")
    print("Press Ctrl+C to stop the inspector when done.")
    
    try:
        # Launch the inspector using npx
        inspector_cmd = [
            "npx", "@modelcontextprotocol/inspector", 
            "uv", "run", "python3", "research_server.py"
        ]
        
        print(f"Running: {' '.join(inspector_cmd)}")
        subprocess.run(inspector_cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Inspector stopped by user.")
    except FileNotFoundError:
        print("❌ Error: npx not found. Please install Node.js and npm first.")
        print("You can install Node.js from: https://nodejs.org/")
    except Exception as e:
        print(f"❌ Error launching inspector: {e}")


def main():
    """Main entry point."""
    print("=" * 50)
    print("🔍 MCP Server Inspector Tool")
    print("=" * 50)
    
    # Get the inspector proxy address
    proxy_address = get_inspector_proxy_address()
    print(f"📡 Inspector Proxy Address: {proxy_address}")
    print()
    
    # Launch the inspector
    launch_inspector()


if __name__ == "__main__":
    main()
