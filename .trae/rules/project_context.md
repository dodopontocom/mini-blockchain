<!-- gerado por repo_architect.sh em 2026-04-25 18:52 -->
# Project Context

## Overview
This project is a blockchain simulation application that allows users to interact with a simulated blockchain environment. It provides functionalities for managing transactions, retrieving blockchain data, and simulating reward transactions, aimed at educational and experimental purposes.

## Architecture
The application is built using Python, leveraging a simple MVC (Model-View-Controller) architecture. Key design decisions include the separation of concerns between the API logic (`api.py`), blockchain management (`blockc.py`), and user interface templates. The project utilizes Flask for web serving and ECDSA for cryptographic functions.

## Structure
- `api.py`: Contains the main API logic for handling requests and responses.
- `blockc.py`: Manages blockchain operations, including transaction handling and data retrieval.
- `simulations.py`: Implements simulation logic for blockchain interactions.
- `static/style.css`: Contains styles for the web interface.
- `templates/`: Directory for HTML templates.
  - `base.html`: Base template for the application.
  - `carteira.html`: Template for displaying wallet information.
  - `erro.html`: Template for error handling.
- `.gitignore`: Specifies files and directories to be ignored by Git.
- `requirements.txt`: Lists external dependencies required for the project.
- `.trae/rules/caveman.md`: Documentation or rules related to project conventions.

## Entry Points
The main entry point is `api.py`, which starts the Flask application and handles incoming web requests. The application serves the HTML templates and processes blockchain-related operations through the defined API endpoints.

## Infrastructure & DevOps
The project does not currently specify any containerization or cloud infrastructure. CI/CD practices are not evident from the provided context. Future enhancements may include integrating Docker for containerization and setting up CI/CD pipelines for automated testing and deployment.

## Dependencies
- `ecdsa`: Essential for implementing cryptographic functions related to blockchain transactions.
- `filelock`: Used for managing file access in a concurrent environment, ensuring data integrity during blockchain operations.

## For AI Assistants
AI should adhere to the MVC pattern when making changes, ensuring that business logic remains in `blockc.py`, API handling in `api.py`, and UI elements in the `templates/` directory. Maintain consistency in naming conventions and code style, particularly with the use of double quotes as indicated in the commit history.
