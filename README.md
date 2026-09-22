# ParaBank AI Automation

## API testing from OpenAPI

The repository uses `config/openapi.yaml` as the documented ParaBank API
contract. It contains the `/parabank/services/bank` server and 27 operations.
The application merges those operations into discovery data before generating
API test cases and Playwright `APIRequestContext` scripts.

To generate and run API tests, choose API testing mode when starting the app:

```powershell
python app.py
```

The contract path can be overridden with `OPENAPI_SPEC_FILE` when using a
different OpenAPI document.
# AI Test Automation Generator

A developer-style GenAI QA framework that:

1. Accepts a website URL.
2. Discovers UI elements and same-origin XHR/fetch API traffic with Playwright.
3. Loads a reusable YAML testing specification.
4. Sends the specification + discovery information to Gemini.
5. Lets the user choose UI functional testing, API testing, or both.
6. Generates selected-layer test cases with synthetic test data.
7. Saves test cases to `data/test_cases.json` and extracted data to `data/test_data.json`.
8. Lets the user review and provide feedback.
9. Revises the test cases through Gemini.
10. Generates only the selected Playwright pytest script(s).
11. Performs basic AST-based validation of generated scripts.
12. Executes only the selected generated tests automatically.
13. Produces a self-contained pytest HTML report.

## Project structure

```text
ai_test_automation/
├── app.py
├── config/
│   ├── settings.py
│   └── test_specification.yaml
├── models/
│   └── test_models.py
├── services/
│   ├── gemini_service.py
│   ├── specification_loader.py
│   ├── website_analyzer.py
│   ├── test_case_service.py
│   ├── script_generator.py
│   └── test_runner.py
├── prompts/
│   ├── test_case_prompt.txt
│   ├── test_case_feedback_prompt.txt
│   └── test_script_prompt.txt
├── data/
│   ├── test_cases.json
│   ├── test_data.json
│   └── website_discovery.json
├── generated/
├── reports/
├── logs/
├── requirements.txt
├── pytest.ini
├── .env.example
└── .gitignore
```

## Setup

Create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Install Chromium:

```powershell
playwright install chromium
```

Create `.env` from `.env.example` and set:

```text
GEMINI_API_KEY=your_key
```

## Run

```powershell
python app.py
```

Enter the target website URL and choose UI, API, or both.

The application will:

- inspect the starting page and same-origin linked pages,
- capture same-origin XHR/fetch traffic,
- generate test cases for the selected layer(s),
- pause for human review,
- accept feedback and regenerate,
- generate the selected Playwright script(s),
- validate the generated Python AST,
- execute the selected script(s),
- create `reports/report.html`.

Discovery is automatic by default. Set `DISCOVERY_ENGINE=auto` to try the
configured Playwright MCP server first and fall back to Python Playwright if
the MCP SDK, command, server package, or required browser tools are unavailable.
Use `DISCOVERY_ENGINE=python` to force the fallback, or
`DISCOVERY_ENGINE=mcp` to fail instead of falling back when MCP is required.

Optional MCP settings are read from `.env`:

```text
DISCOVERY_ENGINE=auto
MCP_SERVER_COMMAND=npx
MCP_SERVER_PACKAGE=@playwright/mcp@latest
```

## API testing

API tests use Playwright's `APIRequestContext`, not the `requests` package.

The analyzer discovers XHR/fetch requests made while navigating the application. This is intentionally conservative: it does not invent API endpoints.

For a website whose APIs require authentication or are not exercised by the UI during discovery, add documented endpoint information to the discovery/specification layer before asking Gemini to generate API tests.

During UI discovery, the application records observed role, accessible name,
visible text, id, `data-testid`, `name`, and placeholder values as
`locator_candidates`. The script prompt requires generated UI tests to use
these candidates instead of guessing selectors.

## Playwright MCP

The workspace `.vscode/mcp.json` configures `@playwright/mcp@latest` for VS
Code browser exploration and locator inspection. The Python flow can also
start that server through the MCP SDK when `DISCOVERY_ENGINE=auto` or `mcp`.
The selected engine is recorded in `data/website_discovery.json`.

## Important limitation

The generated-code AST validator is a basic safety guard, not a security sandbox. Generated code should be treated as untrusted code. For production use, execute generated tests in an isolated environment/container with restricted network and filesystem access.

## Test specification

Edit:

```text
config/test_specification.yaml
```

to control the testing scope. It includes UI and API testing categories, modules, test-data rules, and automation settings.
