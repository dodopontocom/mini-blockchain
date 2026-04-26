<!-- gerado por repo_architect.sh em 2026-04-25 18:52 -->
# Project Context

## Overview
This project is a blockchain simulation application that allows users to interact with a simulated blockchain environment. It provides functionalities for managing transactions, retrieving blockchain data, and simulating reward transactions, aimed at educational and experimental purposes.

## Architecture
The application is built using Python, leveraging a simple MVC (Model-View-Controller) architecture. Key design decisions include the separation of concerns between the API logic (`api.py`), blockchain management (`blockc.py`), and user interface templates. The project utilizes Flask for web serving and ECDSA for cryptographic functions.

## Structure
- `src/`: Core application logic.
  - `api.py`: Main API logic for handling requests and responses.
  - `blockc.py`: Blockchain management operations.
  - `simulations.py`: Simulation logic for blockchain interactions.
  - `static/`: Frontend assets (CSS, etc.).
  - `templates/`: HTML templates for the UI.
- `infra/`: Infrastructure and deployment configuration.
  - `Dockerfile`: Container definition.
  - `scripts/`: Operational scripts (`run.sh`, `entrypoint.sh`, etc.).
- `.gitignore`: Specifies files and directories to be ignored by Git.
- `requirements.txt`: Lists external dependencies.

## Entry Points
The main entry point is `src/api.py`, started via `infra/scripts/run.sh`.

## Infrastructure & DevOps
The project uses Docker for containerization and GitHub Actions for CI/CD, including performance tests and automated image builds.

## Dependencies
- `ecdsa`: Essential for implementing cryptographic functions related to blockchain transactions.
- `filelock`: Used for managing file access in a concurrent environment, ensuring data integrity during blockchain operations.

## For AI Assistants
AI should adhere to the MVC pattern:
- Business logic in `src/blockc.py`.
- API handling in `src/api.py`.
- UI elements in `src/templates/`.
- Scripts in `infra/scripts/`.
