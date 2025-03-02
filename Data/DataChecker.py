import sqlite3
import os

def print_database_structure(db_path):
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        if not tables:
            print("No tables found in the database.")
            return
            
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if not columns:
                print("  No columns found.")
            else:
                print("  {:<5} {:<20} {:<10}".format("ID", "Column Name", "Data Type"))
                print("  {:<5} {:<20} {:<10}".format("-"*2, "-"*20, "-"*10))
                
                for col in columns:
                    col_id, col_name, col_type = col[0], col[1], col[2]
                    print("  {:<5} {:<20} {:<10}".format(col_id, col_name, col_type))
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    db_path = r"C:\Users\raine\OneDrive\Dokumente\Uni\ScientificProgramming\Chefkoch\Data\crawled_data.db"
    print_database_structure(db_path)
