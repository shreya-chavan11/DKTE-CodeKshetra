import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shreya@1106", # Use your Workbench password
        database="breathcoder_db"
    )
    cursor = db.cursor()
    
    # Fetch all records
    cursor.execute("SELECT * FROM patient_diagnostics")
    results = cursor.fetchall()

    print(f"{'ID':<5} | {'Name':<15} | {'Status':<15} | {'Risk':<10}")
    print("-" * 50)
    for row in results:
        # row[0] is ID, row[1] is Name, row[7] is Status, row[6] is Probability
        print(f"{row[0]:<5} | {row[1]:<15} | {row[7]:<15} | {row[6]:<10}")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'db' in locals() and db.is_connected():
        db.close()