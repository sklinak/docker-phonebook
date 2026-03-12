# docker-phonebook
Phonebook application using Docker, PostgreSQL and Python.  Supports adding, updating, deleting and viewing contacts via a terminal interface. Database can be inspected using pgAdmin.
# Docker Phonebook

This project implements a simple phonebook application using Docker, PostgreSQL and Python.  
The application stores contacts in a PostgreSQL database and allows users to interact with the data through a terminal interface.  
The database can also be managed and inspected using pgAdmin.

## Project Structure

The project consists of several components:

- **docker-compose.yml**  
  Defines and runs three services:
  - PostgreSQL database
  - Python phonebook application
  - pgAdmin for database management

- **Dockerfile**  
  Builds the Python application container based on `python:3.11-slim`.  
  It installs required dependencies and runs the main application file.

- **requirements.txt**  
  Contains Python dependencies needed for the project (for example `psycopg2-binary` for PostgreSQL connection).

- **initialization.sql**  
  SQL script used to create the `contacts` table in the PostgreSQL database.

- **phonebook.py**  
  Main Python program that connects to PostgreSQL and provides functionality for managing contacts.

## Database

The PostgreSQL database stores contacts in the table `contacts`.

Table structure:

- `id` – unique contact identifier (primary key)
- `full_name` – contact full name
- `phone` – phone number
- `note` – additional information about the contact

Input validation is implemented both in the database and in the Python application.

Examples of validation rules:
- names must not contain digits
- phone numbers must contain exactly 11 digits and may start with `+`

## Application Features

The Python application provides a terminal-based interactive menu with the following options:

1. Show all contacts  
2. Add a new contact  
3. Update an existing contact  
4. Delete a contact  
5. Exit the program

The program connects to PostgreSQL using the `psycopg2` library and performs standard CRUD operations:
- Create
- Read
- Update
- Delete

## Running the Project

1. Make sure Docker and Docker Compose are installed.

2. Run the following command in the project directory:

```bash
docker-compose up --build
