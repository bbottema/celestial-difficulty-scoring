# Rapid Prototype Workflow

This guide provides a quick overview of the rapid prototype workflow, designed for getting your database up and running quickly, without making use of Alembic historical migrations.

The steps to follow to get this workflow up and running are as follows:

1. **Synchronize your Python environment:** You can do this by running the command `pipenv synq`. This step ensures all necessary Python dependencies are properly installed in your Python environment.

    ```
    pipenv synq
    ``` 

2. **Initialize your database schema:** After synchronizing your environment, run `python initialize_db_schema.py`. Be aware that this command will update the structure of your tables and also drop all existing data whenever it is run.

    ```
    pipenv run python initialize_db_schema.py
    ```
