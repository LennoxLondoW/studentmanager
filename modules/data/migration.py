from modules.data.database import database # database connection 

class migration(database):
    create_table_error = "Error occured while creating table: please try again"
    student_table="lenntecs_students"

    def __init__(self, log_file="error_log.txt"):
        super().__init__(log_file)
    

    def create_student_tables(self)->bool:
        try:
            if self.make_connection():
                agents_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.student_table} (
                    email VARCHAR(50) PRIMARY KEY UNIQUE, 
                    first_name VARCHAR(50) NULL, 
                    last_name VARCHAR(50) NULL, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """


                self.cursor.execute(agents_table_sql)                
                self.conn.commit()
                self.close_connection()
                return True
            raise ValueError(self.database_error)
        except Exception as e:
            self.close_connection()
            self.log_error(e)
            return False