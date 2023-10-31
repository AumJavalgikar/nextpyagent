import os
from dotagent.agent.base_agent import BaseAgent
from dotagent import compiler
from dotagent.compiler import Program
from pathlib import Path
from dotenv import load_dotenv
import json
from typing import List, Dict


load_dotenv('secrets/secrets.env')
api_key = os.getenv('OPENAI_API_KEY')


class AgentResponse:
    def __init__(self, compiler_output):
        """todo - complete this class to encapsulate the json response from the agent"""

        output = json.loads(compiler_output)

        pass


class Component:
    def __init__(self, component_description):
        """todo - complete this class to encapsulate the component from the AgentResponse"""
        pass


class NextPyAgent(BaseAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (llm := kwargs.get('llm')) is None:
            llm = compiler.llms.OpenAI(model='gpt-3.5-turbo-16k', api_key=api_key)

        template = Path(f'./templates/nextpyagent.hbs').read_text()
        self.compiler: Program = compiler(template=template, llm=llm, memory=None, async_mode=True)
        self.output_key = 'components'
        self.file_list = []

        components_dir = Path('skeletons/nextpy/components')
        for glob in components_dir.rglob("*.yaml"):
            self.file_list.append(f'skeletons/{glob.parent}/{glob.name}')

        self.file_information: List[Dict] = []

        # todo - Complete this response format to get a json response from the agent
        self.response_format = '''{ 
        "response_type" : "component_generate"/"file_access_request",
        "generated_components" : [
        "```code that generates required component```",
        "```component 2```",
        "```component 3```"
        ],
        "files_requested" : [
        "path/to/file1.yaml",
        "path/to/file2.yaml"
        ]
        }
        '''

    def parse_file_information(self) -> str:
        """todo - return a formatted string with filename, file contents of each file, which will go into the prompt"""
        pass

    def add_file_information(self, file_names) -> None:
        """todo - add file information to self.file_information as
           todo - dicts in the format {"file_name" : "name of file", "file_content" : "contents of file"}"""
        pass

    def run(self, component_description):
        while True:
            output = self.compiler(file_list='files available :\n' + '\n'.join(self.file_list),
                                   file_information='No file information yet..' if len(self.file_information) == 0 else self.parse_file_information(),
                                   component_description=component_description, silent=True, from_agent=True)
            response = AgentResponse(output)

            if response.type == 'component_generate':
                return generate_components(response)
            else:
                self.add_file_information(response.files_requested)


def generate_components(response: AgentResponse) -> List[Component]:
    """todo - return a list of components generated from the AgentResponse object"""
    pass




