from schemas import Plan


def planning_response_to_markdown(plan: Plan) -> str:
    """Convert a Plan to markdown format."""
    md = "# Project Specification\n\n"
    md += f"## Overview\n{plan.overview}\n\n"
    md += f"## Tech Stack\n{plan.technology_stack}\n\n"

    # Prerequisites
    md += "## Prerequisites\n"
    for req in plan.prerequisites:
        md += f"- {req}\n"
    md += "\n"

    # Core Features
    md += "## Core Features\n"
    for feat in plan.core_features:
        md += f"- {feat}\n"
    md += "\n"

    # Database Schema
    if plan.database_schema:
        md += "## Database Schema\n"
        for table in plan.database_schema:
            md += f"### {table.name}\n"
            for col in table.columns:
                constraints = col.get("constraints", "")
                md += f"- **{col['name']}**: {col['type']}"
                if constraints:
                    md += f" ({constraints})"
                md += "\n"
            md += "\n"

    # API Endpoints
    if plan.api_endpoints_summary:
        md += "## API Endpoints\n"
        for endpoint in plan.api_endpoints_summary:
            md += f"- `{endpoint.method} {endpoint.path}`\n"
        md += "\n"

    # UI Layout
    if plan.ui_layout:
        md += "## UI Layout\n"
        for layout in plan.ui_layout:
            md += f"- {layout}\n"
        md += "\n"

    # Design System
    if plan.design_system:
        md += "## Design System\n"
        for design in plan.design_system:
            md += f"- {design}\n"
        md += "\n"

    # Key Interactions
    md += "## Key Interactions\n"
    for interaction in plan.key_interactions:
        md += f"### {interaction.feature}\n"
        for step in interaction.workflow:
            md += f"- {step}\n"
        md += "\n"

    # Implementation Steps
    md += "## Implementation Steps\n"
    for impl in plan.implementation_steps:
        md += f"### {impl.task_name}\n"
        for step in impl.implementation_steps:
            md += f"- {step}\n"
        md += "\n"

    # Success Criteria
    md += "## Success Criteria\n"
    for criteria in plan.success_criteria:
        md += f"- {criteria}\n"

    return md
