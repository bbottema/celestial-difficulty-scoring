# Rapid Prototype Workflow

This guide provides a quick overview of the rapid prototype workflow, designed for getting your database up and running quickly, without making use of Alembic historical migrations.

The steps to follow to get this workflow up and running are as follows:

1. **Create a new Python environment:** Start by creating a new Python environment and installing the necessary dependencies. You can do this by running the following commands.

    ```
    pipenv sync
    ```
   
Alternatively, use ```pipenv install``` to install the dependencies from the Pipfile with latest versions.

2. **Initialize your database schema:** After synchronizing your environment, run `python initialize_db_schema.py`. Be aware that this command will update the structure of your tables and also drop all existing data whenever it is run.

    ```
    pipenv run python initialize_db_schema.py
    ```
