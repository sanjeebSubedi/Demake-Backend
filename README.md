# Twitter Demake - Backend

This repository contains the backend code for the **Twitter Demake** project, developed as part of **CSC 532 - Advanced Topics in Software Engineering**.

## Project Overview

The **Twitter Demake** is a streamlined version of Twitter, concentrating on essential features such as user management, tweeting, and following functionality. It is implemented using **Python** and **FastAPI** for the backend, with **PostgreSQL** as the database.

## Current Status (Sprint 2 - October 29)

As of Sprint 2, the following backend features have been implemented:

- **User Authentication**: User registration and login.
- **Tweets**: Creating and viewing tweets.
- **Follow System**: Following and unfollowing users, retrieving follower and following lists, and providing follow suggestions.
- **User Management**: Profile updates and basic user info retrieval.

We are following the Scrum methodology, with periodic updates at the end of each sprint.

## Technology Stack

- **Backend Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Dependency Management**: Poetry
- **Containerization**: Docker, Docker Compose
- **API Documentation**: Automatically generated at `http://localhost:8000/docs`.

## Installation Instructions

### Prerequisites

Ensure the following are installed on your machine:

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
