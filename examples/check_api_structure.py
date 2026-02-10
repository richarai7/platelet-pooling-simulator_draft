"""
ADD MULTI-BATCH TEMPLATE TO API
Makes the multi-batch config available via /templates/platelet-pooling-multi-batch
"""
import sys
from pathlib import Path

# Read the API file
api_file = Path(__file__).parent / "api" / "main.py"
with open(api_file, 'r') as f:
    content = f.read()

# Check if multi-batch endpoint already exists
if "platelet-pooling-multi-batch" in content:
    print("✅ Multi-batch template endpoint already exists!")
    sys.exit(0)

# Find the templates.py file
templates_file = Path(__file__).parent / "api" / "templates.py"

print(f"Checking {templates_file}...")

if not templates_file.exists():
    print(f"❌ {templates_file} not found!")
    print("\nLet me check what's in the api directory...")
    api_dir = Path(__file__).parent / "api"
    print(f"Files in {api_dir}:")
    for f in api_dir.iterdir():
        print(f"  • {f.name}")
else:
    print(f"✅ Found {templates_file}")
