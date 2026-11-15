# Part B: Story Tests

Behavior-driven acceptance tests for the Todo Manager REST API (v1.5.5), written as Gherkin feature files and run with pytest-bdd.

## Contents

| Folder | What is in it |
| --- | --- |
| `features/` | 20 Gherkin feature files, 5 per area: `todos/` (T01-T05), `projects/` (P01-P05), `category/` (C01-C05), `interoperability/` (I01-I05) |
| `step_definitions/` | pytest-bdd step implementations, one file per area |
| `docs/test-results/` | Saved pytest output (normal and reverse order) |
| `docs/bugs/` | Bug reports found during Part B |

Each feature has a Background and three Scenario Outlines: normal flow, alternate flow and error flow. The 20 features run as 103 test executions.

## Run

Start the API first (`java -jar runTodoManagerRestAPI-1.5.5.jar`, default http://localhost:4567; override with `TODO_API_URL`). From the repository root:

```powershell
python -m pytest part_b/step_definitions -v             # normal order
python -m pytest part_b/step_definitions -v --reverse   # reverse order
```

Every test fails (does not skip) when the service is not running, and each scenario restores the data it changed.
