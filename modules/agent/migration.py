from modules.agent.params import agent_params # params 
from modules.data.database import database # database connection 

class migration(database, agent_params):
    create_table_error = "Error occured while creating table: please try again"

    def __init__(self):
        super().__init__()

    def create_agent_tables(self):
        try:
            if self.make_connection():
                # stores the agents required 
                agents_table_sql = f"""
                CREATE TABLE IF NOT EXISTS {self.agent_table} (
                    agent_id VARCHAR(50) PRIMARY KEY UNIQUE, 
                    agent_name VARCHAR(50) UNIQUE, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
                """

                # stores the threads and runs for agents to maintain a single conversion 
                threads_and_runs_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.threads_and_runs_table} (
                        user_id VARCHAR(255) PRIMARY KEY UNIQUE, 
                        thread_id VARCHAR(50) NULL, 
                        run_id VARCHAR(50) NULL, 
                        chat LONGTEXT, 
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    )
                    """


                self.cursor.execute(agents_table_sql)
                self.cursor.execute(threads_and_runs_table_sql)
                
                self.conn.commit()
                self.close_connection()
                return True
            raise ValueError(self.database_error)
        except Exception as e:
            self.close_connection()
            self.log_error(e)
            return False