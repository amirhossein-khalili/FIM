FIM PROJECT

Django Project with Accounts, Files, and Notifications
This project is a Django application consisting of three main apps:

accounts: For user identity verification
files: For managing files
notifications: For sending notifications

Installation
Prerequisites

Docker installed on your system
make command available (typically installed on Unix-like systems)

Steps

Clone the repository:
git clone <repository_url>
cd <project_directory>

Dockerize the application:
Run the following command to build and start the Docker containers:
./dockerize.sh

Set up the database:
After launching the containers, use the Makefile to create the database:
make createdb

Apply migrations:
Enter the Docker container's shell:
docker exec -it <container_name> /bin/bash

You can find the container name by running docker ps.
Once inside the container, run:
python manage.py migrate

Create a superuser (optional):
To access the Django admin panel, create a superuser account:
python manage.py createsuperuser

Follow the prompts to set up your superuser credentials.

Note: The Makefile is designed for easier access and development. Check it for additional commands (e.g., make migrate or make shell) that might simplify these steps.
Usage

Start the application:
If the containers are not already running, start them with:
docker-compose up

Access the application:
The Django application should be accessible at http://localhost:8000 (adjust the port if necessary based on your Docker configuration).

Access the admin panel:
Visit http://localhost:8000/admin/ and log in with your superuser credentials.

Test the APIs:
Postman collections are provided in the docs directory. Import these into Postman to test the API endpoints.
