import os
from dotagent.agent.base_agent import BaseAgent
from dotagent import compiler
from dotagent.compiler import Program
from pathlib import Path
from dotenv import load_dotenv
import json
import yaml
from typing import List, Dict


load_dotenv('secrets/secrets.env')
api_key = os.getenv('OPENAI_API_KEY')


class AgentResponse:
    def __init__(self, compiler_output):
        """
        Encapsulates the json response from the agent
        """
        output = json.loads(compiler_output)
        self.type = output.get('response_type')
        self.generated_components = output.get('generated_components')
        self.files_requested = output.get('files_requested')
        self.file_access_reason = output.get('file_access_reason')


class Component:
    def __init__(self, component_description):
        """
        Encapsulate the component from the AgentResponse
        """
        self.component_code = component_description


class NextPyAgent(BaseAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (llm := kwargs.get('llm')) is None:
            llm = compiler.llms.OpenAI(model='gpt-4', api_key=api_key)

        template = Path(f'./templates/nextpyagent.hbs').read_text()
        self.compiler: Program = compiler(template=template, llm=llm, memory=None)
        self.output_key = 'components'
        self.file_list = []

        components_dir = Path('skeletons/nextpy/components')
        for glob in components_dir.rglob("*.yaml"):
            self.file_list.append(f'{glob.parent}/{glob.name}')

        self.file_information: List[Dict] = []

        # todo - Complete this response format to get a json response from the agent
        self.response_format = '''{ 
        "response_type" : "generate_components"/"request_file_access",
        "generated_components" : [
        "```code that generates required component```",
        "```component 2```",
        "```component 3```"
        ],
        "files_requested" : [
        "path/to/file1.yaml",
        "path/to/file2.yaml"
        ],
        "file_access_reason" : "I want access to these files because..",
        "generate_component_reason": "I have generated the component component_name because I have access to it's .yaml file path/to/.yaml file"
        }
        '''

    def parse_file_information(self) -> str:
        """
        Returns a formatted string with filename, file contents of each file, which will go into the prompt
        """
        nl = '\n'
        return '\n'.join([f"File name : \n{file_info['file_name']}{nl}File Contents :{nl} {file_info['file_contents']}{nl}" for file_info in self.file_information])

    def add_file_information(self, file_names) -> None:
        """
        Adds file information to self.file_information as
        dicts in the format {"file_name" : "name of file", "file_content" : "contents of file"}
        """
        for file_path in file_names:
            file_path = Path(file_path)
            with open(file_path) as f:
                file_contents = f.read()
            self.file_information.append({'file_name': str(file_path), 'file_contents': file_contents})

    def run(self, component_description):
        while True:
            output = self.compiler(file_list='List of all files :\n' + '\n'.join(self.file_list),
                                   file_information='No file information yet..' if len(self.file_information) == 0 else self.parse_file_information(),
                                   response_format=self.response_format, component_description=component_description, silent=True, from_agent=True)
            print(output)
            output = output.get('response')
            response = AgentResponse(output)
            if response.type == 'component_generate':
                return generate_components(response)
            else:
                self.add_file_information(response.files_requested)


def generate_components(response: AgentResponse) -> List[Component]:
    """
    Returns a list of components generated from the AgentResponse object
    """
    return [Component(component) for component in response.generated_components]