from langchain_community.llms import Ollama

from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

import re
import json


class Extractor(object):
    def __init__(self,model="llama3:8b",prompt_content=""):
        """
        Choices in models :
            1. llama3:8b ( 4.7 gb ) , llama3:70b ( 40 gb )
            2. phi3:mini ( 8 billion parameters, 2.4 gb ), phi3:medium ( 14 billion parameters, 7.9 gb )
            3. mistral ( 7 billion parameters, 4.1 gb )
            4. gemma:2b ( 1.7 gb ), gemma:7b ( 5 gb )
        """

        self.default_prompt_content = """Using the given HTML block at the end, extract meaningful information and return in JSON format. And provide the output in JSON format very very strictly."""

        self.prompt_content = prompt_content if prompt_content else self.default_prompt_content
        self.model = model


    def query_ollama(self, html_block, streaming=True):
        if streaming:
            llm = Ollama(model=self.model, callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]))
        else:
            llm = Ollama(model=self.model)

        print('Processing by Llama3 8b model......')
        prompt = f"{self.prompt_content}.The html block is: {html_block}"
        output = llm.invoke(prompt)

        output_json_data = re.search(r'\[.*?\]', output, re.DOTALL).group()
        output_json_data = json.loads(output_json_data)
        return output_json_data