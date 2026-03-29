# Sutureprogram.md Template

> This file instructs the connected Multi-Agent System on how to fulfill your requests using the enterprise-grade Suture framework tools.

## The Task
**Goal:** [Describe your overarching goal here, e.g., "Implement a new user authentication system."]

## Workflow Constraints
To ensure production-ready code and avoid hallucinations, you MUST follow these enterprise phases strictly. Use the Suture tools to transition between phases and verify your work.

### Phase 1: Plan
1. Use `start_loop` to initialize the workflow tracking with the overarching goal.
2. Formulate a detailed step-by-step plan.
3. Use the `verify_plan` tool to check your markdown plan against enterprise constraints.
4. Use `set_workflow_phase` to record that you have entered the "Plan" phase.
5. Use `store_memory` to save the core facts of the system you are building to prevent hallucinations during long sessions.

### Phase 2: Work
1. Transition using `set_workflow_phase("Work")`.
2. Write code to satisfy the plan.
3. After completing a significant portion of work, use `record_loop_iteration` to document your progress, including what was successful and what errors were encountered.
4. If you get stuck, use `retrieve_memory` to recall your original facts and intent.

### Phase 3: Test
1. Transition using `set_workflow_phase("Test")`.
2. Write unit tests for your newly written code.
3. Use the `lint` tool to automatically run `black` and `flake8` checks on your code. You must fix all linting errors.
4. Use the `safety_check` tool to verify no API keys or secrets have been leaked in your code or tests.

### Phase 4: Git Commit
1. Transition using `set_workflow_phase("Git Commit")`.
2. Stage and commit your changes with a descriptive commit message that references the loop goal.
3. Finally, use `finish_loop` to record the completion of the automated loop.

---

**AI Agent Instructions:** Please read the rules above. Once you understand them, begin executing Phase 1 using the provided Suture MCP tools.