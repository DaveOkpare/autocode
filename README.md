# Autonomous Coding

> **Work in progress** — this project is under active development and not yet ready for production use.

An autonomous coding agent framework built with [pydantic-ai](https://ai.pydantic.dev/). It takes a project idea from natural language, creates a detailed specification, then autonomously implements it across multiple sessions — no human intervention needed after the initial plan is approved.

## How It Works

1. **Planning Phase** — A planning agent clarifies requirements through follow-up questions, then generates a structured project specification (`app_spec.md`) covering tech stack, database schema, API endpoints, UI layout, and implementation steps.

2. **Coding Phase** — Coding agents pick up the spec and build it incrementally. Each agent session reads `progress.json` to understand what's been done, works on the next task, commits progress, and leaves notes for the following session. Context window limits are tracked so agents commit and hand off cleanly before running out of context.

## Setup

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
uv run python agent.py
```

## Project Structure

```
agent.py      — Planning agent with human-in-the-loop approval
prompts.py    — System instructions for planning, initializer, and coding agents
tools.py      — File operations and persistent bash session for coding agents
schemas.py    — Pydantic models defining the plan structure
utils.py      — Plan-to-markdown converter
skills/       — Loadable skill files (e.g., playwright-cli) for coding agents
```
