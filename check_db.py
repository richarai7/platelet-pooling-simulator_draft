import sqlite3

conn = sqlite3.connect('scenarios.db')

# Check tables
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables in scenarios.db:")
for t in tables:
    print(f"  - {t[0]}")

# Count scenarios
cursor = conn.execute("SELECT COUNT(*) FROM scenarios")
count = cursor.fetchone()[0]
print(f"\nScenarios saved: {count}")

# Show any scenarios if they exist
if count > 0:
    cursor = conn.execute("SELECT id, name, description FROM scenarios")
    print("\nSaved scenarios:")
    for row in cursor.fetchall():
        print(f"  ID {row[0]}: {row[1]} - {row[2]}")
else:
    print("\nNo scenarios saved yet.")
    print("\nTo save a scenario:")
    print("  1. Run a simulation in the UI")
    print("  2. Click 'Save Scenario' button")
    print("  3. Give it a name and description")

conn.close()
