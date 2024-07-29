# import dependencies 
from modules.data.migration import migration

class student(migration):
    # prevent infinite creation of tables if they dont exist 
    tried : bool = False
    # default error 
    student_error : str = "Error! Something unexpected as occured."

    def __init__(self, log_file="error_log.txt"):
        super().__init__(log_file)
    
    # function to add a new student into the database 
    def add_student(self, first_name : str, last_name : str, email : str)->bool:
        try:
            if self.make_connection():
                sql = f"INSERT IGNORE INTO {self.student_table} (first_name, last_name, email) VALUES(%s, %s, %s)"
                self.cursor.execute(sql, (first_name, last_name, email))
                # we need to commit 
                self.conn.commit()
                self.close_connection()
                return True
            self.student_error = self.migration_error
            return False
        except Exception as e:
            # if table hasn't yet been created, we create one and try inserting again
            if not self.tried and self.table_doenst_exist(str(e), self.student_table):
                self.tried = True
                return self.create_student_tables() and self.add_student(first_name, last_name, email)
            # there is an error that cant be resolved so we return false and log it 
            self.log_error(e)
            return False
    
    
    # reading the students
    def fetch_all_students(self) -> list:
        try: 
            if not self.make_connection():
                raise ValueError(self.database_error)
            sql = f"SELECT first_name, last_name, email FROM {self.student_table}"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            self.close_connection()
            # we now return the list os students 
            return results
        except Exception as e:
            # if table hasn't yet been created, we create one
            if not self.tried and self.table_doenst_exist(str(e), self.student_table):
                self.tried = True
                self.create_student_tables()
            # there is an error that cant be resolved so we return empty list and log it 
            self.log_error(e)
            return []
    
    # function to delete student 
    def delete_student(self, student_email)->bool:
        try:
            if not self.make_connection():
                raise ValueError(self.database_error)
            sql = f"DELETE FROM {self.student_table} WHERE email=%s"
            self.cursor.execute(sql, (student_email,))
            self.conn.commit()
            self.close_connection()
            return True
        except Exception as e:
            # if table hasn't yet been created, we create one
            if not self.tried and self.table_doenst_exist(str(e), self.student_table):
                self.tried = True
                return self.create_student_tables()
            # there is an error that cant be resolved so we return false and log it 
            self.log_error(e)
            return False