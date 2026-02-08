from typing import Optional

from pydantic import BaseModel, Field


class Column(BaseModel):
    name: str = Field(description="Column name (e.g., 'id', 'email', 'created_at')")
    type: str = Field(
        description="Column data type (e.g., 'VARCHAR(255)', 'INTEGER', 'TIMESTAMP', 'BOOLEAN')"
    )
    constraints: Optional[str] = Field(
        default=None,
        description="Optional column constraints (e.g., 'PRIMARY KEY', 'NOT NULL', 'UNIQUE', 'FOREIGN KEY')",
    )


class DBTable(BaseModel):
    name: str = Field(description="The database table name (e.g., 'users', 'orders')")
    columns: list[Column] = Field(
        description="List of column definitions with name, type, and optional constraints"
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
    key_interactions: list[Interaction] = Field(
        description="Critical user workflows to test the system. Define end-to-end scenarios that verify core functionality works correctly. Include for any project with user-facing features.",
    )
    implementation_steps: list[Implementation] = Field(
        description="Ordered implementation phases breaking down the project into manageable tasks. Each task should have concrete, actionable steps. Essential for projects requiring staged development.",
    )
    success_criteria: list[str] = Field(
        description="Measurable criteria that define project completion. Include functional requirements (all features work), quality requirements (test coverage, performance), and user experience requirements (responsive design, accessibility). Be specific and testable.",
    )
