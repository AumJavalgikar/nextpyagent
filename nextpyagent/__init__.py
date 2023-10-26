import os
from dotagent.agent.base_agent import BaseAgent
from agents.utils import initialize_dotagent_client
from dotagent import compiler
from dotagent.compiler import Program
from pathlib import Path
from dotenv import load_dotenv

load_dotenv('secrets/secrets.env')
api_key = os.getenv('OPENAI_API_KEY')


class NextPyAgent(BaseAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (llm := kwargs.get('llm')) is None:
            llm = compiler.llms.OpenAI(model='gpt-3.5-turbo-16k', api_key=api_key)

        template = Path(f'./templates/nextpyagent.hbs').read_text()
        self.compiler: Program = compiler(template=template, llm=llm, memory=None, async_mode=True, **kwargs)
        self.output_key = 'components'
