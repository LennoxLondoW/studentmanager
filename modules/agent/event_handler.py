# type checking to prevent ircular importations
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from modules.agent.agent import agent

from openai.types.beta.threads import Text # text type from
from typing_extensions import override # overiding functions
import json # loading arguments to dictionary during function calling
from openai import AssistantEventHandler # event handler class to extend its properties
from modules.data.tools import add_new_student,delete_student,list_students # tools for our agent 

class EventHandler(AssistantEventHandler):
    # tools for our agent to use during the function calling 
    available_functions = {
        "add_new_student": add_new_student,
        "delete_student": delete_student,
        "list_students": list_students
    }


    def __init__(self, instance : agent ): #
        super().__init__()
        self.instance = instance

     # when an event is triggured, we need to give the agent the required tool 
    @override
    def on_event(self, event):
      # Retrieve events that are denoted with 'requires_action'
      # since these will have our tool_calls
      if event.event == 'thread.run.requires_action':
        run_id = event.data.id  # Retrieve the run ID from the event data
        self.handle_requires_action(event.data, run_id)
    

    def handle_requires_action(self, data, run_id):
    #   store the outputs 
      tool_outputs = []
    #   check all the tools requiring actions 
      for tool in data.required_action.submit_tool_outputs.tool_calls:
        if tool.function.name in self.available_functions:
            arguments = json.loads(tool.function.arguments)
            if "timestamp" in arguments:
               arguments.pop("timestamp")
            function_response = self.available_functions[tool.function.name](**arguments)
            tool_outputs.append({
                "tool_call_id": tool.id,
                "output": function_response
            })
      
      # Submit all tool_outputs at the same time
      self.submit_tool_outputs(tool_outputs, run_id)
    

    def submit_tool_outputs(self, tool_outputs, run_id):
      # Use the submit_tool_outputs_stream helper
      with self.instance.client.beta.threads.runs.submit_tool_outputs_stream(
        thread_id=self.current_run.thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs,
        event_handler=EventHandler(self.instance),
      ) as stream:
        stream.until_done()

    
    @override
    def on_text_done(self, text: Text) -> None:
        self.instance.streaming =  False
    
    @override
    def on_text_delta(self, delta, snapshot):
        self.instance.final_agent_output += delta.value
    

    @override
    def on_tool_call_created(self, tool_call):
        self.instance.final_agent_output += f"\n__________________________________________________\n Function called: {tool_call.function.name} \n"
    
    

 