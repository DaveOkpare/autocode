import json
from pathlib import Path

import logfire
from pydantic_ai import (
    Agent,
    DeferredToolRequests,
    Tool,
)

from prompts import coding_instruction, initializer_instruction, planning_instruction
from schemas import AgentDeps, Plan
from tools import BashSession, Tools

logfire.configure()
logfire.instrument_pydantic_ai()

model = "openai:gpt-5-mini"

session = BashSession()
tools = Tools(session)

planning_agent = Agent(
    model=model,
    instructions=planning_instruction,
    output_type=Plan | DeferredToolRequests,
    tools=[
        Tool(function=tools.approve, requires_approval=True),
        Tool(function=tools.ask_followup, requires_approval=True),
    ],
)

initializer_agent = Agent(
    instructions=initializer_instruction,
    model=model,
    tools=[tools.read_file, tools.write_file, tools.execute],
    deps_type=AgentDeps,
)

coding_agent = Agent(
    instructions=coding_instruction,
    model=model,
    tools=[
        tools.read_file,
        tools.write_file,
        tools.execute,
        tools.edit_file,
        tools.list_files,
        tools.search_files,
    ],
    model_settings={"parallel_tool_calls": True},
    deps_type=AgentDeps,
)
