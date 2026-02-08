import json
from pathlib import Path

from pydantic_ai import (
    Agent,
    DeferredToolRequests,
    DeferredToolResults,
    ToolApproved,
    ToolDenied,
)

from prompts import planning_instruction
from schemas import Plan
from utils import planning_response_to_markdown

planning_agent = Agent(
    model="openai:gpt-5-mini",
    instructions=planning_instruction,
    output_type=Plan | DeferredToolRequests,
)


@planning_agent.tool_plain(requires_approval=True)
def ask_followup(questions: list[str]) -> str:
    """Ask clarifying questions to resolve ambiguities in the user's requirements.
    Limit questions to 3 per call to avoid overwhelming the user.

    Use this tool when:
    - Requirements are unclear or missing critical details
    - Multiple technical approaches are possible and user preference is needed
    - Scope boundaries are undefined

    Args:
        questions: A list of specific questions to ask the user. Each question should target a single clarification point.
    """
    return "The user has clarified their requirements."


@planning_agent.tool_plain(requires_approval=True)
def approve(plan: str) -> str:
    """Present the complete implementation plan to the user for approval.

    Use this tool when:
    - All ambiguities have been resolved
    - The plan is comprehensive and ready for autonomous execution
    - You need user confirmation before finalizing

    Args:
        plan: A concise, well-structured summary of the complete plan. Include:
              - Project overview and goals
              - Technology stack decisions
              - Key architectural decisions
              - Core features and implementation approach
              - Major milestones or phases

              Keep it digestible (1-2 pages max) while accurately representing the full detailed plan.
    """
    return "The user has approved the plan."


def run_planning_agent(request, project_dir: Path):
    """Present the complete implementation plan to the user for approval."""
    result = planning_agent.run_sync(request)
    output = result.output
    messages = result.all_messages()

    while isinstance(output, DeferredToolRequests):
        results = DeferredToolResults()
        approvals = output.approvals

        for approval in approvals:
            _result = False
            if approval.tool_name == "approve":
                response = input(
                    f"{
                        approval.args.get('plan')
                        if isinstance(approval.args, dict)
                        else json.loads(approval.args if approval.args else '').get(
                            'plan', ''
                        )
                    }"
                )
                if response.lower() == "no":
                    rejections = input("What should we do instead?")
                    _result = ToolDenied(rejections)
                else:
                    _result = ToolApproved()
            elif approval.tool_name == "ask_followup":
                questions = (
                    approval.args.get("questions", [])
                    if isinstance(approval.args, dict)
                    else json.loads(approval.args if approval.args else "").get(
                        "questions", []
                    )
                )
                questions_text = "\n".join(
                    [f"{i + 1}. {q}" for i, q in enumerate(questions)]
                )
                response = input(f"{questions_text}\n\n")
                _result = ToolApproved(override_args={"answers": response})

            results.approvals[approval.tool_call_id] = _result

        output = planning_agent.run_sync(
            "Now continue with the user's feedback",
            message_history=messages,
            deferred_tool_results=results,
        )
        messages = output.all_messages()
        output = output.output

    # Convert the plan to markdown format
    markdown_plan = planning_response_to_markdown(output)

    if not project_dir.exists():
        project_dir.mkdir(parents=True)

    # Save the markdown plan to a file
    plan_file = project_dir / "plan.md"
    with open(plan_file, "w") as f:
        f.write(markdown_plan)
