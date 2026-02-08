import json
from typing import Optional

from pydantic import BaseModel, Field
from pydantic_ai import (
    Agent,
    DeferredToolRequests,
    DeferredToolResults,
    ToolApproved,
    ToolDenied,
)


class DBTable(BaseModel):
    name: str = Field(description="The database table name (e.g., 'users', 'orders')")
    columns: list[dict[str, str]] = Field(
        description="List of column definitions. Each dict must have 'name' (column name) and 'type' (data type, e.g., 'VARCHAR(255)', 'INTEGER', 'TIMESTAMP'). May include optional 'constraints' key (e.g., 'PRIMARY KEY', 'NOT NULL', 'UNIQUE')."
    )


class APIEndpoint(BaseModel):
    path: str = Field(
        description="The API endpoint path (e.g., '/api/users', '/api/auth/login')"
    )
    method: str = Field(description="The HTTP method (GET, POST, PUT, PATCH, DELETE)")


class Interaction(BaseModel):
    feature: str = Field(
        description="The specific feature name to be tested (e.g., 'User Registration', 'Shopping Cart Checkout')"
    )
    workflow: list[str] = Field(
        description="Step-by-step testing workflow from user perspective. Each step should be actionable (e.g., '1. Navigate to /signup', '2. Fill in email field', '3. Click submit button', '4. Verify success message appears')"
    )


class Implementation(BaseModel):
    task_name: str = Field(
        description="Descriptive name of the implementation task (e.g., 'Setup Database Schema', 'Implement User Authentication API')"
    )
    implementation_steps: list[str] = Field(
        description="Ordered list of concrete implementation steps. Each step must be specific and actionable (e.g., '1. Install bcrypt package for password hashing', '2. Create User model in models/user.py with email and password_hash fields', '3. Implement POST /api/auth/register endpoint')"
    )


class Plan(BaseModel):
    overview: str = Field(
        description="Concise project overview (2-4 sentences). State what the system does, who it's for, and its primary value proposition."
    )
    technology_stack: str = Field(
        description="Complete technology stack specification organized by category. Include specific versions where critical. Example format: 'Frontend: React 18, TypeScript 5.x, Tailwind CSS | Backend: Python 3.11, FastAPI | Database: PostgreSQL 15 | Auth: JWT tokens | Deployment: Docker, AWS'. Adapt categories to project needs."
    )
    prerequisites: list[str] = Field(
        description="Environment setup requirements before development can begin. Include: software installations (Node.js 18+, Python 3.11+), account setups (GitHub, cloud provider), API keys needed, and system requirements. Be specific with versions."
    )
    core_features: list[str] = Field(
        description="List of essential features that define the system's functionality. Each feature should be user-facing and clearly describe what users can do (e.g., 'User registration and authentication', 'Create and manage product listings', 'Real-time chat between users')."
    )
    database_schema: Optional[list[DBTable]] = Field(
        default=None,
        description="Database schema specification. Include all tables with columns, data types, and constraints. Omit only if the project genuinely requires no database (static sites, pure frontend apps).",
    )
    api_endpoints_summary: Optional[list[APIEndpoint]] = Field(
        default=None,
        description="Complete list of API endpoints with paths and HTTP methods. Omit only if there's no backend API (static sites, pure frontend apps).",
    )
    ui_layout: Optional[list[str]] = Field(
        default=None,
        description="UI component structure and page layouts. List all major views/pages and their key components (e.g., 'Login page: email input, password input, submit button, forgot password link', 'Dashboard: sidebar navigation, header with user menu, main content area'). Omit only for backend-only projects.",
    )
    design_system: Optional[list[str]] = Field(
        default=None,
        description="Design system specifications: color palette, typography, spacing scale, component variants, and styling approach (CSS-in-JS, Tailwind, CSS modules). Omit only for backend-only projects.",
    )
    key_interactions: Optional[list[Interaction]] = Field(
        default=None,
        description="Critical user workflows to test the system. Define end-to-end scenarios that verify core functionality works correctly. Include for any project with user-facing features.",
    )
    implementation_steps: Optional[list[Implementation]] = Field(
        default=None,
        description="Ordered implementation phases breaking down the project into manageable tasks. Each task should have concrete, actionable steps. Essential for projects requiring staged development.",
    )
    success_criteria: Optional[list[str]] = Field(
        default=None,
        description="Measurable criteria that define project completion. Include functional requirements (all features work), quality requirements (test coverage, performance), and user experience requirements (responsive design, accessibility). Be specific and testable.",
    )


planning_instruction = """
## YOUR ROLE - PLANNING AGENT

You are a software architect and planning specialist tasked with creating comprehensive implementation plans for LONG-RUNNING AUTONOMOUS DEVELOPMENT PROCESSES.

### CRITICAL REQUIREMENTS

**This plan will be executed by autonomous agents with NO human intervention after approval.**

Your plan must be:
1. **Complete**: Capture every element of the user's requirements
2. **Detailed**: Include specific technical decisions, not vague descriptions
3. **Unambiguous**: Clear enough that an agent can implement without clarification
4. **Structured**: Organized logically with implementation steps, success criteria, and testing workflows

### AVAILABLE TOOLS

You have access to:
- `ask_followup`: Ask clarifying questions BEFORE finalizing the plan
- `approve`: Present the complete plan summary for user review and approval. This should be a digestible overview that accurately represents the final detailed plan.

### YOUR PROCESS

1. **Clarify First**: Use `ask_followup` to resolve any ambiguities in requirements
2. **Design Completely**: Create a detailed plan covering all aspects (tech stack, schema, endpoints, UI, workflows)
3. **Specify Implementation**: Break down into actionable steps with clear success criteria
4. **Seek Approval**: Present the final plan for user confirmation

**Remember**: Autonomous agents will execute this plan independently. Every detail matters.
"""

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


if __name__ == "__main__":
    request = input("What are we building?\n\n")
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
    print("Plan:", output)
