import json # json data handler
from modules.agent.event_handler import EventHandler
from modules.agent.migration import migration
from modules.agent.hash import hash
from dotenv import load_dotenv 
import json

load_dotenv()

class agent(migration, hash):
    streaming = True

    def __init__(self):
        super().__init__()

    # We check if we already have our agent created  
    def get_agent(self) -> bool:
        try:
            if not self.make_connection(): # database failed to connect
                return False
            self.cursor.execute(f"SELECT agent_id FROM {self.agent_table} WHERE agent_name=%s", (self.agent_name,)) 
            agent = self.cursor.fetchone()
            self.close_connection()
            if not agent:
                # here we create a new agent 
                return self.create_agent()
            # a valid agent exists 
            self.agent_id = agent["agent_id"]
            return True
        except Exception as e:
            self.close_connection()
            if self.table_doenst_exist(str(e), self.agent_table) and not self.tried:
                self.tried = True
                # if we succeed in creating table, we create a new agent
                return self.create_agent_tables() and self.create_agent()
                # we need to create the user table 
            else:
                self.log_error(e)
            return False
    
    # creating an agent if they dont exist 
    def create_agent(self) -> bool:
        try:
            agent = self.client.beta.assistants.create(
                name=self.agent_name,
                instructions=self.instructions,
                model=self.model,
                tools=self.tools,
                top_p=0.1
            )

            self.agent_id = agent.id 
            # nullify the dependants 
            self.thread_id = None
            self.run_id = None
            self.chat = []
            # save the state 
            return self.save_agent() and self.save_thread_and_run() # we nullify any threads and runs available we will see it later 
        except Exception as e:
            self.log_error(e)
            return False
    
    # save the agent state 
    def save_agent(self) -> bool:
        try:
            if not self.make_connection():
                return False
            self.cursor.execute(f"""INSERT INTO {self.agent_table} (agent_id, agent_name) VALUES (%s, %s) 
                                    ON DUPLICATE KEY UPDATE agent_id = VALUES(agent_id)""", (self.agent_id, self.agent_name))
            self.conn.commit()
            self.close_connection()
            return True
        except Exception as e:
            self.close_connection()
            if self.table_doenst_exist(str(e), self.agent_table) and not self.tried:
                self.tried = True
                # if we succeed in creating table, we return true 
                return self.create_agent_tables() and self.save_agent()
            self.log_error(e)
            return False
    
    # getting the threads and runs if present 
    def get_thread(self)->bool:
        try:
            if not self.make_connection():
                return False
            sql = f"SELECT thread_id, run_id, chat FROM {self.threads_and_runs_table} WHERE user_id=%s"
            self.cursor.execute(sql, (self.user_id,)) 
            threads_and_runs = self.cursor.fetchone()
            self.close_connection()
            # no thread available so we create one 
            if not threads_and_runs or threads_and_runs['thread_id'] is None:
                return self.create_thread()
            
            self.thread_id = threads_and_runs["thread_id"]
            self.run_id = threads_and_runs["run_id"]
            self.chat = self.get_prev_chats(threads_and_runs)
           
            return True
        except Exception as e:
            self.close_connection()
            if self.table_doenst_exist(str(e), self.threads_and_runs_table) and not self.tried:
                self.tried = True
                # if we succeed in creating table, we create an agent and thread 
                return self.create_agent_tables() and self.create_thread()
            self.log_error(e)
            return False
    
    # get previous chats if available 
    def get_prev_chats(self, prev_object)->list:
        try:
                # Load messgaes from the thread 
            return json.loads(prev_object["chat"])
        except json.JSONDecodeError:
            # If error put an empty list
            return []
    
    # creating a new thread 
    def create_thread(self, messages=None):
        try:
            if messages is None:
                messages= [{"role":"user","content":"Be a reliable assistant"}]
            
            thread = self.client.beta.threads.create(
                    messages=messages
                )

            self.thread_id = thread.id 
            self.run_id = None 
            self.chat = messages
            # save the state 
            return self.save_thread_and_run()
        except Exception as e:
            str_e = str(e)
            if (self.not_agent in str_e) and not self.tried:
                return self.create_agent() and self.create_thread(messages)
            self.log_error(e)
            return False
    # saving a thread to database 
    def save_thread_and_run(self)->bool:
        try:
            if not self.make_connection():
                return False
            
            sql= f"INSERT INTO {self.threads_and_runs_table} (user_id, thread_id, run_id, chat) VALUES(%s, %s, %s, %s) ON DUPLICATE KEY UPDATE thread_id = VALUES(thread_id), run_id = VALUES(run_id), chat = VALUES(chat)"
            chat = json.dumps(self.chat)
            self.cursor.execute(sql, (self.user_id, self.thread_id, self.run_id, chat))
            self.conn.commit()
            self.close_connection()
            return True
        except Exception as e:
            self.close_connection()
            if self.table_doenst_exist(str(e), self.threads_and_runs_table) and not self.tried:
                self.tried = True
                return self.create_agent_tables() and self.save_thread_and_run()
            self.log_error(e)
            return False
    

    # create a new message for the agent 
    def create_message(self, message : str|None) -> bool:
        try:
            if message is None:
                raise ValueError("Message cannot be none")
            
            # there is run in the thread so we cant add new message to the thread, we create a new one 
            if not self.previous_run_done():
                raise ValueError("Can't add messages to")
                
            message = self.client.beta.threads.messages.create(
                    thread_id=self.thread_id,
                    role="user",
                    content=str(message)
                )
            return True
        except Exception as e:
            str_e = str(e)
            if (self.not_agent in str_e) and not self.tried:
                self.tried = True
                return self.create_agent() and self.create_thread() and self.create_message(message)

            if any(run in str_e for run in self.active_runs)  and not self.tried :
                self.tried = True
                return self.create_thread(self.chat) and self.create_message(message)
            self.log_error(e)
            return False
    
    # check if all runs have been cleared 
    def previous_run_done(self) -> bool:
        if self.run_id is None:
            return True
        
        run_status = self.client.beta.threads.runs.retrieve(
            thread_id=self.thread_id, 
            run_id=self.run_id
            )
        return run_status.status in  ["completed", "expired"]
    
    # append message to our chat 
    def append_chat(self, message, role) -> None:
        if message is None or str(message).strip() == "":
            message = "Kindly make me understand more."
        self.chat.append({"role":role,"content":message})
    
    # running agent with stream 
    def run_agent_with_stream(self) -> None:
        with self.client.beta.threads.runs.stream(
            thread_id=self.thread_id,
            assistant_id=self.agent_id,
            instructions="Execute using the available tools",
            event_handler=EventHandler(self),
            top_p=0.1,
            timeout=180
            ) as stream:
            stream.until_done()
            run = stream.get_final_run()
            self.run_id = run.id

    # clossing stream 
    def close_stream(self)->None:
        self.streaming = False
    
    # inlet function to query your agent to do something 
    def ask_agent(self, user_prompt, user_id)->str:
        try:
            if not self.get_agent():
                raise ValueError("Failed to create agent")

            # we set user id based on agent id 
            self.user_id = self.create_hash(user_id + self.agent_id)
            if not self.get_thread():
                raise ValueError("Failed to create thread")


            if not self.create_message(user_prompt):
                raise ValueError("Failed to create message")
                        
            # append the user prompt to our chat 
            self.append_chat(user_prompt, "user")

            # save the chart progress 
            self.save_thread_and_run()

            # ask the agent to stream the output 
            self.run_agent_with_stream()

            self.append_chat(self.final_agent_output, "assistant")

            self.save_thread_and_run()
            # close the stream 
            self.close_stream()
            return self.final_agent_output
        except Exception as e:
            str_e = str(e)
            if (self.not_agent in str_e) and not self.tried:
                 self.tried = True
                 return self.create_agent() and self.ask_agent(user_prompt, user_id)
            # if a thread is clogged 
            if any(run in str_e for run in self.active_runs)  and not self.tried :
                self.tried= True
                return self.create_thread(self.chat) and self.ask_agent(user_prompt, user_id)
            self.close_stream()
            self.log_error(e)
            self.final_agent_output = self.agent_error
            return self.final_agent_output


