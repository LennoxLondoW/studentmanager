import openai

class agent_params:
    client = openai.OpenAI()
    model = "gpt-4o"  
    agent_error = "I am unable to process your request, please try again." # stores any errors encountered
    tried = False # prevent infinite creating of tables 


    not_agent = "No assistant found with id" # if agent does not exist
    active_runs = ["Can't add messages to", "already has an active"]

    # assistant id 
    agent_id = None
    # the actual thrread to use 
    thread_id = None
    # the current run id
    run_id = None
    # assistant name 
    agent_name = "Lenntecs Student Manager"
    # to store output of the agent from streaming 
    final_agent_output = ""
    # this holds the thread chats so that messages can be transfered to another thread 
    chat = []
    # id for the user to create a unique thread for them 
    user_id = None
    # table to store assistants 
    agent_table = "lenntecs_assistants"
    # table to store threads and runs  
    threads_and_runs_table = "lenntecs_threads_and_runs"

    instructions = "You are an exceptional student manager, responsible for onboarding, listing, and removing students from Lenntecs academy. Your task is to efficiently manage these processes, ensuring a smooth experience. "

    tools = [
        # for onboarding a new student 
        {
            "type":"function",
            "function": {
                "name": "add_new_student",
                "description":"Onboards a new student to the system",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "first_name": {
                            "type": "string",
                            "description":"The firstname of the student. If it is not available from the chat, prompt the user to give one."
                        },
                        "last_name": {
                            "type": "string",
                            "description":"The last name of the student. If it is not available from the chat, prompt the user to give one."
                        },
                        "email": {
                            "type": "string",
                            "description":"The email of the student. If it is not available from the chat, prompt the user to give one."
                        }
                    },
                    "required": ["first_name","last_name","email"]
                }
            }
        },
        {
            "type":"function",
            "function": {
                "name": "list_students",
                "description":"Lists all students.",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "timestamp": {
                            "type": "string",
                            "description":"Get the current time"
                        }
                    },
                    "required": ["timestamp"]
                }
            }
        },
        {
            "type":"function",
            "function": {
                "name": "delete_student",
                "description":"Delete a student from the database",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "email": {
                            "type": "string",
                            "description":"The email of the student to delete. If it is not available from the chat, prompt the user to give one."
                        }
                    },
                    "required": ["email"]
                }
            }
        }

    ]