from pathlib import Path

import questionary
from pydantic_ai import (
    DeferredToolRequests,
    DeferredToolResults,
    ToolApproved,
    ToolDenied,
)
from rich.console import Console

from agent import planning_agent
from schemas import Plan
from utils import format_plan_to_markdown

console = Console()


async def planning_step():
    project_path = Path.cwd() / "project"
    plan_file_path = project_path / "app_spec.md"

    user_input = await questionary.text("Enter your project description: ").ask_async()
    result = await planning_agent.run(user_input)

    messages = result.all_messages()
    output: Plan | DeferredToolRequests = result.output

    while isinstance(output, DeferredToolRequests):
        results = DeferredToolResults()

        for call in output.approvals:
            approval = False

            if call.tool_name == "approve":
                _questions = call.args_as_dict().get("plan", "")
                console.print(_questions)
                choice = await questionary.select(
                    "Do you approve this plan? ", choices=["Yes", "No"]
                ).ask_async()

                if choice == "Yes":
                    approval = True
                else:
                    followup = await questionary.text(
                        "What should agent do instead?: "
                    ).ask_async()
                    approval = ToolDenied(followup)
            elif call.tool_name == "ask_followup":
                _questions = call.args_as_dict().get("questions", "")
                answers = await questionary.form(
                    **{
                        f"{i}": questionary.text(question)
                        for i, question in enumerate(_questions)
                    }
                ).ask_async()

                approval = ToolApproved(
                    override_args={
                        "results": [
                            {"question": q, "answers": a}
                            for q, a in zip(_questions, answers.values())
                        ]
                    }
                )

            results.approvals[call.tool_call_id] = approval

        result = await planning_agent.run(
            user_prompt="Continue with the next step after receiving the answers to the previous questions.",
            message_history=messages,
            deferred_tool_results=results,
        )
        messages = result.all_messages()
        output = result.output

    if isinstance(output, Plan):
        print("Writing project specification to app_spec.md...")
        plan = format_plan_to_markdown(output)
        with open(plan_file_path, "w") as f:
            f.write(plan)


if __name__ == "__main__":
    import asyncio

    asyncio.run(planning_step())
