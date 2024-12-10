from fastapi import HTTPException
import openai
import json
from app.assistance.assistant import Assistant
from app.constant.config import OPENAPI_KEY
from fastapi import status

class ThreadManager:
    def __init__(self, session: dict):
        self.client = openai.OpenAI(api_key=OPENAPI_KEY)
        self.thread = None
        self.session = session

    def create_thread(self):
        print("is thread_id in self.session: ", 'thread_id' in self.session)
        if 'thread_id' not in self.session:
            thread_obj = self.client.beta.threads.create()
            self.session['thread_id'] = thread_obj.id
            self.thread = thread_obj
        else:
            self.retrieve_thread(thread_id= self.session['thread_id'])
    
    def retrieve_thread(self, thread_id):
        self.thread = self.client.beta.threads.retrieve(thread_id=thread_id)

    def add_message_to_thread(self, role, content):
        if self.thread:
            self.client.beta.threads.messages.create(
                thread_id=self.thread.id, 
                role=role, 
                content=content
        )

    def get_last_message(self):
        messages = self.client.beta.threads.messages.list(thread_id=self.thread.id)
        message_content = messages.data[0].content[0].text
        print("messages.data[0]", messages.data[0])
        annotations = message_content.annotations
        # Remove annotations
        for annotation in annotations:
            message_content.value = message_content.value.replace(annotation.text, '')

        response_message = message_content.value
        return response_message
    
    def run_assistant(self, assistant_id):
        if not self.thread:
            raise HTTPException(
                status_code= status.HTTP_400_BAD_REQUEST, 
                detail="Thread not created")
        
        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=self.thread.id,
            assistant_id=assistant_id,
            timeout = 20
            )
    
        if run.status == 'requires_action' and run.required_action:
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            run = self.call_required_functions(
                run=run, 
                tool_calls=tool_calls
            )
        
        if run.status == 'completed':
            return self.get_last_message()
        elif run.status in ['expired','failed','cancelled','incomplete']:
            raise HTTPException(
                status_code= status.HTTP_501_NOT_IMPLEMENTED,
                detail= "Sorry I do not have ability to answer this question"
            )

    def call_required_functions(self, run, tool_calls):
        # Define the list to store tool outputs
        tool_outputs = []
        
        # Loop through each tool in the required action section
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = Assistant.registered_functions.get(function_name)
            if function_to_call:
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                print(f"Function response: {function_response}")
                tool_outputs.append(
                    {
                        "tool_call_id": tool_call.id, 
                        "output": function_response
                    }
                )
        print(f"tool outputs:::: {tool_outputs}")
        # Submit all tool outputs at once after collecting them in a list
        run = self.client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id= self.thread.id,
            run_id= run.id,
            tool_outputs=tool_outputs,
            timeout=20
        )
        return run