import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

def init_mysql_db():
    """Initialize MySQL database if it doesn't exist"""
    load_dotenv()
    
    # Get database connection details from environment variables
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_NAME = os.getenv("DB_NAME", "angular_migration")
    
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            print(f"Database '{DB_NAME}' created or already exists.")
            
            # Close connection
            cursor.close()
            connection.close()
            print("MySQL connection closed.")
            
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")

if __name__ == "__main__":
    init_mysql_db()
