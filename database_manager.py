import mysql.connector

def insert_patient_data(name, age, gender, asthma, smoking, probability, status, ratio):
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Shreya@1106", # Replace with your Workbench password
            database="breathcoder_db"
        )
        cursor = db.cursor()

        sql = """INSERT INTO patient_diagnostics 
                 (patient_name, age, gender, is_asthmatic, smoking_years, risk_probability, status, fev1_fvc_ratio) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        
        values = (name, age, gender, asthma, smoking, probability, status, ratio)

        cursor.execute(sql, values)
        db.commit()
        print("Record inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()