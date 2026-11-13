# ECSE 429 — Software Validation | Fall 2026 — Group 7

This repository contains **Group 7's course project for ECSE 429 (Software Validation) at McGill University**. We test the **Todo Manager REST API** (v1.5.5), which manages Todos, Projects, Categories, and the relationships between them.

The repository focuses on **API validation**, not on implementing the Todo Manager service itself. It contains exploratory testing material, automated API tests, bug-investigation records, and behavior-driven acceptance tests.

## Project work

### Part A — API and exploratory testing

- Explored the Todo Manager API across **Todos, Projects, Categories, and Interoperability**.
- Developed automated Python/pytest tests for REST endpoints, including successful requests, error handling, and entity relationships.
- Recorded exploratory-testing notes and bug investigations.

Relevant locations: [`tests/`](tests/), [`exploratory/`](exploratory/), [`docs/session-notes/`](docs/session-notes/), and [`docs/bugs/`](docs/bugs/).

### Part B — Behavior-driven acceptance testing

Implemented **20 user stories**, organized into four areas, using **Gherkin feature files** and **Python step definitions with pytest-bdd**. The story scenarios cover normal, alternate, and error flows.

| Area | Stories | Test executions |
| --- | --- | ---: |
| Todos | T01–T05 | 28 |
| Projects | P01–P05 | 30 |
| Categories | C01–C05 | 15 |
| Interoperability | I01–I05 | 30 |
| **Total** | **20 stories** | **103** |

Interoperability scenarios exercise linking Todos to Projects and Categories, viewing related entities, and unlinking a Todo from a Project without deleting either entity.

**Latest reported local verification:** All **103 Part B test executions passed** in normal and reverse order. These results were reported after completing the stories; they should be rechecked on the current `main` branch before final submission. The repository also contains saved text logs under [`part_b/docs/test-results/`](part_b/docs/test-results/).

Part B test setup creates temporary entities and cleans them up after each scenario to help keep tests independent of execution order.

## Repository structure

```text
.
├── tests/                         # Part A automated API tests
├── exploratory/                   # Exploratory testing material by API area
├── docs/
│   ├── bugs/                      # Bug investigation and reporting material
│   └── session-notes/             # Exploratory testing notes
├── part_b/
│   ├── features/
│   │   ├── todos/                 # T01–T05 Gherkin scenarios
│   │   ├── projects/              # P01–P05 Gherkin scenarios
│   │   ├── category/              # C01–C05 Gherkin scenarios
│   │   └── interoperability/      # I01–I05 Gherkin scenarios
│   ├── step_definitions/          # Python pytest-bdd step implementations
│   ├── support/                   # Part B supporting code
│   └── docs/
│       ├── test-results/          # Saved pytest output
│       └── deliverables/          # Submission-related material
├── requirements.txt
└── run_random_tests.py           # Part A randomized-order test runner
```

## Getting started

### Prerequisites

- **Python 3.10+** and a terminal
- **Java** to run the provided Todo Manager REST API JAR
- The course-provided `runTodoManagerRestAPI-1.5.5.jar` (the application is not included in this repository)

Start the API in a separate terminal (adjust the JAR path to your machine):

```powershell
java -jar path/to/runTodoManagerRestAPI-1.5.5.jar
```

The tests expect the service at **http://localhost:4567** by default. The Part B API base URL can be overridden using the `TODO_API_URL` environment variable.

### Install Python dependencies

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install pytest-bdd pytest-reverse
```

The extra packages are required for the Part B Gherkin steps and the `--reverse` option; they are not currently listed in the root `requirements.txt`.

### Run Part A API tests

```powershell
python -m pytest tests/ -v
```

To run the Part A suite in a reproducible random order:

```powershell
python run_random_tests.py --seed 429
```

### Run Part B acceptance tests

Run the entire 103-execution suite in normal order:

```powershell
python -m pytest part_b/step_definitions -v
```

Run the same tests in reverse order:

```powershell
python -m pytest part_b/step_definitions -v --reverse
```

Run a specific Part B area (for example, Interoperability):

```powershell
python -m pytest part_b/step_definitions/test_interoperability_steps.py -v
```

Run these commands **while the Todo Manager API is running**. The tests are integration/acceptance tests against a live local REST service, not mocks.

## Current status and remaining work

- **Implemented:** Part A automated API testing and exploratory work; Part B Gherkin stories, step definitions, relationship testing, and test cleanup.
- **Verified locally:** 103 Part B executions reported passing in both normal and reverse order.
- **Before submission:** Re-run the merged `main` test suite, finalize and review bug reports, prepare the required demonstration video showing different execution orders, complete the final written report, and check the submission package.

### Notable investigation

During Part B I03 testing, requesting `GET /projects/abc/tasks` and `GET /projects/missing/tasks` returned HTTP 200 with a Todo collection instead of the expected missing-project error. This was recorded as a **potential API bug** that should be checked against the API contract before being labeled a confirmed defect.

## Course and team

**ECSE 429 — Software Validation, Fall 2026**  
**McGill University — Group 7**

This repository is maintained for the course project and academic testing purposes.
