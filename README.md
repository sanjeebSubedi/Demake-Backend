# Twitter Demake - Backend

This repository contains the backend code for the Twitter Demake project, developed as part of **CSC 532 - Advanced Topics in Software Engineering**.

## Project Overview

The **Twitter Demake** project is a simplified version of Twitter that focuses on core features such as user management and tweeting. It is implemented using **Python** and **FastAPI** for the backend, and **PostgreSQL** as the database.

## Current Status (Sprint 1 - October 10)

As of Sprint 1, the following backend features have been completed:

- User Registration
- User Login
- Tweet Creation
- Tweet Viewing

The project follows the Scrum methodology and will be updated progressively over future sprints.

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Dependency Management**: Poetry
- **Containerization**: Docker, Docker Compose
- **API Documentation**: Automatically generated and available at `localhost:8000/docs` once the server is running.

## Installation Instructions

### Prerequisites

1. **Python** (>= 3.10)
2. **Docker** and **Docker Compose**
3. **Poetry** for managing dependencies

### Step 1: Clone the repository

```bash
git clone https://github.com/your-username/twitter-demake-backend.git
cd twitter-demake-backend
```

### Step 2: Set up environment variables

Create a .env file in the root directory of the project with the necessary environment variables for the application to run.
Ensure that your .env file contains all necessary variables..

### Step 3: Using Docker (Recommended)

You can run the application and its dependencies using Docker and Docker Compose.

Build and run the application:

```bash
docker-compose up
```

The FastAPI server will be accessible at http://localhost:8000 and the API documentation can be accessed at http://localhost:8000/docs.

### Step 4: Manual Setup (Without Docker)

If you prefer not to use Docker, follow these steps:

Install the project dependencies using Poetry:

```bash
poetry install
```

Activate the virtual environment:

```
poetry shell
```

Run the FastAPI server using Uvicorn:

```bash
uvicorn src.main:app --reload
```

The application will be running at http://localhost:8000.

The project includes unit tests for key features such as user login and registration. To run the tests:

```bash
pytest -s
```

## Course Information

This project is part of the CSC 532 - Advanced Topics in Software Engineering course at Louisiana Tech University. The backend is being developed in multiple sprints using the Scrum methodology.
