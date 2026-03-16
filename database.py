import sqlite3

def get_connection():
    return sqlite3.connect("spendora.db", check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        name TEXT,
        password TEXT
    )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS financial_data (
        email TEXT,
        month TEXT,
        salary REAL,
        rent REAL,
        emi REAL,
        bills REAL,
        food REAL,
        travel REAL,
        entertainment REAL,
        shopping REAL,
        other REAL,
        total_expense REAL,
        savings REAL,
        saving_percentage REAL,
        PRIMARY KEY (email, month)
)
""")
    
    

    conn.commit()
    conn.close()


    