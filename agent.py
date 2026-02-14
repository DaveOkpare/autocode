from pydantic_ai import (
    Agent,
    DeferredToolRequests,
    Tool,
)

from prompts import coding_instruction, initializer_instruction, planning_instruction
from schemas import Plan
from tools import Tools

model = "openai:gpt-5-mini"

planning_agent = Agent(
    model=model,
    instructions=planning_instruction,
    output_type=Plan | DeferredToolRequests,
    tools=[
        Tool(function=Tools.approve, requires_approval=True),
        Tool(function=Tools.ask_followup, requires_approval=True),
    ],
)

initializer_agent = Agent(
    instructions=initializer_instruction,
    model=model,
    tools=[Tools.read_file, Tools.write_file, Tools.execute],
)

coding_agent = Agent(
    instructions=coding_instruction,
    model=model,
    tools=[
        Tools.read_file,
        Tools.write_file,
        Tools.execute,
        Tools.edit_file,
        Tools.list_files,
        Tools.search_files,
    ],
    model_settings={"parallel_tool_calls": True},
)
