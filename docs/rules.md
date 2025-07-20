# LLM Coding Rules for Large Projects

## General Principles

- Prioritize **readability**, **modularity**, and **maintainability** in all code.
- Ensure all code is **well-documented** and follows project conventions.
- Only introduce code changes justified by a clear project requirement or bug fix.
- **Never include secrets or credentials** in code, config, or comments.

## Structure & Organization

### Directory Structure
- Always follow the prescribed project file structure.
- Place new modules, assets, or scripts in their correct directories.
- Do not duplicate logic or files across the project.

### Modularity
- Design each module and component with a **single, well-defined responsibility**.
- Use clear, consistent, and descriptive names for all files, variables, functions, and classes.

## Coding Style and Standards

- Follow the language’s official style guide (e.g., **PEP8 for Python**).
- Use **docstrings** for modules, classes, and functions.
- Add inline comments only where necessary to clarify complex sections.
- Employ **type annotations** where supported by the language.
- Functions should generally be **shorter than 40 lines**.

## Error Handling

- Proactively handle all reasonable error conditions.
- Log all errors with **detailed messages** that aid in troubleshooting.
- On encountering errors, update system states (such as MongoDB document status) accordingly.
- Propagate unhandled errors upward to be managed at an appropriate layer.

## Dependencies

- Use only dependencies already listed in the project requirements or explicitly approved by project maintainers.
- If new dependencies are necessary, update `requirements.txt` or the appropriate manager and document the change.

## External APIs & Services

- Validate input/output data with all APIs and third-party services.
- Apply exponential backoff and automatic retries for transient errors in external requests.
- Never hardcode or expose API keys, tokens, or service credentials in source code.

## Database Interactions

- Interact with the database only through project-approved abstractions.
- Validate data before any insert or update.
- Write and test migration scripts for schema changes.

## Testing

- Write thorough unit and integration tests for new or modified business logic.
- Use designated testing frameworks per project guidelines.
- Ensure all tests pass before merging branches.
- Add regression tests for bug fixes.
- Always use test data—**never production data**—in tests.

### Test Generation Rules

- **Test Code Belongs in Test Files**: Never place test functions or test logic in production code files. All test helpers and test cases should reside in the `tests/` directory, mirroring the app structure if possible.
- **Naming Conventions**: Test functions must start with `test_` so pytest can discover them. Helper functions in test files should **not** start with `test_` to avoid pytest treating them as tests.
- **Imports and Paths**: Always import from the app using absolute imports (e.g., `from app.database.mongo import mongo_client`). Ensure all relevant directories (`app/`, `tests/`, and their subdirectories) contain `__init__.py` for package recognition.
- **Test Isolation**: Each test should be independent and not rely on the state set by other tests. Use fixtures for setup/teardown if needed.
- **Environment and Configuration**: Ensure all required environment variables (like `MONGO_URI`) are set before running tests. Use test databases or mock services when possible to avoid affecting production data.
- **Error Handling and Debugging**: Print or log detailed error messages in test helpers to aid debugging. Assert meaningful conditions and provide clear failure messages.
- **Dependency Management**: All test dependencies (e.g., `pytest`) must be listed in `requirements.txt` or a separate test requirements file.
- **Test Discovery**: Run tests from the project root to ensure the app package is discoverable. Optionally, use a `pytest.ini` file to set the `pythonpath` for consistent test discovery.
- **Test Output**: Keep test output clean and readable; use print statements only for debugging, and remove them in final versions.
- **Documentation**: Add docstrings to all test functions explaining what they verify.

## Documentation

- Update Markdown documentation (`/docs/` etc.) to reflect significant code or design changes.
- Keep API and data model documentation current.
- Record all migrations and breaking changes in `CHANGELOG.md`.
- Use tables, lists, and clear headings for clarity.

## Collaboration and Review

- Use topic/feature branches or forks—**never commit directly to main/master**.
- Submit clear, descriptive Pull Requests, referencing related issues or tasks as needed.
- Engage in code reviews; offer and address constructive feedback.
- Resolve all review comments before merge.

## Security

- Sanitize all user input/output.
- Use encryption and secure practices for sensitive data operations.
- Remove unnecessary debug logs and sensitive prints before committing.
- Follow the principle of least privilege regarding permissions.

## Release & Deployment

- Ensure all deployments are gated by passing automated tests and checks.
- Never deploy untested or unreviewed code to production.
- Roll back and notify if production deployment causes critical failures.
- Document operation and deployment procedures.

---

Follow these guidelines to ensure all code in large projects is robust, maintainable, and secure, and to help both LLM and human collaborators work more efficiently together.
