from modules.agent.agent import agent


user_id = "lenntecs"
while True:
    user_prompt = input("Prompt: ")
    _agent = agent()
    print(_agent.ask_agent(user_prompt, user_id))