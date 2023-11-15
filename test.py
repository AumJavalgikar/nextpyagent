from nextpyagent import NextPyAgent

agent = NextPyAgent()

component = agent.run('Create a popup on the screen that asks whether user wants to place the order and accept and cancel buttons')
print(component.component_description)