from nextpyagent import NextPyAgent
from fastapi import FastAPI
from dotenv import load_dotenv
load_dotenv('secrets/secrets.env')

app = FastAPI()

agent = NextPyAgent()


@app.get("/getComponent/")
async def read_item(component_description: str):
    result = await agent.arun(component_description=component_description)
    return {"result": result}