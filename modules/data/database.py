   
# import dependencies 
import mysql.connector
from dotenv import load_dotenv
import os
# import error logging 
from modules.data.error_log import ErrorLogger

# load the environment variables 
load_dotenv()

# database class that extends the error logging 
class database(ErrorLogger):
    # stores database errors 
    database_error = ""
    conn = None
    cursor = None

    def __init__(self, log_file="error_log.txt"):
        super().__init__(log_file)
        self.db_config = {
            'host': os.environ.get('server'),
            'user': os.environ.get('user'),
            'password': os.environ.get('password'),
            'database': os.environ.get('database'),
        }
    
    # make connection to database 
    def make_connection (self) -> bool:
        if self.conn is None or self.cursor is None:
            try:
                self.conn = mysql.connector.connect(**self.db_config)
                self.cursor = self.conn.cursor(dictionary=True)
                return True
            except Exception as e:
                self.log_error(e)
                self.database_error = "Could not establish connection to the database."
                return False
        
        return True
    
    # close connection to database 
    def close_connection(self):
        try:
            if self.cursor is not None:
                self.cursor.close()
                self.cursor = None
            
            if self.conn is not None:
                self.conn.close()
                self.conn = None

        except Exception as e:
            self.log_error(e)
    
    def table_doenst_exist(self, error: str, table_name: str)-> bool:
        return f"Table '{self.db_config['database']}.{table_name}' doesn't exist" in error