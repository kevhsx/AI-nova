# Software engineering extension — 9 November 2026

The existing Nova AI application was extended with a pytest suite, a Docker image definition and GitHub Actions. The application runtime logic was left unchanged.

## Evidence

- `tests/test_api.py`: 16 collected test cases covering session revocation, duplicate and invalid registrations, password checks, role boundaries, authenticated feature calls, logged provider failures and upload validation.
- `tests/conftest.py`: isolated temporary databases and mocked provider responses, with local dotenv loading disabled.
- `requirements.txt` and `requirements-dev.txt`: pinned direct dependency versions; transitive dependencies are not fully locked.
- `Dockerfile` and `.dockerignore`: Python 3.12, explicit application files, a non-root process, persistent database location and a health check.
- `.github/workflows/ci.yml`: independent test and Docker smoke-test jobs on pushes and pull requests; JUnit results are retained as an artifact.

Local pytest result: **16 passed**, with two warnings about the application's existing deprecated startup event API. Local Docker execution was unavailable because the Docker daemon was not running. The remote Actions result must be checked separately.

## Authorship and assessment use

Codex wrote and executed this extension at the project owner's request. These files and the Git history demonstrate an AI-assisted engineering change. They do not by themselves establish the student's independent mastery, personal study hours, or work completed before this date. For an individual learning report, the student should run the workflow, review the assertions, explain a failure case and document what they personally learned. The original developer contribution and the historical tester's contribution remain separate.

Live LLM response quality, successful PDF text extraction, browser interactions, RAG and AWS deployment are outside these checks.
